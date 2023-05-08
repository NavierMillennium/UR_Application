import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import time 
MIN_MATCH_COUNT = 10
cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)#640
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)#480

cap.set(cv.CAP_PROP_FPS, 30)
time.sleep(1)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
# ------ trainImage -----------
img1 = cv.imread('template_01.png',0) # trainImage
while True:
    ret, img2 = cap.read()   # Odczytanie kadru z kamery(dlatego też funkcję 
    if ret :
        img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY) 
        # Initiate SIFT detector
        sift = cv.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)
        if len(good)>MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
            M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            h,w = img1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv.perspectiveTransform(pts,M)
            img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)
        else:
            #print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
            matchesMask = None
        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                        singlePointColor = None,
                        matchesMask = matchesMask, # draw only inliers
                        flags = 2)
        img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
        cv.imshow('img',img3)    
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'): 
            cv.destroyAllWindows()
            break
       
   