import cv2
import numpy as np
import mediapipe as mp
import time
import os
from sklearn.linear_model import LinearRegression


mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.75)
mpDraw = mp.solutions.drawing_utils


canvas = None
brushColor = (0, 0, 255)   
brushThickness = 7
eraserThickness = 50


colors = {'Red': (0, 0, 255), 'Green': (0, 255, 0), 'Blue': (255, 0, 0), 'Yellow': (0, 255, 255)}
colorKeys = list(colors.keys())


points = []  


def find_finger_positions(hand_landmarks, img):
    lmList = []
    h, w, c = img.shape
    if hand_landmarks:
        for id, lm in enumerate(hand_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append((id, cx, cy))
    return lmList

def fingers_up(lmList):
    fingers = []
    if lmList[4][1] < lmList[3][1]:  
        fingers.append(1)
    else:
        fingers.append(0)
    tipsIds = [8, 12, 16, 20]
    for id in tipsIds:
        if lmList[id][2] < lmList[id - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def recognize_shape(points):
    if len(points) < 5:
        return None
    pts = np.array(points)
    x = pts[:,0].reshape(-1,1)
    y = pts[:,1]
    
    
    model = LinearRegression().fit(x, y)
    y_pred = model.predict(x)
    error = np.mean(np.abs(y - y_pred))
    if error < 5:
        return ('line', (pts[0], pts[-1]))
    
    
    (x_center, y_center), radius = cv2.minEnclosingCircle(pts)
    mean_dist = np.mean(np.sqrt((pts[:,0]-x_center)**2 + (pts[:,1]-y_center)**2))
    if abs(mean_dist - radius) < 10:
        return ('circle', (int(x_center), int(y_center), int(radius)))
    
    
    x, y, w, h = cv2.boundingRect(pts)
    aspect = w/h
    if 0.8 < aspect < 1.2:
        return ('rectangle', (x, y, w, h))
    
    return None


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

xp, yp = 0, 0
mode = 'Draw'

while True:
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.flip(img, 1)
    
    if canvas is None:
        canvas = np.zeros_like(img)
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        lmList = find_finger_positions(handLms, img)
        
        if lmList:
            fingers = fingers_up(lmList)
            
            
            if fingers[1] and fingers[2]:
                xp, yp = 0, 0
                mode = 'Select'
                for i, key in enumerate(colorKeys):
                    if lmList[8][1] > 50 + i*100 and lmList[8][1] < 150 + i*100:
                        brushColor = colors[key]
                        mode = 'Draw'
            
           
            if fingers[1] and not fingers[2]:
                mode = 'Draw'
                cx, cy = lmList[8][1], lmList[8][2]
                points.append((cx, cy))
                if xp == 0 and yp == 0:
                    xp, yp = cx, cy
                if brushColor == (0, 0, 0):  
                    cv2.line(img, (xp, yp), (cx, cy), (0, 0, 0), eraserThickness)
                    cv2.line(canvas, (xp, yp), (cx, cy), (0, 0, 0), eraserThickness)
                else:
                    cv2.line(img, (xp, yp), (cx, cy), brushColor, brushThickness)
                    cv2.line(canvas, (xp, yp), (cx, cy), brushColor, brushThickness)
                xp, yp = cx, cy
            
            
            if fingers[0] and fingers[1]:
                brushColor = (0, 0, 0)
    
    
    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, canvas)
    
    
    for i, key in enumerate(colorKeys):
        cv2.rectangle(img, (50 + i*100, 10), (150 + i*100, 110), colors[key], -1)
        cv2.putText(img, key, (60 + i*100, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    
    cv2.putText(img, f"Mode: {mode}", (1000, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
    
    cv2.imshow("Smart Air Whiteboard - Pro+", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros_like(img)  
        points = []
    elif key == ord('s'):
        if not os.path.exists("Drawings"):
            os.makedirs("Drawings")
        cv2.imwrite(f"Drawings/Drawing_{int(time.time())}.png", canvas)
        print("Drawing Saved!")
    
    
    if len(points) > 10 and (not fingers[1] or fingers[2]):
        shape = recognize_shape(points)
        if shape:
            if shape[0] == 'line':
                cv2.line(canvas, shape[1][0], shape[1][1], brushColor, brushThickness)
            elif shape[0] == 'circle':
                cv2.circle(canvas, (shape[1][0], shape[1][1]), shape[1][2], brushColor, brushThickness)
            elif shape[0] == 'rectangle':
                x, y, w, h = shape[1]
                cv2.rectangle(canvas, (x, y), (x+w, y+h), brushColor, brushThickness)
        points = []  

cap.release()
cv2.destroyAllWindows()
