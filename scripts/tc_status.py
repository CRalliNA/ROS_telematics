#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from telematics.msg import can_frame


def callback(data,args):
    pub=args[0]
    message=args[1]
    print('tc-status activated')       
    rospy.sleep(6)
    while not rospy.is_shutdown():
        message.ID=0x0CCBFFEC
        message.Dest=255
        message.Data=b'\xfe\xff\xff\xff\x01\x00\x00\xff'
        pub.publish(message)
        rospy.sleep(2)
def talker():
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    rospy.init_node('tc_status', anonymous=True)

    message=can_frame()
    

    rospy.Subscriber('tc_status',String,callback,(pub,message))
    rospy.spin()
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

