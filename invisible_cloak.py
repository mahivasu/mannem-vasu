
import cv2
import numpy as np
import time

def get_clean_background(cap, num_frames=80, delay=0.03):
    """
    Capture clean background by removing any moving objects (like your body).
    """
    print("[INFO] Capturing clean background... Please step out!")

    frames = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        frames.append(frame)
        time.sleep(delay)

    frames = np.array(frames, dtype=np.uint8)

    
    median_bg = np.median(frames, axis=0).astype(np.uint8)

    print("[INFO] Clean background ready.")
    return median_bg


def main():
    cap = cv2.VideoCapture(0)
    time.sleep(1)

    
    background = get_clean_background(cap)
    background = cv2.GaussianBlur(background, (5,5), 0)

    kernel = np.ones((3,3), np.uint8)

    print("[INFO] Cloak ready! Show your cloth.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        
        lower1 = np.array([0, 120, 50])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 50])
        upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = mask1 + mask2

       
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

        mask_inv = cv2.bitwise_not(mask)

        bg_part = cv2.bitwise_and(background, background, mask=mask)
        fg_part = cv2.bitwise_and(frame, frame, mask=mask_inv)

        final = cv2.add(bg_part, fg_part)

        cv2.imshow("Invisible Cloak", final)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            print("[INFO] Re-capturing background...")
            background = get_clean_background(cap)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
