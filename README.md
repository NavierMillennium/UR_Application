UR5 CB2 series <--> camera
===============
**OpenCV** does not have an API for enumerating capture devices. The sample shows how to create a Python extension to invoke DirectShow C++ APIs for enumerating capture devices and corresponding resolutions.

## Dependencies   
* Python 3.10.4
* pyqt5==5.15.9
* pandas==1.5.0
* cv2 ==4.7.2
* numy
* json
* glob

![camera list in Python](https://raw.githubusercontent.com/yushulx/python-capture-device-list/master/screenshot/python-list-device.PNG)

## Links
* [OpenCV-Python Tutorials][1]
* [Qt for Python][2]


[1]:https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
[2]:https://doc.qt.io/qtforpython-6/