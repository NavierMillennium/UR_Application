import sys
import ui
import cv2 as cv
import numpy as np

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5 import QtGui
from PyQt5.QtGui import (
    QPixmap,QStandardItemModel, QStandardItem
)
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog
)
from PyQt5.QtMultimedia import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import (
QMutex, QObject, QThread, pyqtSignal as Signal, pyqtSlot as Slot ,Qt, QModelIndex
)
#internal libraries 
from model import *

class Window(QMainWindow, ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # connect its signal to the update_image slot
        self.disply_width = 337
        self.display_height = 350
        self.video_thread_live = False
        self._calib_folder_path = ""
        # initialization processes
        self._connect_signals_slots()
        self._init_all_Widgets()
        
#------------Methods for: widgets-------------------  
    def _connect_signals_slots(self):
        """Connecting singals from all windows"""
        # Signals --> USB-Camera --> initPage
        self.btnStartCalibSeq.clicked.connect(lambda:self._calib_sequence(0))
        # Signals --> USB-Camera --> imgSrc
        self.btnLiveImg.clicked.connect(self._init_camera_connection)
        self.btnStopImg.clicked.connect(lambda:self.btnLiveImg.setEnabled(True))
        self.btnStopImg.clicked.connect(lambda:self.video_thread.stop())
        self.btnNextCamSeq.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.gridCalib))    
        self.btnNextCamSeq.clicked.connect(lambda:self._calib_sequence(1))
        self.listView.clicked[QModelIndex].connect(self._init_camera_connection)
        self.btnUpdateList.clicked.connect(self.update_camera_list)
        
        # Signals --> USB-Camera --> gridCalib
        self.btnStopImg_2.clicked.connect(lambda:self.btnLiveImg.setEnabled(True))
        self.btnStopImg_2.clicked.connect(lambda:self.video_thread.stop())
        self.btnLiveImg_2.clicked.connect(self._init_camera_connection)
        self.btnSaveImg.clicked.connect()
        self.btnNextCamSeq_2.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.resultUpdate))    
        self.btnBackCamSeq.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.imgSrc))  
       
        # Signals --> USB-Camera --> resultUpdate
        self.btnBackCamSeq_2.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.gridCalib))  
           
        #self.listView.clicked[QModelIndex].connect(self.video_index_to_graber)
        
        # Signal - menubar
        self.action_About.triggered.connect(self.about_info)
    
    def _init_all_Widgets(self):
        self.stackedWidget_2.setCurrentWidget(self.initPage)
        self.tabWidget.setCurrentWidget(self.URobot)
        self.tabForURmodule.setCurrentWidget(self.comTab)
        self.init_dynamic_icons()
    
    def init_dynamic_icons(self):
        """Graphical elements state initialisation"""
        self.iconImgSrcStep.clear()
        self.iconGridCalibStep.clear()
        self.iconResultUpdatesStep.clear()   
           
#------------Methods for window : USB-Camera-------------------          
    def _calib_sequence(self, step:int):
        # Init step - start calibration sequence - prepare all widgets
        # First step in calibration process (user select --> new calibration process)
        if step == 0:
            # Set icons for actual calibration step
            self.stackedWidget_2.setCurrentWidget(self.calibSeqPage)
            self.stackedWidget.setCurrentWidget(self.imgSrc)
            self.btnStopImg.setEnabled(False)
            self.btnNextCamSeq.setEnabled(False)
            self.listView.clicked[QModelIndex].connect(lambda:self.btnNextCamSeq.setEnabled(True))
            #self.init_dynamic_icons()
            self.iconImgSrcStep.setPixmap(QPixmap(r"src/ui/resources/iconGreenArrow.png"))
            # Get camera device list 
            self.update_camera_list()
        elif step == 1:
            
            pass
            
    def _init_camera_connection(self,index): 
        """Creating thread for camera object"""  
        index = self.listView.currentIndex().row()
        
        if self.video_thread_live:
            self.video_thread.stop()
        self.cam = Camera(index)
        self.video_thread = VideoThread(self.cam)
        self.video_thread.finished.connect(lambda:self.video_thread_slot(False))
        self.video_thread.finished.connect(self.video_thread.deleteLater)
        self.video_thread.started.connect(lambda:self.video_thread_slot(True))
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()
        
        self.btnLiveImg.setEnabled(False)  
        self.btnStopImg.setEnabled(True)
        self.btnLiveImg_2.setEnabled(False)  
        self.btnStopImg_2.setEnabled(True)

    def video_thread_slot(self,state):
        self.video_thread_live = state  
    def update_camera_list (self): 
     # Get camera device list 
        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
                pass 
        else:
            # Dispaly available camera list in listView object 
            self.model = QStandardItemModel()
            self.listView.setModel(self.model)  
            for i in self.available_cameras:
                self.model.appendRow(QStandardItem(i.description()))
    
    
    def _select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select project folder", "")
        if path:
           self._calib_folder_path = path
     
    
    def _save_selected_prop (self):
        pass        
#------------Methods for: cameras and frame graber-------------------    
        
    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.inputImg.setPixmap(qt_img)
        self.inputImg_2.setPixmap(qt_img)
        
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)
    
#------------Methods for: menubar and task bar-------------------
    def about_info(self): 
            QMessageBox.about(self,
        "Vision application for URrobot",
        "<p>Version - 1.0.0.1<p>"
        "<p>Copyright © 2023 - Kamil Skop<p>"
        "<p>GUI software: PyQt5</p>"
        "<p>Backend language: Python 3.10.4"
        "<p>Image processing and computer vsion: OpenCV 4.7.0</p>",
        )
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
