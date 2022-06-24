import time

from pynput.keyboard import Key, Controller

from handTracker import *
from keys import *


def getMousPos(event, x, y, flags, param):
    global clickedX, clickedY
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONUP:
        clickedX, clickedY = x, y
    if event == cv2.EVENT_MOUSEMOVE:
        mouseX, mouseY = x, y


def calculateIntDidtance(pt1, pt2):
    return int(((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2) ** 0.5)

def createLowerCase():
    # Creating keys
    global keys
    keys = []
    letters = list("QWERTYUIOPASDFGHJKLZXCVBNM")
    for i, l in enumerate(letters):
        if i < 10:
            keys.append(Key(startX + i * w + i * 5, startY, w, h, l))
        elif i < 19:
            keys.append(Key(startX + (i - 10) * w + i * 5, startY + h + 5, w, h, l))
        else:
            keys.append(Key(startX + (i - 19) * w + i * 5, startY + 2 * h + 10, w, h, l))

    keys.append(Key(startX + 25, startY + 3 * h + 15, 5 * w, h, "Space"))
    keys.append(Key(startX + 8 * w + 50, startY + 2 * h + 10, w, h, "Clear"))
    keys.append(Key(startX + 5 * w + 30, startY + 3 * h + 15, 5 * w, h, "Backspace"))

    return

def createUpperCase():
    # Creating keys
    global keys
    keys = []
    letters = list("qwertyuiopasdfghjklzxcvbnm")
    for i, l in enumerate(letters):
        if i < 10:
            keys.append(Key(startX + i * w + i * 5, startY, w, h, l))
        elif i < 19:
            keys.append(Key(startX + (i - 10) * w + i * 5, startY + h + 5, w, h, l))
        else:
            keys.append(Key(startX + (i - 19) * w + i * 5, startY + 2 * h + 10, w, h, l))

    keys.append(Key(startX + 25, startY + 3 * h + 15, 5 * w, h, "Space"))
    keys.append(Key(startX + 8 * w + 50, startY + 2 * h + 10, w, h, "Clear"))
    keys.append(Key(startX + 5 * w + 30, startY + 3 * h + 15, 5 * w, h, "Backspace"))

    return

w, h = 80, 60
startX, startY = 40, 100

toggleKeyboard = False

showKey = Key(350, 5, 60, 50, 'Show')
exitKey = Key(350, 65, 60, 50, 'Exit')
toggleKey = Key(350, 125, 60, 50, 'Toggle')
textBox = Key(startX, startY - h - 5, 10 * w + 9 * 5, h, '')
cap = cv2.VideoCapture(0)
ptime = 0

# initiating the hand tracker
tracker = HandTracker(detectionCon=1)

# getting frame's height and width
frameHeight, frameWidth, _ = cap.read()[1].shape
showKey.x = int(frameWidth * 1.5) - 85
exitKey.x = int(frameWidth * 1.5) - 85
toggleKey.x = int(frameWidth * 1.5) - 85

clickedX, clickedY = 0, 0
mousX, mousY = 0, 0

show = False
cv2.namedWindow('video')
counter = 0
previousClick = 0

keyboard = Controller()
while True:
    if counter > 0:
        counter -= 1

    signTipX = 0
    signTipY = 0

    thumbTipX = 0
    thumbTipY = 0

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (int(frameWidth * 1.5), int(frameHeight * 1.5)))
    frame = cv2.flip(frame, 1)
    # find hands
    frame = tracker.findHands(frame)
    lmList = tracker.getPostion(frame, draw=False)
    if lmList:
        signTipX, signTipY = lmList[8][1], lmList[8][2]
        thumbTipX, thumbTipY = lmList[4][1], lmList[4][2]
        if calculateIntDidtance((signTipX, signTipY), (thumbTipX, thumbTipY)) < 50:
            centerX = int((signTipX + thumbTipX) / 2)
            centerY = int((signTipY + thumbTipY) / 2)
            cv2.line(frame, (signTipX, signTipY), (thumbTipX, thumbTipY), (0, 255, 0), 2)
            cv2.circle(frame, (centerX, centerY), 5, (0, 255, 0), cv2.FILLED)

    ctime = time.time()
    fps = int(1 / (ctime - ptime))

    cv2.putText(frame, str(fps) + " FPS", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    showKey.drawKey(frame, (255, 255, 255), (0, 0, 0), 0.1, fontScale=0.5)
    exitKey.drawKey(frame, (255, 255, 255), (0, 0, 0), 0.1, fontScale=0.5)
    toggleKey.drawKey(frame, (255, 255, 255), (0, 0, 0), 0.1, fontScale=0.5)
    cv2.setMouseCallback('video', getMousPos)

    if showKey.isOver(clickedX, clickedY):
        show = not show
        showKey.text = "Hide" if show else "Show"
        clickedX, clickedY = 0, 0

    if toggleKey.isOver(clickedX, clickedY) or toggleKey.isOver(thumbTipX, thumbTipY):
        toggleKeyboard = not toggleKeyboard

    if exitKey.isOver(clickedX, clickedY):
        # break
        exit()

    # checking if sign finger is over a key and if click happens
    alpha = 0.5
    if show:
        if toggleKeyboard:
            createLowerCase()
        else:
            createUpperCase()
        textBox.drawKey(frame, (255, 255, 255), (0, 0, 0), 0.3)
        for k in keys:
            if k.isOver(mouseX, mouseY) or k.isOver(signTipX, signTipY):
                alpha = 0.1
                # writing using mouse right click
                if k.isOver(clickedX, clickedY):
                    if k.text == '<--':
                        textBox.text = textBox.text[:-1]
                    elif k.text == 'Clear':
                        textBox.text = ''
                    elif len(textBox.text) < 30:
                        if k.text == 'Space':
                            textBox.text += " "
                        else:
                            textBox.text += k.text

                # writing using fingers
                if k.isOver(thumbTipX, thumbTipY):
                    clickTime = time.time()
                    if clickTime - previousClick > 0.4:
                        if k.text == 'Backspace':
                            textBox.text = textBox.text[:-1]
                            keyboard.press("\b")
                        elif k.text == 'Clear':
                            textBox.text = ''
                        elif len(textBox.text) < 30:
                            if k.text == 'Space':
                                textBox.text += " "
                                keyboard.press(" ")
                            else:
                                textBox.text += k.text
                                # simulating the press of actual keyboard
                                keyboard.press(k.text)
                        previousClick = clickTime
            k.drawKey(frame, (255, 255, 255), (0, 0, 0), alpha=alpha)
            alpha = 0.5
        clickedX, clickedY = 0, 0
    ptime = ctime
    cv2.imshow('video', frame)

    ## stop the video when 'q' is pressed
    pressedKey = cv2.waitKey(1)
    if pressedKey == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
