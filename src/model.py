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
        self.MAX_COUNT = 30
        self.EPSILON = 0.001 
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
        
    def create_folder(self,project_path):
        """Prepare folder for calibration images"""
        try:  
            if not os.path.exists('camCorr_img'):
                os.makedirs('camCorr_img')
            else:
                return 1
        # catch exception
        except OSError:
            return -1
        else:
            return 0
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

    def config_file_exist(self,project_path):
        if not os.path.exists('camCorr_img') or os.path.isfile('config.json'):
            return -1
        else:
            return 0
    @property
    def criteria_SubPix(self):
        return [self.MAX_COUNT, self.EPSILON]
    
    def criteria_SubPix(self,MAX_COUNT:int,EPSILON:float)->None:
        
        if 20 < MAX_COUNT and 20 < MAX_COUNT:
            self.MAX_COUNT = MAX_COUNT
            self.EPSILON = EPSILON
        
         
    def calib_camera(self):
       
        # Criteria for termination of the iterative process of corner refinement.
        # That is, the process of corner position refinement stops either after criteria.maxCount iterations or when the corner position moves by less than criteria.epsilon on some iteration.
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, self.MAX_COUNT, self.EPSILON)

        # Macierze przechowywujące współrzędne punktów obiektu i współrzędne pikseli na obrazie
        objpoints = [] # trójwymiarowe współrzędne obiektu
        imgpoints = [] # dwuwymiarowe współrzędne punktu na obrazie

        images = glob.glob('camera_correction_photos/*.png')  # Utworzenie listy obiektów o rozszeżeniu .png znajdujących się w katalogu cam_correction_photos
        # Wprowadzenie wymiarów tablicy
        heigth = int(input("Podaj ilość narożników szachownicy w pionie na szukanej tablicy kalibracyjnej: "))
        width = int(input("Podaj ilość narożników szachownicy w poziomie na szukanej tablicy kalibracyjnej: "))
        dim = (heigth, width)

        # Przygotowanie współrzędnych punktów na planszy kalibracyjnej
        objp = np.zeros((heigth*width, 3), np.float32)
        objp[:,:2] = np.mgrid[0:heigth, 0:width].T.reshape(-1, 2)

        # Pętla wykonywana dla każdego zdjęcia znalezionego w powyższym katalogu (camera_correction_photos)
        for fname in images:
            img = cv.imread(fname)  # Odczytanie obrazu
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Konwersja BGR na skalę szarości

            ret, corners = cv.findChessboardCorners(gray, dim, None)     # Wyszukanie wzoru szachownicy na zdjęciu

            if ret == True:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)     # Funkcja zwiększająca dokładność współrzędnych wykrytych narożników
                imgpoints.append(corners2)

        # Funkcja zwracająca parametry wewnętrzne kamery, wektor zniekształceń oraz wektory rotacji i translacji
        ret, mtx_old, dist_old, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

          
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