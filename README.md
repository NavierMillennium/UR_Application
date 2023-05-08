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

## Examples

* **UR5 control section** - Enter easy URScript Comand, testing comunication

![UR control section](https://github.com/NavierMillennium/UR_Application/blob/master/screenshots/ur_control.png?raw=true)

* **Comunication with simulator** - We have to select DHCP in 'NETWORK' robot setup and check IP address

![Comunicaton with URsim](https://github.com/NavierMillennium/UR_Application/blob/master/screenshots/vmware.png?raw=true)

![Comunicaton with URsim - IO](https://github.com/NavierMillennium/UR_Application/blob/master/screenshots/vmware_io.png?raw=true)

* **Calibration process** - selecting new or load previes files

![Calibration process](https://github.com/NavierMillennium/UR_Application/blob/master/screenshots/calib_path.png?raw=true)

* **New calibration process** - selecting video source

![Image catcher](https://github.com/NavierMillennium/UR_Application/blob/master/screenshots/catch_frame.png?raw=true)

## Links
* [OpenCV-Python Tutorials][1]
* [Qt for Python][2]


[1]:https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
[2]:https://doc.qt.io/qtforpython-6/