#!/usr/bin/env python

import rospy
import os
import sys

if __name__ == '__main__':
    try:
        os.system("roslaunch turtlebot_bringup minimal.launch --screen")
	os.system("roslaunch turtlebot_rviz_launchers view_navigation.launch --screen")
	os.system("roslaunch turtlebot_navigation amcl_demo.launch map_file:=~/catkin_ws/src/PopliL/src/map/roboticsLab.yaml")

    except rospy.ROSException:
        pass
