import socket
import time
import json
import numpy as np
import cv2 as cv
import orientation as ort
from time import sleep
import sys

#Specify the server IP address (local PC) and port
HOST = '192.168.0.110'
PORT = 10000

# Create a socket for TCP/IP communication between the computer and the robot
# with statement --> exeption handling, we don't need to use s.close()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	
	s.bind((HOST, PORT))
	s.listen(5)
	print('Waiting for connection')
	connection, client_addr = s.accept() 

	with connection:
		print('Connection from: ', client_addr)  
		with open("config.json") as confige_file:
			data =json.load(confige_file)
   
		mtx = np.array(data['cam_calibration']['mtx'])
		dist = np.array(data['cam_calibration']['dist'])
		H = np.array(data['pos_calibration']['T'])
		U = np.array(data['pos_calibration']['U_vector'])
		
		obj_point = np.empty((1,1,2), dtype=np.float32)
		
		print("Camera matrix read:\n ", mtx)
		print("\nRead vector of distortion coefficients:\n", dist)
		print("\nHomography matrix read:\n",H)
		print("\nInput vector read:\n",U)
  
		cap = cv.VideoCapture(0)
		cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)#640
		cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)#480
	
		cap.set(cv.CAP_PROP_FPS, 30)
		sleep(0.1)
		if not cap.isOpened():
			print("Cannot open camera")
			exit()
		try:
			while True:
				# Send the X Y plane offset vector to the UR5
				# String: coordinates in meters
				#(X,Y)
				ret, img = cap.read()
				#img = img[:,:590]
				img = cv.undistort(img, mtx, dist) 
				gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
				#Thresholding of the input image
				_, bw = cv.threshold(gray, 70, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
				# Contour recognition, position and orientation estimation
				# a,_ = function() '_' - skip the return value
				contours, _ = cv.findContours(bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

				for i, c in enumerate(contours):
					# Calculate the area of each contour
					area = cv.contourArea(c)
					# We reject contours with too small or too large an area
					if area < 1e3 or 2e4 < area:
						continue
					cv.drawContours(img, contours, i, (0, 0, 255), 2)
					# Determining the orientation for each of the contours
					[angle,cntr] = ort.getOrientation(c, img)
					print("Orientation:{ort}, Center point:{pose}".format(ort=angle,pose=cntr))
				
				obj_point[0,0,0] = cntr[0]
				obj_point[0,0,1] = cntr[1]
				#Determine on the basis of previously determined
				#matrix of the homography of the coordinates of the object in the global system
				robotFramePoint = cv.perspectiveTransform(obj_point, H)
				#Correction of the obtained position
				#offset_x, offset_y =-0.04195,0.011506
				offset_x, offset_y = 0,0
				robotFramePoint[0,0,0]+=offset_x
				robotFramePoint[0,0,1]+=offset_y
				print('Robot frame pose:',robotFramePoint)
    
				if img is None:
					sys.exit("Odczyt obrazu nie powiódł się")
				cv.imshow("Display window", img)
				k = cv.waitKey(0)
				cv.destroyAllWindows()
				# Expected to accept object position
				# Protection against possible 'Locator' errors
				if input("Zakaceptuj pozycję: ") == str(1):
					x = float(robotFramePoint[0,0,0])
					y = float(robotFramePoint[0,0,1])
					connection.sendall(('(' + str(round(x,5)) + ', ' + str(round(y,5)) 
							+ ')').encode('ascii'))
					time.sleep(0.5)
					data = connection.recv(1024).decode('ascii')  
					print("Response:{}".format(data))
		except KeyboardInterrupt:
			print('Script interrupted')