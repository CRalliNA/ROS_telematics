#!/usr/bin/env python


import rospy,codecs
from std_msgs.msg import Int32
from telematics.msg import can_frame
from tp_func import *
from op_decode import *
f=open('/home/charlie/Telemetry/object_pool2.txt','a')
whole_msg=bytes()
last_packet=0
msg_bytes=0
msg_packets=0
PGN=bytes()
def callback(data,args):
    global whole_msg,last_packet,msg_bytes,msg_packets,PGN
    
    
    pub=args[0]
    pub2=args[1]
    pub3=args[2]
    message=args[3]
    my_address=args[4]
    
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
            
            if data.Data[0]==msg_packets:# and data.Data[0]==msg_bytes//7: 
                print(whole_msg) 
                print(PGN)
                dec_PGN=(PGN[1])+(PGN[2]<<18)
                message.ID=(dec_PGN<<16)+(my_address<<8)+(data.ID&0xFF)
                print(message.ID)
                message.Data=whole_msg
                message.Dest=my_address
                #print('sending pool')
                pub2.publish(message)
                
                
                whole_msg=bytes()
                last_packet=0
                TP_ACK(pub,message,data,my_address,msg_bytes,PGN)#calls function to acknowledge the tp messages
                
                if PGN==b'\x00\xcb\x00':#lets bus manager know that a tp has been received so it can send the object pool response
                    pub3.publish(data.ID&0xFF)
                
                PGN=bytes()
                msg_bytes=0
                msg_packets=0
        else:
            print('Error in packet order')#find a better way of dealing with this at some point
        
        
        
        
def listener():

    rospy.init_node('tp_receiver', anonymous=True)
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    pub2= rospy.Publisher('Received_CAN', can_frame, queue_size=10)
    pub3= rospy.Publisher('tp_received',Int32,queue_size=10)
    message=can_frame()
    my_address=236
    rospy.Subscriber('Received_CAN', can_frame, callback,(pub,pub2,pub3,message,my_address))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
