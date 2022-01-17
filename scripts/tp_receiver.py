#!/usr/bin/env python


import rospy
from std_msgs.msg import String
from telematics.msg import can_frame
from tp_func import *
f=open('\home\charlie\Telemetry\object_pool.txt','w')
whole_msg=bytes()
last_packet=0
msg_bytes=0
msg_packets=0
PGN=bytes()
def callback(data,args):
    global whole_msg,last_packet,msg_bytes,msg_packets,PGN
    
    
    pub=args[0]
    message=args[1]
    my_address=args[2]
    
    PF=(data.ID>>16)&0xFF
    PS=(data.ID>>8)&0xFF
    #Look for RTS messages directed at us
    if PF==236 and PS==my_address:
        
        msg_bytes,msg_packets=TP_CTS(pub,message,data,my_address,msg_bytes,msg_packets)
        PGN=data.Data[5:8]
    #Receive data 
    if PF==235 and PS==my_address:   
        if data.Data[0]==last_packet+1:
            whole_msg=whole_msg+data.Data[1:8]
            last_packet=data.Data[0]
            
            if data.Data[0]==msg_packets: 
                print(whole_msg) #Do something with this
                f.write(str(whole_msg))
                
                whole_msg=bytes()
                last_packet=0
                TP_ACK(pub,message,data,my_address,msg_bytes,PGN)
                PGN=bytes()
                msg_bytes=0
                msg_packets=0
        else:
            print('Error in packet order')#find a better way of dealing with this at some point
        
        
        
        
def listener():

    rospy.init_node('tp_receiver', anonymous=True)
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    message=can_frame()
    my_address=236
    rospy.Subscriber('Received_CAN', can_frame, callback,(pub,message,my_address))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
