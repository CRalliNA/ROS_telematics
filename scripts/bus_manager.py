#!/usr/bin/env python


import rospy
from std_msgs.msg import String
from telematics.msg import can_frame
from msg_funcs import *


def callback(data,args):
    pub=args[0]
    status_pub=args[1]
    message=args[2]
    my_address=236#make this variable 
    
    #Looking for messages requesting we respond
    if (data.ID>>16)&0xFF==234 and (data.ID>>8)&0xFF==236:#PF and PS make our address a variable?
        
        bus_respond(pub,message,data,my_address) #function sends response to request from another ecu on the bus
    elif (data.ID>>16)&0xFF==234 and data.Data==b'\x00\xee\x00':
        address_claim(pub,message) #responds to address claim message
    	status_pub.pubish('1')
    
    elif (data.ID>>16)&0xFF==203 and (data.ID>>8)&0xFF==236:#Responds to process data messages
        implement_respond(pub,message,data,my_address)
    
     

def listener():
    
    rospy.init_node('bus_manager', anonymous=True)
    rospy.loginfo('start')
    pub=rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    status_pub=rospy.Publisher('tc_status', String, queue_size=10)
    
    message=can_frame()
    rospy.sleep(0.5)
    #Send address request message
    
    message.ID=0x18EAFFFE
    message.Dest=255
    message.Data=b'\x00\xee\x00'
    pub.publish(message)
    
    rospy.sleep(0.1)
    #Calls function to send a message containing our NAME and address
    address_claim(pub,message)
    status_pub.publish('1')
    
    
    rospy.Subscriber('Received_CAN', can_frame, callback,(pub,status_pub,message))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
