# UR3overNet
Python script for moving a UR3 robot over a local network to pre-selected positions using hand gestures (detected on the other edge of the network by some other program). The script is receiving commands in the form of Strings depending on the desired direction the robot should follow.

The script runs two threads. One is for acting as a UDP server that receives sting messages and interacts with UR3 to make it move. 

The other one is for receiving feedback from a sensor (this code is not in the script but in my case it was a simple serial communication with an Arduino) and sending UDP messages to the other side of the network. This part of the code of course needs further modification in case you need it to work, to adapt it to your application.

The code was made to just work and it's not optimized. It would also be great to have the option for directly controlling UR3 (ie. not with gestures)

More info on my blog: http://blog.antonakoglou.com/controlling-ur3-gestures-network/

## Credits
Special thanks to [arvyram](https://github.com/arvyram) and [headamage](https://github.com/headamage) for the Python hints and tips.
