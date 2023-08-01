UR5 CB2 series <--> camera
===============
The application contains a communication module dedicated to UR robots (especially for CB2 serie wich is currently not supported and and does not support modern protocols offered by Universal Robots company, for example RTDE ), vision tools for camera calibration, camera calibration with the robot and subsequent cooperation between the vision system and the robot.

In the basic interface, there is a service of consumer cameras available directly from the system level. The application also includes an additional module dedicated to [Allied Vison][3] industrial cameras using the [GiGE][4] protocol(Presented application was tested with Mako 145G and Vimba SDK([VimbaPython][5])).

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

* **Real robot UR5 CB2**:
https://user-images.githubusercontent.com/120511384/236850290-c5bf121d-2248-4c86-b6ac-8847bf14dcad.mp4


## Links
* [OpenCV-Python Tutorials][1]
* [Qt for Python][2]
* [Allied Vision][3]


[1]:https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
[2]:https://doc.qt.io/qtforpython-6/
[3]:https://www.alliedvision.com/en/?setLang=1&cHash=e2be2c30c770facfbce9b11cc6388dfa
[4]:https://en.wikipedia.org/wiki/GigE_Vision
[5]:https://github.com/alliedvision/VimbaPython
