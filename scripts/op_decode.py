import struct


class object_pool:
    def __init__(self,DVC_t,DET_t,DPT_t,DPD_t,DVP_t):
        self.DVC_t=DVC_t
        self.DET_t=DET_t
        self.DPT_t=DPT_t
        self.DPD_t=DPD_t
        self.DVP_t=DVP_t
class DVC:
    def __init__(self,ob_id,txt_name,software,name,serial_num,structure_lab,local_lab,ext_structure_lab):
        self.ob_id=ob_id
        self.txt_name=txt_name
        self.software=software
        self.name=name
        self.serial_num=serial_num
        self.structure_lab=structure_lab
        self.local_lab=local_lab
        self.ext_structure_lab=ext_structure_lab

class DET:
    def __init__(self,ob_id,DE_type,txt_name,DE_num,parent_id,objects):
        self.ob_id=ob_id
        self.DE_type=DE_type
        self.txt_name=txt_name
        self.DE_num=DE_num
        self.parent_id=parent_id
        self.objects=objects
        
class DPT:
    def __init__(self,ob_id,DDI,value,txt_name,presentation_id):
        self.ob_id=ob_id
        self.DDI=DDI
        self.value=value
        self.txt_name=txt_name
        self.presentation_id=presentation_id
        
class DPD:
    def __init__(self,ob_id,DDI,dset,trigger,txt_name,presentation_id):
        self.ob_id=ob_id
        self.DDI=DDI
        self.dset=dset
        self.trigger=trigger
        self.txt_name=txt_name
        self.presentation_id=presentation_id       
class DVP:
    def __init__(self,ob_id,offset,scale,num_dec,unit):
        self.ob_id=ob_id
        self.offset=offset
        self.scale=scale
        self.num_dec=num_dec
        self.unit=unit
        
def pool_decode(pool): 
    array=list()
    data=[]
    DVCs=[]
    DETs=[]
    DPTs=[]
    DPDs=[]
    DVPs=[]
    for i in range(len(pool)):
        if  pool[i:i+3]==b'DVC' or pool[i:i+3]==b'DET' or pool[i:i+3]==b'DPD' or pool[i:i+3]==b'DVP' or pool[i:i+3]==b'DPT':
            array.append(i)

    array.append(len(pool))

    for i in range(len(array)-1):
        data.append(pool[array[i]:array[i+1]])

    for i in range(len(data)):
        #look at page ~54 of section 10
        
        if data[i][0:3]==b'DVC':
            ob_id,len1=struct.unpack('<HB',data[i][3:6])
            txt_name=data[i][6:6+len1].decode('utf-8')
            len2=data[i][6+len1]
            software=data[i][7+len1:7+len1+len2].decode('utf-8')
            name=data[i][7+len1+len2:15+len1+len2]#Same as address call NAME
            len3=data[i][15+len1+len2]
            serial_num=data[i][16+len1+len2:16+len1+len2+len3].decode('utf-8')
            structure_lab=data[i][16+len1+len2+len3:23+len1+len2+len3]
            local_lab=data[i][23+len1+len2+len3:30+len1+len2+len3]
            if len(data[i])>30+len1+len2+len3:
                len4=data[i][30+len1+len2+len3]
                ext_structure_lab=data[i][30+len1+len2+len3:30+len1+len2+len3+len4]
            else:
                ext_structure_lab=None
            DVCs.append(DVC(ob_id,txt_name,software,name,serial_num,structure_lab,local_lab,ext_structure_lab))
        	
        elif data[i][0:3]==b'DET':
            objects=[]
            ob_id,DE_type,len1=struct.unpack('<HBB',data[i][3:7])
            txt_name=data[i][7:7+len1].decode('utf-8')
            DE_num,parent_id,len2=struct.unpack('<HHH',data[i][7+len1:13+len1])
            for j in range(len2): 
                objects.append((struct.unpack('<H',data[i][13+len1+2*j:15+len1+2*j]))[0])
            DETs.append(DET(ob_id,DE_type,txt_name,DE_num,parent_id,objects))	       	
        	
        elif data[i][0:3]==b'DPT':
            ob_id,DDI,value,len1=struct.unpack('<HHlB',data[i][3:12])
            txt_name=data[i][12:12+len1].decode('utf-8')
            presentation_id=(struct.unpack('<H',data[i][12+len1:14+len1]))[0]
            DPTs.append(DPT(ob_id,DDI,value,txt_name,presentation_id))
            
        elif data[i][0:3]==b'DPD':
            ob_id,DDI,dset,trigger,len1=struct.unpack('<HHBBB',data[i][3:10])
            txt_name=data[i][10:10+len1].decode('utf-8')
            presentation_id=(struct.unpack('<H',data[i][10+len1:12+len1]))[0]
            DPDs.append(DPD(ob_id,DDI,dset,trigger,txt_name,presentation_id))
        
        elif data[i][0:3]==b'DVP':
            ob_id,offset,scale,num_dec=struct.unpack('<HlfB',data[i][3:14])
            unit=data[i][15:].decode('utf-8')
            DVPs.append(DVP(ob_id,offset,scale,num_dec,unit))

    op=object_pool(DVCs,DETs,DPTs,DPDs,DVPs)
    
    return op
    

