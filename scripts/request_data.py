#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from telematics.msg import can_frame
hex_num =b'\x01\x00'
f=open('/home/charlie/Telemetry/DDIs.txt','w')
def callback(data,args):
    global hex_num
    
    pub=args[0]
    message=args[1]
    
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0:1]==b'\x81':
    #First request here
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00\x8d\x00\x00\x40\x00\x00'
        pub.publish(message) 
        
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00'+ int.to_bytes(1,2,'little')+b'\x00\x40\x00\x00'
        pub.publish(message) 
    #Subsequent requests here
    
    elif (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13) and data.Data[2:4]==hex_num and hex_num[1]<=255:
        
        dec_num=hex_num[0]+(hex_num[1]<<8)
        
        hex_num=int.to_bytes((dec_num+1),2,'little')

        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00'+ hex_num +b'\x00\x40\x00\x00'
        pub.publish(message)
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0]&0x0F==3:
        f.write('%d,  %s\n'%(data.Data[2]+(data.Data[3]<<8),data.Data))
        
    
def talker():
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    rospy.init_node('request_data', anonymous=True)

    message=can_frame()
    
    
   
    rospy.Subscriber('Received_CAN',can_frame,callback,(pub,message))
    rospy.spin()
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

