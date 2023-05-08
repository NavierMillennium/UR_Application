import cv2 as cv
from time import sleep
import os

# Initial camera settings
print("-------Program for saving calibration photos-------")
print("The photos are saved in the 'camera_correction_photos' folder\n. If the folder does not exist, it will be created relative to the current folder!!!\n")

# Set the parameters of the used camera 
camera = cv.VideoCapture(0, cv.CAP_DSHOW)
# Resolution
camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)#640
camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)#480
# Frames Per Second
camera.set(cv.CAP_PROP_FPS, 30)
# Stop the program so that the camera can start up
sleep(0.1)

# Check if the specified folder exists
# If there is no create it with the current directory
try:  
    if not os.path.exists('camera_correction_photos'):
        os.makedirs('camera_correction_photos')
# catch exception
except OSError:
    print ('Error! could not create folder')

# Dimensions of the calibration board used
heigth = int(input("Enter the number of chessboard corners vertically on the calibration table you are looking for: "))
width = int(input("Enter the number of chessboard corners horizontally on the calibration table you are looking for: "))

dim = (heigth, width)

currentPhoto = 1   # Variable for numbering filenames of saved photos 

while True:
    
    ret, img = camera.read()   
    cv.imshow('Camera', img)    # Displaying the image preview window

    # Waiting for the user to press the 's'-save key, the frame is displayed for 1ms
    key = cv.waitKey(1) & 0xFF
    
    if key == ord('q'):     #  If the key pressed is 'q' close the window and exit the program
        cv.destroyAllWindows()
        break
    elif key == ord('s'): # Key 's' - trying to write to a folder
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, dim, None)     # Searching for a chessboard

        if ret:  # If a checkerboard is detected in the frame
            print('Saved photo number:', currentPhoto) # Displays the information about saved image
            name = './camera_correction_photos/pict' + str(currentPhoto) + '.png'
            cv.imwrite(name, img)     # Save the photo to a folder
            currentPhoto += 1      # Incrementing photo numbering
        else:
            print('Nie znaleziono tablicy kalibracyjnej')

