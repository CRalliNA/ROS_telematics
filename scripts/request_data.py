#!/usr/bin/env python
# license removed for brevity
import rospy,struct
from std_msgs.msg import String
from telematics.msg import can_frame
from op_decode import *
count=0
DE_DDI=[]#list of available Elements and DDIs
obj_pool=None
f=open('/home/charlie/Telemetry/DDIs.txt','w')
def callback(data,args):
    global count,DE_DDI,obj_pool
    
    pub=args[0]
    message=args[1]
    

    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and len(data.Data)>8:#Find a better way to check for the object pool
        obj_pool=pool_decode(data.Data)
        '''print('Elements\n')
        for i in range(len(obj_pool.DET_t)):
            print(obj_pool.DET_t[i].DE_num,obj_pool.DET_t[i].txt_name,obj_pool.DET_t[i].objects)
        print('\nAvailable DDIs\n')
        for i in range(len(obj_pool.DPD_t)):
            print(obj_pool.DPD_t[i].ob_id,obj_pool.DPD_t[i].txt_name,obj_pool.DPD_t[i].DDI, obj_pool.DPD_t[i].trigger)

        print('\nInformation\n')
        for i in range(len(obj_pool.DPT_t)):
            print(obj_pool.DPT_t[i].ob_id,obj_pool.DPT_t[i].txt_name,obj_pool.DPT_t[i].DDI,obj_pool.DPT_t[i].value)
'''
        for i in range(len(obj_pool.DET_t)):
            for j in range(len(obj_pool.DET_t[i].objects)):
                for k in range(len(obj_pool.DPD_t)):
                    if obj_pool.DET_t[i].objects[j]==obj_pool.DPD_t[k].ob_id:
                        #print(obj_pool.DET_t[i].DE_num,obj_pool.DET_t[i].txt_name,obj_pool.DPD_t[k].ob_id,obj_pool.DPD_t[k].txt_name,obj_pool.DPD_t[k].DDI, obj_pool.DPD_t[k].trigger)
                        DE_DDI.append([obj_pool.DET_t[i].DE_num,obj_pool.DPD_t[k].DDI,obj_pool.DPD_t[k].trigger])
    
        print(DE_DDI)
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0:1]==b'\x81':
    #First request here
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00\x8d\x00\x00\x40\x00\x00'
        pub.publish(message) 
        
        
    elif (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13) and count<len(DE_DDI):
        
       
        
        hex_num=struct.pack('<H',DE_DDI[count][1])

        hex_el=int.to_bytes(((DE_DDI[count][0]&0x0F)<<4)+2,1,'little')+int.to_bytes(((DE_DDI[count][0]>>4)&0xFF),1,'little')
        
        print (hex_el)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        
        
        message.Data=hex_el+ hex_num +b'\x00\x00\x00\x00'
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

