#!/usr/bin/env python
# license removed for brevity
import rospy,struct
from std_msgs.msg import Int32
from telematics.msg import can_frame
from op_decode import *
count=0
DE_DDI=[]#list of available Elements and DDIs
obj_pool=None
receiving_op=0

f=open('/home/charlie/Telemetry/DDIs.csv','w')
f.write('valid(3),Element Number,DDI,Information')
g=open('/home/charlie/Telemetry/fixed_info.csv','w')
g.write('Object id, DDI, Information')
def callback(data,args):
    global count,DE_DDI,obj_pool
    
    pub=args[0]
    message=args[1]
    

    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and len(data.Data)>8 and b'DVC' in data.Data[0:10]:#Scans messages for the object pool arriving
    #Find a better way to check for the object pool
        obj_pool=pool_decode(data.Data)
        
        for i in range(len(obj_pool.DET_t)):#Creates an array (DE_DDI) of all the DDI messages we are allowed to ask for and all the info required to do so 
            for j in range(len(obj_pool.DET_t[i].objects)):
                for k in range(len(obj_pool.DPD_t)):
                    if obj_pool.DET_t[i].objects[j]==obj_pool.DPD_t[k].ob_id:
                        
                        DE_DDI.append([obj_pool.DET_t[i].DE_num,obj_pool.DPD_t[k].DDI,obj_pool.DPD_t[k].trigger])
    
        print(DE_DDI)
    
    
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and data.Data[0:1]==b'\x81':#Receives the object pool activated messages and sends first message
    #First request here
        rospy.sleep(0.1)
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=b'\x02\x00\x8d\x00\x00\x00\x00\x00'
        pub.publish(message) 
        
        
    elif (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13)  and count<len(DE_DDI):#Receives response to prev message and sends the nect one
        print(count, len(DE_DDI),DE_DDI[count][1])
        if  DE_DDI[count][1] == 57343:#version 4 doesn't seem to like this message , so we skip it
            count=count+1
            
        trig=2
        value=0
       
        #Puts the info from the DE_DDI array into message format
        hex_num=struct.pack('<H',DE_DDI[count][1])
        hex_el1=int.to_bytes(((DE_DDI[count][0]&0x0F)<<4)+trig,1,'little')+int.to_bytes(((DE_DDI[count][0]>>4)&0xFF),1,'little')
        
        #sends a message with command 2- respond once
        message.ID=(3<<26)+(203<<16)+(234<<8)+236
        message.Dest=234
        message.Data=hex_el1+ hex_num +int.to_bytes(value,4,'little')
        pub.publish(message)


        
        if DE_DDI[count][2]%2==1:#checks if we can request DDI based on time
            trig=4
            value=1000
        
        elif DE_DDI[count][2]&8==1:#checks if we can request DDI based on change
            trig=8
            value=1   
        
        #Sends request for DDI every second or when the value changes (depending on what it allows (above))
        rospy.sleep(0.1)
        hex_el2=int.to_bytes(((DE_DDI[count][0]&0x0F)<<4)+trig,1,'little')+int.to_bytes(((DE_DDI[count][0]>>4)&0xFF),1,'little')
        message.Data=hex_el2+ hex_num +int.to_bytes(value,4,'little')
        pub.publish(message)
        count=count+1
     

    #This section is for outputting the data into a file- change to real time at soem point    
    if (data.ID>>16)&0xFF==203  and (data.ID>>8)&0xFF==236 and (data.Data[0]&0x0F==3 or data.Data[0]&0x0F==13):
        dpd_num=0
        det_num=0
        dvp_num=0
        for i in range (len(obj_pool.DET_t)):#matches up element numbers with their names from the object pool
            if obj_pool.DET_t[i].DE_num==(data.Data[0]>>4)+(data.Data[1]<<4):
                det_num=i
        for i in range (len(obj_pool.DPD_t)):#matches up process data messages with their description from the object pool
            if obj_pool.DPD_t[i].DDI==data.Data[2]+(data.Data[3]<<8):
                dpd_num=i
        for i in range (len(obj_pool.DVP_t)):#matches up process data messages with theirscale, offset and units from the object pool
            if obj_pool.DVP_t[i].ob_id==obj_pool.DPD_t[dpd_num].presentation_id:
                dvp_num=i
                
        #writes to csv 
        f.write('\n%d, %d, %d, %s:%s = %d%s'%(data.Data[0]&0x0F,(data.Data[0]>>4)+(data.Data[1]<<4),data.Data[2]+(data.Data[3]<<8), obj_pool.DET_t[det_num].txt_name, obj_pool.DPD_t[dpd_num].txt_name, (struct.unpack('<l',data.Data[4:8])[0] * obj_pool.DVP_t[dvp_num].scale) + obj_pool.DVP_t[dvp_num].offset, obj_pool.DVP_t[dvp_num].unit))
        
        print('%d, %d, %d, %s:%s = %d%s\n'%(data.Data[0]&0x0F,(data.Data[0]>>4)+(data.Data[1]<<4),data.Data[2]+(data.Data[3]<<8),obj_pool.DET_t[det_num].txt_name,obj_pool.DPD_t[dpd_num].txt_name, (struct.unpack('<l',data.Data[4:8])[0] * obj_pool.DVP_t[dvp_num].scale) + obj_pool.DVP_t[dvp_num].offset, obj_pool.DVP_t[dvp_num].unit))







#standard rospy stuff
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

