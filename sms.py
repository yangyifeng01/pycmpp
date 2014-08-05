#!/usr/bin/env python


import cmpp
from cmppdefines import CMPP_CONNECT, CMPP_SUBMIT, CMPP_DELIVER
import cmppresp

#connect to the ISMG
c = cmpp.cmpp('221.131.129.1',7890)
c.connect()

#create a connection on application layer
mb = cmpp.cmppconnect(sp_id='000000',sp_passwd='000000')
mh = cmpp.messageheader(mb.length(), CMPP_CONNECT, 1)

c.send(mh.header()+mb.body())
#get response from ISMG
resp = cmppresp.connectresp()
h,b = c.recv(resp)
print(h,b)

#submit short message to ISMG
mb = cmpp.cmppsubmit(Msg_src='000000', Src_Id = '000000000000',Registered_Delivery = 1, Msg_Content = 'test', Msg_length = 4, Dest_terminal_Id = '8613900000000')
mh = cmpp.messageheader(mb.length(), CMPP_SUBMIT, 2)

c.send(mh.header()+mb.body())

#get response from ISMG
resp = cmppresp.submitresp()
h,b = c.recv(resp)
print(h,b)


#get response from ISMG
resp = cmppresp.deliver()
h,b = c.recv(resp)
print(h,b)

