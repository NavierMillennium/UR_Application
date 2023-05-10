import cv2 as cv
import pandas as pd
import numpy as np
from PyQt5.QtCore import QMutex, QObject, QThread, pyqtSignal as Signal, pyqtSlot as Slot ,Qt
import os  
import json
import glob
class Camera():

    def __init__(self,imgSrc):
        # Parameters for cornerSubPix() 
        self.__MAX_COUNT = 30
        self.__EPSILON = 0.001 
        self.image_index = 0
        self._imgSrc = imgSrc
        self.last_frame = np.zeros((1,1))
        self.data = {}
        
        
    # @contextmanager
    # def cam_init(self):
    #     try:
    #         self.cap = cv.VideoCapture(self._imgSrc)
    #         yield self
    #     finally:
    #         print("I was calling")
    #         self.cap.release()   
       
    def __enter__(self):
        self.cap = cv.VideoCapture(self._imgSrc)
        if not self.cap.isOpened():
            raise Exception("Error: Cannot open camera!") 
        else:
            return self
    def __exit__(self, exc_type, exc_value, tb):
        self.cap.release()
        
    def available_camera_resolution(self):
        """Checking available camera resolution"""
        url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
        table = pd.read_html(url)[0]
        table.columns = table.columns.droplevel()
        resolutions = []
        for _, row in table[["W", "H"]].iterrows():
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, row["W"])
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, row["H"])
            width = self.cap.get(cv.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)
            resolutions.append(str(width)+"x"+str(height))
        list(dict.fromkeys(resolutions))
    def get_frame(self):
        """Caching frame from camera"""
        ret, self.last_frame = self.cap.read()
        if not ret:
            raise Exception("Error: Frames not received!")
        else:
            return self.last_frame   
    
    @property
    def brightness(self):
        """Getter brightness funtion"""
        return self.cap.get(cv.CAP_PROP_BRIGHTNESS)
    
    #@brightness.setter
    def brightness(self, alpha = 1.0, beta = 0):
        #self.cap.set(cv.CAP_PROP_BRIGHTNESS, value)
        image = self.last_frame
        new_image = np.zeros(image.shape, image.dtype)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                for c in range(image.shape[2]):
                    new_image[y,x,c] = np.clip(alpha*image[y,x,c] + beta, 0, 255)
        self.last_frame = new_image
        
    def _create_folder(self,project_path):
        """Prepare folder for calibration images"""
        try:  
            if not os.path.exists('camCorr_img'):
                os.makedirs('camCorr_img')
        # Catch exception
        except OSError:
            raise ('Error! Cannot create folder')
    def init_congif_file(self):
        """Initialisation configuration 'json.' file """
        self.data = {
            'video_source':{
                'name':'',
                'id':''
            },
            'cam_calibration': {
                'mtx':'',
                'dist':''
            },
            'pos_calibration':{
                'T':'',
                'distRatio':'',
                'U_vector':''
            }
        }
        # Create --> config.json file
        with open('config.json','w') as config_file:
            json.dump(self.data, config_file, sort_keys=True, indent=4)

    def config_files_exist(self,project_path):
        if not os.path.exists('camCorr_img') or not os.path.isfile('config.json'):
            raise Exception('One of config files exist!')
    def image_save(self, img:np.ndarray, dim:int):
        """Save image with calibration table"""
        self._create_folder()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  
        # Checking calibration images before saving
        ret, _ = cv.findChessboardCorners(gray, dim, None) 

        if ret:  
            self.image_index+=1 
            path = './camCorr_img/pict' + str(self.image_index) + '.png'
            cv.imwrite(path, img)         
        else:
            raise Exception('Chessboard corners not found ') 
    
    @property
    def __MAX_COUNT(self):
        return self.__MAX_COUNT
    @__MAX_COUNT.setter
    def __MAX_COUNT(self,MAX_COUNT:int):
        try:
            if 20 < int(MAX_COUNT) and 20 < int(MAX_COUNT):
                self.__MAX_COUNT = MAX_COUNT
        except ValueError:
            raise ValueError('Enter value must be number') from None
 
    @property
    def __EPSILON(self):
        return self.__MAX_COUNT
    @__EPSILON.setter
    def __EPSILON(self,EPSILON:float):
        try:
            if 0.0001 < int(EPSILON) and 0.1 < int(EPSILON):
                self.__EPSILON = EPSILON
        except ValueError:
            raise ValueError('Enter value must be number') from None
        
    def calib_camera(self,folder_path:str,dim:tuple):
       
        # Criteria for termination of the iterative process of corner refinement.
        # That is, the process of corner position refinement stops either after criteria.maxCount iterations or when the corner position moves by less than criteria.epsilon on some iteration.
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, self.__MAX_COUNT, self.__EPSILON)

        objpoints = []
        imgpoints = [] 

        images = glob.glob(folder_path+'/*.png') 
       
        objp = np.zeros((dim[0]*dim[1], 3), np.float32)
        objp[:,:2] = np.mgrid[0:dim[0], 0:dim[1]].T.reshape(-1, 2)

        for fname in images:
            img = cv.imread(fname) 
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  
            ret, corners = cv.findChessboardCorners(gray, dim, None)    

            if ret == True:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)     
                imgpoints.append(corners2)
        ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        #Saving data from calibration process
        mean_error = 0      
        camConfigRaport = np.empty(shape=(0, 4))   

        for rv, tv, fname, objpnt, imgpnt in zip(rvecs, tvecs, images, objpoints, imgpoints):
            if '/' in fname:
                fname = fname.split('/')
                fname = fname[1]
            if '\\' in fname:
                fname = fname.split('\\')
                fname = fname[1]
          
            imgpoints2, _ = cv.projectPoints(objpnt, rv, tv, mtx, dist)
           
            error = cv.norm(imgpnt, imgpoints2, cv.NORM_L2)/len(imgpoints2)
           
            camConfigRaport = np.append(camConfigRaport, [[fname, rv, tv, error]], axis=0)
            mean_error += error

        mean_error = mean_error / len(objpoints)   

        with open(folder_path+'/raport.txt', "w") as f:
            for x in camConfigRaport:
                s = '\n\nfile: ' + x[0] + ',\nrotation vector:\n' + str(x[1]) + ',\ntranslation vector:\n' + str(x[2]) + ',\nreprojection error: ' + str(x[3])
                f.write(s)
          
                
        with open('config.json','r') as config_file:
            config = json.load(config_file)

       
        config['cam_calibration']['mtx'] = mtx.tolist()
        config['cam_calibration']['dist'] = dist.tolist()
        
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, sort_keys=True, indent=4)
            
        return mean_error
    
class VideoThread(QThread):
    finished = Signal()
    change_pixmap_signal = Signal(np.ndarray)
    def __init__(self,camera:Camera):
        super().__init__()
        self._camera = camera
        self._run_flag = True

    def run(self):
        """Capture frame from input camera"""
        with self._camera as cam:
            while self._run_flag:
                try:
                    frame = cam.get_frame()
                except Exception as error:
                    print(error)
                    break
                else:
                    self.change_pixmap_signal.emit(frame)
        self.finished.emit()
        
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.quit()
        self.wait()

if __name__ == '__main__':
    with Camera(1) as cam:
            while True:
                try:
                    frame = cam.get_frame()
                except Exception as error:
                    print(error)
                    break
                else:
                    cam.brightness = 0.1
                    # Display the resulting frame
                    cv.imshow('frame', frame)
                if cv.waitKey(1) == ord('q'):
                    break