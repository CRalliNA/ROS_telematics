#!/usr/bin/env python

from tp_func import *
import rospy
from std_msgs.msg import String
from telematics.msg import can_frame
class tp_info:
    def __init__(self,PF,PS,dest,source,data):
        self.PF=PF
        self.PS=PS
        self.dest=dest
        self.source=source
        self.data=data

def RTS_callback(data,args):
    
    pub = args[0]
    message = args[1]
    msg=args[2]
    
    msg.PF=(data.ID>>16)&0xFF
    msg.PS=(data.ID>>8)&0xFF
    msg.dest=data.Dest
    msg.source=(data.ID&0xFF)
    msg.data=data.Data

    TP_RTS(message,pub,msg.PF,msg.PS,msg.source,msg.dest,msg.data)

    

def DT_callback(data,args):
    #Detect CTS message and send DT (data transfer) messages
    
    pub = args[0]
    message = args[1]
    msg=args[2]
    
    
    PF=(data.ID>>16)&0xFF
    PS=(data.ID>>8)&0xFF
    
    if PF==236 and PS==236 and data.Data[0]==17 and msg.PF!=None:
        TP_data_transfer(message,pub,msg.PF,msg.PS,msg.source,msg.dest,msg.data)
       
       
    msg.PF=None
    msg.PS=None
    msg.dest=None
    msg.source=None
    msg.data=None
        
def listener():

    rospy.init_node('tp_sender', anonymous=True)
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    message=can_frame()
    msg=tp_info(None,None,None,None,None)
    rospy.Subscriber('tp_to_send', can_frame, RTS_callback,(pub,message,msg))
    rospy.Subscriber('Received_CAN', can_frame, DT_callback,(pub,message,msg))
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
