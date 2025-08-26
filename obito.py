import cv2
from fer import FER


detector = FER()


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

   
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    
    
    emotions = detector.detect_emotions(small_frame)

    for face in emotions:
        
        x, y, w, h = [int(coord*2) for coord in face["box"]] 

        
        face_frame = frame[max(y,0):min(y+h, frame.shape[0]),
                           max(x,0):min(x+w, frame.shape[1])]
        
        dominant_emotion, score = detector.top_emotion(face_frame)
        
        if dominant_emotion is not None:
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            cv2.putText(frame, f"{dominant_emotion} ({int(score*100)}%)", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    
    cv2.imshow("Real-time Emotion Detection", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
