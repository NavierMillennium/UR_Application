import cv2 as cv
import orientation as ort
import json
import numpy as np
import time

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv.CAP_PROP_FPS, 30)
time.sleep(1)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
# Downloading data about the camera, the homography matrix and the order of the elements
# from the configuration file, setting the element pointer to the first value
# config, order, mtx, dist, T, distRatio, thresholdValue, objectHeight = cvis.configRead('config.json')
with open("config.json") as confige_file:
    data =json.load(confige_file)
    mtx = np.array(data['cam_calibration']['mtx'])
    dist = np.array(data['cam_calibration']['dist'])
    
while True:
  
    ret, src = cap.read()

    src = cv.undistort(src, mtx, dist)  
    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
    
    # Image thresholding
    _, bw = cv.threshold(gray, 70, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    deleteFrame=[]

    cv.imshow('Image window', src)
    key = cv.waitKey(1) & 0xFF
   # ENTER - take a photo, determine the ROI
    if key == 13:
        # Copy the input target frame for the record of the defined ROI
        # To not save marked markers and axes
        imageCopy = src.copy()
        templateCopy = src.copy()
        cv.startWindowThread()
        for i, c in enumerate(contours):
            # Calculation of contour areas 
            area = cv.contourArea(c)
            # We reject contours with too small or too large an area 
            if area < 1e3 or 1e7 < area:
                continue
            # Applying contours to the image 
            cv.drawContours(src, contours, i, (0, 0, 255), 2)
            # Determining the orientation for each of the contours
            [angle,cntr] = ort.getOrientation(c, src)
            cv.putText(src, str(i), (int(cntr[0]) + 10, int(cntr[1]) - 10), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 1)
            print('Cordinate {iter}: X={x}, Y={y}'.format(iter=i,x=cntr[0],y=cntr[1]))
            deleteFrame.append(i)
        cv.imshow('Image window', src)
        cv.waitKey(0) 
        cv.destroyAllWindows()
        # Delete areas not belonging to the object
        print('Enter the numbers of the objects to be deleted. When done type "confirm"')
        print('Input vector: ',deleteFrame)
        while True:
            enter = input('Enter value:')
            if enter == 'confirm':
                break
            else:
                try:
                    float(enter)
                except:
                    print('The entered value is not a number')
                    
                try:
                    deleteFrame.remove(float(enter))
                except:
                    print("There is no such identifier")
        print('Vector after reduction: ', deleteFrame)

        for i in deleteFrame:
            print(i)
            contours_tmp = contours[i]
            # Applying contours to the image
            cv.drawContours(imageCopy, contours_tmp, i, (0, 0, 255), 2)
            # Determining the orientation for each of the contours
            [angle,cntr] = ort.getOrientation(contours_tmp,imageCopy)
            cv.putText(imageCopy, str(i), (int(cntr[0]) + 10, int(cntr[1]) - 10), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 1)
            print('Coordinate {iter}:X={x}, Y={y}'.format(iter=i,x=cntr[0],y=cntr[1]))
        cv.imshow('New image display', imageCopy)
        cv.waitKey(0)
        # ROI setting and image saving
        x = int(input('Podaj rozmiar ROI: '))
        template_img = templateCopy[(cntr[1]-x):(cntr[1]+x),(cntr[0]-x):(cntr[0]+x)]
        cv.imwrite('template_01_new_toDelete.png', template_img)
        cv.imwrite('template_00_new_toDelete.png', templateCopy)
        break

    # End the program if the q or Esc key is pressed
    elif key == ord('q') or key == 27:
        print("Proces przerwany")
        cv.destroyAllWindows()
        break