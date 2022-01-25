
def TP_RTS(message,pub,PF,PS,SA,dest,Data):
    #Send RTS
    
    total_len=int.to_bytes(len(Data),2,'little')
    
    num_packets=int.to_bytes((-(-len(Data)//7)),1,'little')
    
    PGN=int.to_bytes(PS,1,'little')+int.to_bytes(PF,1,'little')+b'\x00'
    
    message.ID=0x1CEC0000+(dest<<8)+SA
    message.Data=b'\x10'+total_len+num_packets+b'\xff'+PGN
    message.Dest=dest
    pub.publish(message)
   
    
    
def TP_data_transfer(message,pub,PF,PS,SA,dest,Data):
    
    ffs=b'\xff\xff\xff\xff\xff\xff\xff\xff'
    if len(Data)%7!=0:
        new_data=Data+ffs[:7-(len(Data)%7)]
    else:
        new_data=Data
    for i in range(-(-len(new_data)//7)):
        message.Data=int.to_bytes((i+1),1,'little')+new_data[i*7:(i+1)*7]
        message.Dest=dest
        message.ID=0x1CEB0000+(dest<<8)+SA
        

        pub.publish(message)
        
        
        
def TP_CTS(pub,message,data,my_address,msg_bytes,msg_packets):
    
    #received an RTS message
    if data.Data[0]==16:
        
        sender=data.ID&0xFF
        msg_bytes=data.Data[1]+(data.Data[2]<<8)
        msg_packets=data.Data[3]
        max_packets=data.Data[4]#per_CTS message
        
        packets_to_send=min(msg_packets,max_packets)
        
        message.ID=0x1CEC0000+(sender<<8)+my_address
        message.Dest=sender
        message.Data=b'\x11'+int.to_bytes(packets_to_send,1,'little')+b'\x01\xff\xff'+data.Data[5:8]
        pub.publish(message)
        
    return msg_bytes,msg_packets
        
def TP_ACK(pub,message,data,my_address,msg_bytes,PGN):

    #Send end of message acknowledgement
    sender=data.ID&0xFF
    message.ID=0x1CEC0000+(sender<<8)+my_address
    message.Dest=sender
    message.Data=b'\x13'+int.to_bytes(msg_bytes,2,'little')+data.Data[0:1]+b'\xff'+PGN
    pub.publish(message)
    
    
    #if PGN==b'\x00\xcb\x00':
        #This is the object pool transfer response bytes3-6 are the size of data received
        #Probably move somewhere else
        #message.ID=0x0CCBEAEC
        #message.Dest=234
        #message.Data=b'q\x00\x93\x06\x00\x00\xff\xff'
        #pub.publish(message) 
    
    
