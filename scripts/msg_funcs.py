import rospy
def address_claim(pub,message):
    
    #Send our address to the bus
    message.ID=0x18EEFFEC#SA=236 to startwith
    message.Dest=255
    message.Data=b'\x00\x00\xc0\x99\x00\x8b\x01\xa0'
    pub.publish(message)
    
    
def bus_respond(pub,message,data,my_address):
    priority=0
    if len(data.Data)==3:
        req_PGN=int.from_bytes(data.Data,'little')
        sender=data.ID&0xFF
        message.Data=None
        
        
        #This contains the function type of the CF
        if req_PGN==64654:
            priority=6
            message.Data=b'\xff\x01\x07\x01\x00\xff\xff\xff'

        #This contains the diagnostic types supported
        elif req_PGN==64818:
            priority=6
            message.Data=b'\x00\xff\xff\xff\xff\xff\xff\xff'

        #This contains the isobus complaince- says we are not compliant (same as topcon)
        elif req_PGN==64834:
            priority=6
            message.Data=b'\x00\x06\x00\x00\x00\x80\x00\x00'
                   
        #Request for tractor classification and facilities
        elif req_PGN==65033:
            priority=3
            message.Data=b'\x01\xff\xff\xff\xff\x09\xfe\x00'#This is copied from the topcon task controller- look at ISO -7 to change 

        #Required tractor faciities message   
        elif req_PGN==65032:
            priority=3
            message.Data=b'\x00\x06\x00\x00\x00\x90\x00\x00'#This is copied from the topcon task controller- look at ISO -7 to change 
            
        #Active error codes- set to none    
        elif req_PGN==65226:
            priority=3
            message.Data=b'\xff\xff\x00\x00\x00\x00\xff\xff'#This is copied from the topcon task controller- look at ISO -10 to change 

      #Previous error codes- set to none    
        elif req_PGN==65227:
            priority=3
            message.Data=b'\xff\xff\x00\x00\x00\x00\xff\xff'#This is copied from the topcon task controller- look at ISO -10 to change 
            
            
        #product identification
        elif req_PGN==64965:
            message.Data=b'Twyne1*00:00:00:00:00:00*In Cab*Nick Abbey Digital Agriculture*0000*'#zeros should be mac address - find out what it is for the ecu
            
         #ECU identification
        elif req_PGN==64653:
            message.Data=b'Twyne1*Nick Abbey Digital Agriculture*Twyne1*'#Change model name when we have one
               
        #Software Version
        elif req_PGN==65242:
            message.Data=b'\x01*Twyne1 0.0.0'#Change model name when we have one
        
        
        if message.Data!=None:
            message.ID=(priority<<26)+(req_PGN<<8)+my_address
            message.Dest=sender
            pub.publish(message)
            
        
def implement_respond(pub,message,data,my_address,rec_op):
    sender=data.ID&0xFF
    message.Data=None
    priority=0
    #Receive client task message and respond with request version message
    if data.Data==b'\xff\xff\xff\xff\xfe\xff\xff\xff':
        priority=5
        message.Data=b'\x00\xff\xff\xff\xff\xff\xff\xff'
           
    #Receive request version message or the client version message and respond with our version and request the client version
    elif data.Data==b'\x00\xff\xff\xff\xff\xff\xff\xff':# or data.Data[0:1]==b'\x10':
        print('received request version')
        priority=5
        message.Data=(b'\x10\x04\xff\x01\x00\x00\x00\x00')#TC/DL version message
        message.ID=(priority<<26)+(203<<16)+(sender<<8)+my_address
        message.Dest=sender
        pub.publish(message) 
        priority=5
        message.Data=b'\x00\xff\xff\xff\xff\xff\xff\xff'#request version message
        
    #Receive request structure label message and send structure label unavailable in response
    elif data.Data[0]==1:#b'\x01\x34\x90\x42\x0d\x91\x1a\x7b':
        priority=5
        #message.Data=(b'\x11\xff\xff\xff\xff\xff\xff\xff')
        message.Data=b'\x11'+data.Data[1:]
    
    #Receive request localisation and respond with localisation unknown    
    elif data.Data[0:1]==b'\x21':
        priority=5
        message.Data=(b'\x31\xff\xff\xff\xff\xff\xff\xff')

    #Receive request object pool transfer message and respond with request object pool transfer response message
    elif data.Data[0:1]==b'\x41':
        priority=5
        message.Data=(b'\x51\x00\xff\xff\xff\xff\xff\xff')
        rec_op=1
        
    #Receive object pool activate message and respond with object pool activate response message
    elif data.Data==b'\x81\xff\xff\xff\xff\xff\xff\xff':
        priority=5
        message.Data=(b'\x91\x00\xff\xff\xff\xff\x00\xff')
  
    
    if message.Data!=None:
        message.ID=(priority<<26)+(203<<16)+(sender<<8)+my_address
        message.Dest=sender
        pub.publish(message) 
        
    return (rec_op)
