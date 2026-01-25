import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.HandTrackingModule import HandDetector
import threading
import time

import pyautogui

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Initialize FPS reader
from cvzone.FPS import FPS
fpsReader = FPS(avgCount=30)

# Face and Hand Detectors
detector1 = FaceMeshDetector(maxFaces=1)
detector2 = HandDetector(maxHands=2, detectionCon=0.85)

# Control and gesture variables
go_right = go_left = go_up = go_down = 0
ges_ctrl_track = 0
gesture_on = None
misle_coldwn = flare_coldwn = booster_coldwn = fire_on = 0

def ges_enable():
    """ Enable gesture control after 3 seconds """
    global gesture_on
    time.sleep(3)
    gesture_on = 1
    print("Gesture Control On")

def cooldown_function(func_name, cooldown_time):
    """ General cooldown function to prevent rapid triggers """
    global misle_coldwn, flare_coldwn, booster_coldwn
    time.sleep(cooldown_time)
    if func_name == 'missile':
        misle_coldwn = 0
        print("Missile reloaded")
    elif func_name == 'flare':
        flare_coldwn = 0
        print("Flares reloaded")
    elif func_name == 'booster':
        booster_coldwn = 0
        print("Boosters cooled down")

# Start gesture enable thread
gesture_on_thread = threading.Thread(target=ges_enable)

while True:
    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        img, faces = detector1.findFaceMesh(img, draw=False)

        if faces:
            # Capture facial control points
            ctrl_x, ctrl_y = faces[0][168][0], faces[0][168][1]
            left_x, left_y = faces[0][57][0] + 10, faces[0][57][1]
            right_x, right_y = faces[0][287][0] - 10, faces[0][287][1]

            # Display control points
            cv2.circle(img, (ctrl_x, ctrl_y), 5, (255, 255, 0), 2)
            cv2.circle(img, (left_x, left_y), 5, (255, 255, 0), 2)
            cv2.circle(img, (right_x, right_y), 5, (255, 255, 0), 2)
            cv2.line(img, (ctrl_x, 0), (ctrl_x, 1000), (255, 255, 255), 2)
            cv2.line(img, (0, ctrl_y), (1000, ctrl_y), (255, 255, 255), 2)

            # Detect hands
            hands, img = detector2.findHands(img, draw=True, flipType=False)

            if len(hands) == 2:
                # Left and right hand distinction
                hands_l, hands_r = (hands[0], hands[1]) if hands[0]['type'] == "Left" else (hands[1], hands[0])

                lmlist_l, lmlist_r = hands_l['lmList'], hands_r['lmList']

                # Capture relevant finger positions
                r_idx_x, r_idx_y = lmlist_r[8][0], lmlist_r[8][1]
                l_idx_x, l_idx_y = lmlist_l[8][0], lmlist_l[8][1]
                r_thmb_x, r_thmb_y = lmlist_r[4][0], lmlist_r[4][1]
                l_thmb_x, l_thmb_y = lmlist_l[4][0], lmlist_l[4][1]

                # Display the finger positions
                cv2.circle(img, (r_idx_x, r_idx_y), 5, (0, 255, 255), 2)
                cv2.circle(img, (l_idx_x, l_idx_y), 5, (0, 255, 255), 2)
                cv2.circle(img, (r_thmb_x, r_thmb_y), 5, (0, 255, 255), 2)
                cv2.circle(img, (l_thmb_x, l_thmb_y), 5, (0, 255, 255), 2)

                # Check which fingers are up
                l_fing_upno = detector2.fingersUp(hands_l)
                r_fing_upno = detector2.fingersUp(hands_r)

                # Debug print to verify fingers are being detected correctly


                # Activate gesture control based on a specific hand gesture
                if (l_fing_upno == [1, 0, 0, 0, 1] and r_fing_upno == [1, 0, 0, 0, 1] and ges_ctrl_track == 0):
                    ges_ctrl_track = 1
                    print("Gesture Enabled")

                    if not gesture_on_thread.is_alive():
                        gesture_on_thread.start()

        # Aircraft control section (active once gesture is enabled)
        if gesture_on == 1:
            cv2.line(img, (0, ctrl_y), (1000, ctrl_y), (255, 0, 255), 2)

            # Aircraft Moving Up
            if ctrl_y < 200 and go_up == 0:
                pyautogui.keyDown('W')
                go_up = 1
                print("Going Up")
            elif ctrl_y > 250 and go_up == 1:
                pyautogui.keyUp('W')
                go_up = 0

            # Aircraft Moving Down
            if ctrl_y > 300 and go_down == 0:
                pyautogui.keyDown('S')
                go_down = 1
                print("Going Down")
            elif ctrl_y < 250 and go_down == 1:
                pyautogui.keyUp('S')
                go_down = 0

            # Aircraft Moving Right or Left
            if right_x < ctrl_x and go_right == 0:
                pyautogui.keyDown('D')
                go_right = 1
                print("Going Right")
            elif left_x > ctrl_x and go_left == 0:
                pyautogui.keyDown('A')
                go_left = 1
                print("Going Left")
            elif left_x < ctrl_x < right_x:
                if go_right == 1:
                    pyautogui.keyUp('D')
                    go_right = 0
                if go_left == 1:
                    pyautogui.keyUp('A')
                    go_left = 0

            # Missile Launch
            if abs(r_thmb_y - r_idx_y) < 30 and abs(l_thmb_y - l_idx_y) < 30 and misle_coldwn == 0:
                print("Missile Launched")
                pyautogui.press("Space")
                misle_coldwn = 1
                threading.Thread(target=cooldown_function, args=('missile', 2)).start()

            # Flares Deploying
            if abs(r_thmb_y - r_idx_y) > 30 and abs(l_thmb_y - l_idx_y) < 30 and flare_coldwn == 0:
                print("Flares Deployed")
                pyautogui.press("R")
                flare_coldwn = 1
                threading.Thread(target=cooldown_function, args=('flare', 2)).start()

            # Gun Fire
            if abs(r_thmb_y - r_idx_y) < 30 and abs(l_thmb_y - l_idx_y) > 30 and fire_on == 0:
                pyautogui.keyDown("left")
                fire_on = 1
                print("Gun Firing")
            if abs(r_thmb_y - r_idx_y) > 30 and fire_on == 1:
                pyautogui.keyUp("left")
                fire_on = 0
                print("Firing Stopped")

            # Booster Activation
            if abs(r_idx_x - l_idx_x) < 50 and booster_coldwn == 0:
                print("Booster Engaged")
                pyautogui.press("Shift")
                booster_coldwn = 1
                threading.Thread(target=cooldown_function, args=('booster', 3)).start()

        # Update and display FPS
        fps, img = fpsReader.update(img)
        cv2.putText(img, f'FPS: {int(fps)}', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow("Aircraft Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
