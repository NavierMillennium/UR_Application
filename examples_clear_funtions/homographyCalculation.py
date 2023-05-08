import cv2 as cv
import math
from time import sleep
import json
import numpy as np
import sys

def distance(pointA, pointB):
    dist = math.sqrt((pointA[0]-pointB[0])**2 + (pointA[1]-pointB[1])**2)
    return dist

# Downloading data about the camera, the homography matrix and the order of the elements
# from the configuration file, setting the element pointer to the first value
# config, order, mtx, dist, T, distRatio, thresholdValue, objectHeight = cvis.configRead('config.json')
with open("config.json") as confige_file:
    data =json.load(confige_file)
    
    mtx = np.array(data['cam_calibration']['mtx'])
    dist = np.array(data['cam_calibration']['dist'])
    
print("Camera matrix read:\n ", mtx)
print("\nRead vector of dispersion coefficients:\n", dist)

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Initial camera settings
camera = cv.VideoCapture(0, cv.CAP_DSHOW)
camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv.CAP_PROP_FPS, 30)
# Stop the program so that the camera can start up
sleep(0.1)

# Initialization of arrays to store coordinates of points in the image and in robot space
U = np.empty(shape=(4, 2))
X = np.empty(shape=(4, 2))
print("\n--------------------------------------------------------------------------------------------------")
print("-----------------------------------Camera calibration with the robot--------------------------------------")
print("----------------------------------------------------------------------------------------------------")
print("Description of the calibration procedure:")
print("1.Move the robot's gripper out of the camera's field of view")
print("2.Place the calibration chart in the field of view of the camera")
print("3.Press 'Enter'")
print("4.Position the robot tip at the indicated points")
print("5.After reading the position of the robot, enter the coordinates of the corresponding points in [mm]")

# Wprowadzenie rozmiarów tablicy kalibracyjnej (ilość przecinających się narożników)
chess_heigth = int(input("Enter the number of chessboard corners vertically on the calibration table you are looking for:"))
chess_width = int(input("Enter the number of chessboard corners horizontally on the calibration table you are looking for:"))
dim = (chess_heigth, chess_width)

while True:

    ret, img = camera.read()   
    
    img = cv.undistort(img, mtx, dist)  # Removal of image distortion
    cv.startWindowThread()
    cv.namedWindow("Homography Calculation")
    cv.imshow("Homography Calculation", img)      # Displaying the image preview window

    # Waiting for the user to press a key, the frame is displayed for 1ms
    # The logical operator AND makes only the first byte returned by the function valid
    # so it doesn't matter if the key was pressed with CapsLock on or not
    
    key = cv.waitKey(1) & 0xFF

    # Loop if key pressed is ENTER  
    if key == 13:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  
        ret, corners = cv.findChessboardCorners(gray, dim, None)   
        if ret:
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria) 
            cv.imwrite('homography_calculation.png', img)
            # Assigning the extreme points of the calibration chart to the matrix
            # For this we use the 'objp' matrix written....
            # ....below specifying the coordinates of the points on the calibration chart
            # objp = np.zeros((heigth*width, 3), np.float32)
            # objp[:,:2] = np.mgrid[0:heigth, 0:width].T.reshape(-1, 2)
            
            U[0] = [corners2[0,0,0],corners2[0,0,1]]
            U[1] = [corners2[dim[0]-1,0,0],corners2[dim[0]-1,0,1]]
            U[2] = [corners2[len(corners2)-dim[0],0,0],corners2[len(corners2)-dim[0],0,1]]
            U[3] = [corners2[len(corners2)-1,0,0],corners2[len(corners2)-1,0,1]]
            
            # Drawing positions and numbers of individual calibration points on the image
            for num, cnt in enumerate(U):
                cv.circle(img, (int(cnt[0]), int(cnt[1])), 5, (0, 0, 255), 3)
                cv.putText(img, str(num + 1), (int(cnt[0]) + 10, int(cnt[1]) - 10), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 1)
            cv.startWindowThread()
            cv.namedWindow("Position Calibration")
            cv.imshow('Position Calibration', img)
            cv.waitKey(0)
            cv.imwrite('homography_calculation_points.png', img)
            #Loop assigning coordinates of points in the space of the robot
            for num, point in enumerate(X):
                x = input('Współrzędna X punktu nr [mm]:' + str(num + 1) + ':')
                y = input('Współrzędna Y punktu nr [mm]:' + str(num + 1) + ':')
                point[0] = float(x) / 1000
                point[1] = float(y) / 1000

            T = cv.findHomography(U, X) # Homography matrix calculation camera -> robot
            print(X) # Displaying the coordinate matrix of points in the space of the robot
            distRatio = float(distance(X[0], X[2]) / distance(U[0], U[2]))  # Calculation of the length proportionality coefficient in the m/pixel unit
            print("Macierz homografii:\n", T[0])
           # Saving the calculated values to the configuration file
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            config['pos_calibration']['T'] = T[0].tolist()
            config['pos_calibration']['distRatio'] = distRatio
            config['pos_calibration']['U_vector'] = U.tolist()
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, sort_keys=True, indent=4)
            cv.destroyAllWindows()
            sys.exit()
        else:
            print("No calibration table was detected in the camera area")

    # Quit the program if the key pressed is q or Esc
    elif key == ord('q') or key == 27:
        print("The calibration process has been interrupted")
        cv.destroyAllWindows()
        break
