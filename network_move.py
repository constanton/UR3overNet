#!/usr/bin/env python
import time, socket, serial, rospy, actionlib, threading
import roslib; roslib.load_manifest('ur_driver')
import numpy as np
from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from math import pi
from threading import Thread

JOINT_NAMES = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
               'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

Center = [-177.31,-121.21,-50.89,-216.94,270.30,15.05]
Left = [-170.56,-124.29,-51.11,-215.27,278.25,0.5]
Right = [-176.82,-124.95,-51.09,-214.26,272.90,27.99]
Down = [-177.61,-125.04,-50.75,-214.28,269.66,17.68]
Up = [-177.72,-119.92,-50.00,-214.88,269.52,15.04]
Forward = [-177.04,-123.78,-50.84,-210.05,270.25,15.05]
Back = [-177.34,-114.96,-51.01,-228.19,270.62,15.03]
client = None
th_gesture = "reset"

Center = np.asarray(Center)*pi/180.
Left = np.asarray(Left)*pi/180.
Right = np.asarray(Right)*pi/180.
Down = np.asarray(Down)*pi/180.
Up = np.asarray(Up)*pi/180.
Forward = np.asarray(Forward)*pi/180.
Back = np.asarray(Back)*pi/180.



def moveto(gesture):
	global joints_pos
        global th_gesture
        th_gesture = gesture
	if gesture == "left":
		move_to = Left
	elif gesture == "right":
		move_to = Right
	elif gesture == "up":
		move_to = Up
	elif gesture == "down":
		move_to = Down
	elif gesture == "forward":
		move_to = Forward
	elif gesture == "back":
		move_to = Back
	elif gesture == "reset":
		move_to = Center
        else:
		return
	g = FollowJointTrajectoryGoal()
   	g.trajectory = JointTrajectory()
        g.trajectory.joint_names = JOINT_NAMES
   	try:
           joint_states = rospy.wait_for_message("joint_states", JointState)
     	   joints_pos = joint_states.position
     	   g.trajectory.points = [
              JointTrajectoryPoint(positions=joints_pos, velocities=[0]*6, time_from_start=rospy.Duration(0.0)),
	      JointTrajectoryPoint(positions=Center, velocities=[0]*6, time_from_start=rospy.Duration(0.75)),
              JointTrajectoryPoint(positions=move_to, velocities=[0]*6, time_from_start=rospy.Duration(1.5))]
           client.send_goal(g)
           client.wait_for_result()
  	except KeyboardInterrupt:
           client.cancel_goal()
    	   raise
    	except:
     	   raise

#this thread is for sending feedback to a haptic glove
#it's not working as it is, you need to modify it to your own application
def send_thread(arg1, stop_event):
    global th_gesture
    feedback_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    prev_gest = th_gesture
    while (not stop_event.is_set()):
        if th_gesture != prev_gest:
		#grab a value from somewhere and put it inside msg to...
		feedback_socket.sendto(msg, ("xxx.xxx.xxx.xxx", 11006))
        prev_gest = th_gesture
        time.sleep(0.1)
              
  
def main():
    global client 
    global gesture
    try:
	#boolean to enable/disable movement when reset is received
	enable_move = False
	#initializing feedback thread and stop event
	thread1_stop = threading.Event()
	thread1 = Thread(target=send_thread, args=(1, thread1_stop))
    #we don't want duplicate movements
    prev_gesture = None;
    port = 11005
	#init socket for communication with UR3
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(("xxx.xxx.xxx.xxx", port))
	print "Waiting on port:", port
        rospy.init_node("test_move", anonymous=True, disable_signals=True)
        client = actionlib.SimpleActionClient('follow_joint_trajectory', FollowJointTrajectoryAction)
        print "Waiting for UR3 server..."
        client.wait_for_server()
        print "Connected to UR3 server"
        parameters = rospy.get_param(None)
        index = str(parameters).find('prefix')
        print "Please make sure that your robot can move freely between these poses before proceeding!"
        inp = raw_input("Continue? y/n: ")[0]
        if (inp == 'y'):
	    thread1.start()
            while 1:
				gesture, addr = s.recvfrom(54)
				if gesture == "reset":
					print gesture
					enable_move = not enable_move
				if (enable_move and prev_gesture != gesture) or gesture == "reset":
					print "Gesture received: ", gesture
					moveto(gesture)
					prev_gesture = gesture
				time.sleep(0.14)
		else:
            print "Halting program"
    except KeyboardInterrupt:
        rospy.signal_shutdown("KeyboardInterrupt")
	thread1_stop.set()
        thread1.join()
        raise

if __name__ == '__main__': main()
