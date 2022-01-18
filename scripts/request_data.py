#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from telematics.msg import can_frame
count=0
f=open('/home/charlie/Telemetry/DDIs.txt','w')
def callback(data,args):
    global count
    
    pub=args[0]
    message=args[1]
    
    ddi_list=[67,160,161,205,206,34,1,2,71,72,80,116,158,179,194]
    element_list=[1,1,1,1,1,1,7,7,7,7,7,7,7,7,7]
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0:1]==b'\x81':
    #First request here
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00\x8d\x00\x00\x40\x00\x00'
        pub.publish(message) 
        
        
    elif (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13) and count<15:
        
       
        
        hex_num=int.to_bytes((ddi_list[count]),2,'little')

        hex_el=int.to_bytes((element_list[count]<<4)+2,1,'little')
        print (hex_el)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        
        
        message.Data=hex_el+b'\x00'+ hex_num +b'\x00\x00\x00\x00'
        pub.publish(message)
        count=count+1
    if   (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13):
        f.write('%d, %d, %d, %d, %s\n'%(data.Data[0]&0x0F,(data.Data[0]>>4),data.Data[2]+(data.Data[3]<<8),data.Data[4]+(data.Data[5]<<8) + (data.Data[6]<<16) + (data.Data[7]<<24),data.Data))
    
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

