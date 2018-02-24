#!/usr/bin/env python

import rospy
from turtlesim.msg import *
from turtlesim.srv import *
from geometry_msgs.msg import Twist
from std_srvs.srv import *
import random
from time import time
from math import atan2,pi, sqrt, pow
import sys

lastDistance = 1000000

#Gets the Hunter's Pose, this is a subscriber call back
def hunterPose(data):
    global turtle1x, turtle1y, turtle1theta
    turtle1x = data.x
    turtle1y = data.y
    turtle1theta = data.theta

#Gets the runner's Pose, this is a subscriber call back
def runnerPose(data):
    global runnerx, runnery
    runnerx = data.x
    runnery = data.y

#Create a new Turtle to Hunt
def spawnNewTurtle():
    global runnerx, runnery
    runnerx = random.randint(0, 11)
    runnery = random.randint(0, 11)
    spawnTurtle(runnerx,runnery,0,"runner")

#After finding a turtle, reset the stage for the next turtle
def resetHunt():
    global timeToFind, lastDistance
    try:
        killTurtle("runner")
    except:
        pass
    lastDistance = 1000000
    clearStage()
    spawnNewTurtle()
    timeToFind = time()

#Get the distance between two points on a plane.
def getDistance(x1, y1, x2, y2):
    return sqrt(pow((x2-x1),2) + pow((y2-y1),2))

def chaseRunner():
    global motion, lastDistance
    distance = getDistance(turtle1x, turtle1y, runnerx, runnery)
    targetTheta = atan2(runnery - turtle1y, runnerx - turtle1x)
    if (targetTheta<0):
       targetTheta += 2 * pi
    if (distance <= lastDistance):
        motion.linear.x = 1
    else:
        motion.linear.x = .1
    lastDistance=distance
    change = 1
    if (targetTheta - turtle1theta <0):
        change = -1
    motion.angular.z = 4 * (targetTheta - turtle1theta) * change
    pub.publish(motion)
    motion.angular.z = random.randint(0,2)
    motion.angular.x = random.randint(-1,1)
    pubrunner.publish(motion)


#Found all the Turtles we wanted to find.
def finishHunt():
    global motion
    motion.linear.x = 0
    motion.angular.z = 0
    pub.publish(motion)
    try:
        killTurtle("runner")
    except:
        pass
    clearStage()
    sys.exit()

#Main Function, sets up first hunt then loops.
def hunt():
    global turtle1x, turtle1y, runnerx, runnery

    #Set up board for first hunt.
    resetHunt()
    
    #Main Loop
    while not rospy.is_shutdown():

        #See how far away hunter is from runner
        distance = getDistance(turtle1x, turtle1y, runnerx, runnery)
        if (distance <= 1):
            resetHunt()   
        else:
            chaseRunner()

#Entry Point, sets up the ROS globals then calls hunt()
if __name__ == '__main__':
    try:
        global pub, pubrunner, rate, motion
        rospy.init_node('turtleHunt', anonymous=True)
        pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size = 10)
	pubrunner = rospy.Publisher('/runner/cmd_vel', Twist, queue_size = 10)
        rospy.Subscriber("/turtle1/pose", Pose, hunterPose) #Getting the hunter's Pose
        rospy.Subscriber("/runner/pose", Pose, runnerPose) #Getting the runner's Pose
        rate = rospy.Rate(30) #The rate of our publishing
        clearStage = rospy.ServiceProxy('/clear', Empty) #Blanks the Stage
        spawnTurtle = rospy.ServiceProxy('/spawn', Spawn) #Can spawn a turtle
        killTurtle = rospy.ServiceProxy('/kill', Kill) #Delets a turtle
        motion = Twist() #The variable we send out to publish
        hunt()

    except rospy.ROSInterruptException:
        pass
