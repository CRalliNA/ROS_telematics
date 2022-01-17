#!/usr/bin/env python


import rospy,can,struct
from std_msgs.msg import String
from telematics.msg import can_frame
from can import Message
can_interface='can0'
bus= can.interface.Bus(can_interface, bustype='socketcan')
write_f=open('/home/charlie/Telemetry/telematics.csv','w')#Writing to csv for testing
write_f.write('S/R,ID,PF,PS,SA,Data\n')


def callback(data,args):
    message=args[0]
    tp_pub=args[1]
    if len(data.Data)>8 :#and len(data.Data)<=(255*7):
        #255*7 is the max number you can write in the sequence number section of the tp packet
        tp_pub.publish(data)
        
        
    #elif len(data.Data)>255*7:
        #call extended tp function here
        
    else:  
        write_f.write('S,%X,%d,%d,%d,%s,%s\n'%(data.ID,(data.ID>>16)&0xFF,(data.ID>>8)&0xFF,data.ID&0xFF,str(data.Data.hex(' ')),data.Data))
        rospy.loginfo('Sending message:%X\n'%data.ID)
        send_msg=Message(is_extended_id=True, arbitration_id=data.ID,data=data.Data)
        bus.send(send_msg)
def talker():
    pub = rospy.Publisher('Received_CAN', can_frame, queue_size=10)
    tp_pub=rospy.Publisher('tp_to_send', can_frame, queue_size=10)
    
    rospy.init_node('CAN_monitor', anonymous=True)
    
    message=can_frame()
    
    rospy.Subscriber('CAN_to_send',can_frame,callback,(message,tp_pub))
    
    
    while not rospy.is_shutdown():
        can_msg=bus.recv(0.0)
        if can_msg is not None:
            
            message.ID=can_msg.arbitration_id
            message.Data=can_msg.data
            write_f.write('R,%X,%d,%d,%d,%s,%s\n'%(message.ID,(message.ID>>16)&0xFF,(message.ID>>8)&0xFF,message.ID&0xFF,str(message.Data.hex(' ')),message.Data))
            #rospy.loginfo('Received message:%X\n'%message.ID)
            pub.publish(message)
    rospy.spin()
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
