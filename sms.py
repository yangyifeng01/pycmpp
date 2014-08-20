#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cmpp

c = cmpp.cmpp('221.131.129.1',7890, '000000', '000000', '000000000000')
#c.debug(True)

c.connectgateway()
c.connect()
c.start()

for i in range(0,10):
    c.sendmessage(content = '测试一条短信，测试一条短信，测试一条短信，测试一条短信', dest = ['8613900000000',], isdelivery = 1)


#c.sendmessage(content = '测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，', dest = '8613900000000')


