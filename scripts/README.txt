README - keep updated with whats in the telematics folder

CAN_monitor
-  Sits on the can bus
-  When it receives a ros message it forwards to the bus
-  When it receives a can message it forwards to ROS

tp_sender
-  if the message a node is trying to send is too long for one byte, this node organises sending via transport protocol

tp_receiver
-  organises receiveing long messages over transport protocol
-  pieces together the different pacjets

tp_func
-  functions to help with tp_sender and tp_receiver

bus_manager
- organises sending the correct messages (handshakes) to be allowed on the bus
- responds to the on board diagnositics and the implement

msg_funcs
- support functions for bus manager

tc_status
-  sends the tc status every 2s starting 6s afterthe address claim


op_decode
- function that decodes the tc object pool

request_data
- requests data from the implement- might change




talker + listener - just exampes to use as a base for new nodes
