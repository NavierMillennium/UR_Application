import numpy as np
import cv2 as cv
import glob
import json

# Set criteria for ending calculations
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Matrixs that store the coordinates of the object's points and the coordinates of the pixels in the image
objpoints = [] # three-dimensional coordinates of the object
imgpoints = [] # two-dimensional coordinates of a point in the image

images = glob.glob('camera_correction_photos/*.png')  # Creating a list of objects with the extension .png located in the cam_correction_photos directory
# Entering the dimensions of the array
heigth = int(input("Enter the number of chessboard corners vertically on the calibration table you are looking for: "))
width = int(input("Enter the number of chessboard corners horizontally on the calibration table you are looking for: "))
dim = (heigth, width)

# Preparation of coordinates of points on the calibration board
objp = np.zeros((heigth*width, 3), np.float32)
objp[:,:2] = np.mgrid[0:heigth, 0:width].T.reshape(-1, 2)

# Loop performed for each photo found in the above directory (camera correction photos)
for fname in images:
    img = cv.imread(fname)  
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) 

    ret, corners = cv.findChessboardCorners(gray, dim, None)    

    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)   # A function that increases the accuracy of the coordinates of detected corners
        imgpoints.append(corners2)

# A function that returns the internal parameters of the camera, the distortion vector as well as the rotation and translation vectors
ret, mtx_old, dist_old, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

mean_error = 0      # Initialization of a variable holding the average reprojection error
camConfigRaport = np.empty(shape=(0, 4))    # Initializing an array containing [image name, rotation vector, translation vector, reprojection error]

# Saving rotation, translation and reprojection error vectors to an external file
for rv, tv, fname, objpnt, imgpnt in zip(rvecs, tvecs, images, objpoints, imgpoints):
    # Usuwanie nazwy folderu ze ścieżki zdjęcia
    if '/' in fname:
        fname = fname.split('/')
        fname = fname[1]
    if '\\' in fname:
        fname = fname.split('\\')
        fname = fname[1]
    # 2D coordinate projection based on camera parameters matrix, distortion vector, rotation and translation vector
    imgpoints2, _ = cv.projectPoints(objpnt, rv, tv, mtx_old, dist_old)
    # Reprojection error calculation
    error = cv.norm(imgpnt, imgpoints2, cv.NORM_L2)/len(imgpoints2)
    # Adding information about rotation and translation vectors and reprojection error to the table
    camConfigRaport = np.append(camConfigRaport, [[fname, rv, tv, error]], axis=0)
    mean_error += error

mean_error = mean_error / len(objpoints)    # Calculation of the average reprojection error

# Saving information about rotation and translation vectors as well as reprojection error for each analyzed image to the table file
with open('camera_correction_photos/raport.txt', "w") as f:
    for x in camConfigRaport:
        s = '\n\nfile: ' + x[0] + ',\nrotation vector:\n' + str(x[1]) + ',\ntranslation vector:\n' + str(x[2]) + ',\nreprojection error: ' + str(x[3])
        f.write(s)

print('The average value of the reprojection error is: ', mean_error)

# Recalculation of the distortion vector 
# This time for images with a reprojection error less than the user-specified
error = float(input('Enter the error value for which the camera will be recalibrated: '))

# Matrix that store the coordinates of the object's points and the coordinates of the pixels in the image
objpoints = [] # three-dimensional coordinates of the object
imgpoints = [] # two-dimensional coordinates of a point in the image

good_img = 0

for i, fname in enumerate(images):
    img = cv.imread(fname)  
    if '/' in fname:
        fname = fname.split('/')
        fname = fname[1]
    if '\\' in fname:
        fname = fname.split('\\')
        fname = fname[1]
    if camConfigRaport[i-1][3] <= error:
        good_img += 1
        print(fname)
        print(i)
        cv.imwrite('camera_correction_photos/second_run/'+fname, img)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  

        ret, corners = cv.findChessboardCorners(gray, dim, None)  

        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria) 
            imgpoints.append(corners2)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

for rv, tv, fname, objpnt, imgpnt in zip(rvecs, tvecs, images, objpoints, imgpoints):
    imgpoints2, _ = cv.projectPoints(objpnt, rv, tv, mtx_old, dist_old)
    error = cv.norm(imgpnt, imgpoints2, cv.NORM_L2) / len(imgpoints2)
    mean_error += error

mean_error = mean_error / len(objpoints)
print("Rejected %d images from %d" % (len(images)-good_img, len(images)))
print("New average reprojection error: ", mean_error)


print("\nPrimary matrix of internal parameters:\n", mtx_old)
print('New matrix of internal parameters:\n', mtx)

print("\nThe original distortion vector:\n", dist_old)
print("New distortion vector:\n", dist)
# Przygotoawnie .json file
data = {
    "cam_calibration": {
        "mtx":'',
        "dist":''
    },
    'pos_calibration':{
        'T':'',
        'distRatio':'',
        'U_vector':''
    }
}
with open('config.json','w') as config_file:
    json.dump(data, config_file, sort_keys=True, indent=4)

with open('config.json','r') as config_file:
    config = json.load(config_file)

# Assigning the determined values of the camera parameters matrix and the distortion vector to variables in the configuration file
config['cam_calibration']['mtx'] = mtx.tolist()
config['cam_calibration']['dist'] = dist.tolist()

# Saving the above values to the configuration file
with open('config.json', 'w') as config_file:
    json.dump(config, config_file, sort_keys=True, indent=4)

# Remove distortions from calibration images and save them to a folder (camera_correction_photos/undistored_images)
images = glob.glob('camera_correction_photos/*.png')

for fname in images:
    img = cv.imread(fname)
    if '/' in fname:
        fname = fname.split('/')
        fname = fname[1]
    if '\\' in fname:
        fname = fname.split('\\')
        fname = fname[1]
    dst = cv.undistort(img, mtx, dist)
    cv.imwrite('camera_correction_photos/undistored_images/' + fname, dst)
