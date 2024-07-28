import cv2
import numpy as np
import time
import HandTrackingModule
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

width_cam, height_cam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

previous_time = 0

detector = HandTrackingModule.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volume_BAR = 400
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        lm_4 = next((lm for lm in lmList if lm[0] == 4), None)
        lm_8 = next((lm for lm in lmList if lm[0] == 8), None)
        x1, y1 = lm_4[1], lm_4[2]
        x2, y2 = lm_8[1], lm_8[2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(img, (int(x1), int(y1)), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (int(x2), int(y2)), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 255), 3)
        center = cv2.circle(img, (int(cx), int(cy)), 10, (255, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [30, 150], [minVol, maxVol])
        volume_BAR = np.interp(length, [30, 150], [400, 150])
        volPer = np.interp(length, [30, 150], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 30:
            center = cv2.circle(img, (int(cx), int(cy)), 10, (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (50, 140), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volume_BAR)), (85, 400), (255, 0, 0), cv2.FILLED)
    current_time = time.time()
    fps = 1 / (current_time - previous_time)

    previous_time = current_time
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
