# 3WD RPi4 flex robot
Public repository for a 3WD robot usng the RPi-flex PCB and a RPi4 runnng the Bullseye 32bit OS, as illustrated below in 3WD omni-wheel build visualisations and a schematic to show how motor directions control robot movement:

<img src="images\3WD_robot_vis-image01.jpeg" width="210" height="200"> &nbsp; &nbsp; <img src="images\3WD_robot_vis-image08.jpeg" width="202" height="200">  &nbsp; &nbsp; <img src="images\3WD_omni-wheels-drive_logic_180DEG_600w.jpg" width="238" height="200">

More detailed project information can be found [here](https://onlinedevices.org.uk/RPi4_3WD_robot)

The designs for the associated custom 3D printed components can be downloaded from [here](https://www.printables.com/model/1288474-3wd-rpi-flex-pcb-robot).

A new updated design for the custom PCB is now used in this build (with changed version numbering!), with images shown below, and the KiCAD design gerber files can be downloaded from the 'PCB_design_files' folder.

<img src="images\RPi-flex_PCB02_front01_800w.jpg" width="138" height="250"> &nbsp; &nbsp; &nbsp; &nbsp;<img src="images\RPi-flex_PCB02_back01_800w.jpg" width="142" height="250">  &nbsp; &nbsp; &nbsp; &nbsp;<img src="images\RPi-flex_PCB02_back02_800W.jpg" width="146" height="250">

The completed build is shown in the images below and some initial code for testing individual components can be downloaded from the 'component_testing_code' folder - but the command text and paths for associated  code should be checked/updated for the specific installation.

The C-code used in various other code can be downloaded from the 'C-code' folder - with a gcc compilation command text to produce a .so library provided as a comment, but it should be amended for the appropriate file paths used in the actual installation.

More testing code and managing the robot's operational modes will be made available, along with some usage notes, in due course.

<img src="images\3WD_robot_20250428_074142243_1000w.jpg" width="287" height="250"> &nbsp; &nbsp; &nbsp; &nbsp;<img src="images\3WD_robot_20250428_074042638_1000w.jpg" width="307" height="250"> 

