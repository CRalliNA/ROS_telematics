#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from telematics.msg import can_frame


def callback(data,args):
    pub=args[0]
    message=args[1]
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0]==129:
    #Test requests for stuff here
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00\x8d\x00\x00\x00\x00\x00'
        pub.publish(message) 
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x08\x00\x8d\x00\x01\x00\x00\x00'
        pub.publish(message) 
        rospy.sleep(0.1)

        for i in range(1):
            message.ID=(3<<26)+(203<<16)+(234<<8)+236
            message.Dest=234
            message.Data=b'\x02\x00'+ int.to_bytes(1,2,'little')+b'\x00\x40\x00\x00'
            pub.publish(message) 
            rospy.sleep(0.02)
           
        
    if (data.ID>>16)&0xFF==234  and data.Data==b'\xca\xfe\x00' and ((data.ID>>8)&0xFF==234 or (data.ID>>8)&0xFF==236):
        rospy.sleep(0.3)
        for i in range(1):
            message.ID=0x0CCBFFEC
            message.Dest=255
            message.Data=b'\xfe\xff\xff\xff\x00\x00\x00\x00'
            pub.publish(message) 
            rospy.sleep(0.1)
              
              
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0]&0x0F==3:
        print('Process Data Message from %d:\nDDI:%d\n:Value:%d'%(data.ID&0xFF,(data.Data[2]+(data.Data[3]<<8)),(data.Data[4]+(data.Data[5]<<8)+(data.Data[6]<<16)+(data.Data[7]<<24))))
def talker():
    pub = rospy.Publisher('CAN_to_send', can_frame, queue_size=10)
    rospy.init_node('talker', anonymous=True)

    message=can_frame()
    
    #for i in range(5):
    #    message.ID=0x0CCBFFEC
    #    message.Dest=255
    #    message.Data=b'\xfe\xff\xff\xff\x00\x00\x00\x00'
    #    pub.publish(message) 
    #    rospy.sleep(0.1)
    rospy.Subscriber('Received_CAN',can_frame,callback,(pub,message))
    rospy.spin()
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

