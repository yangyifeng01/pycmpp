#!/usr/bin/env python
# -*- coding: utf-8 -*-


from cmpp.cmpp import cmpp
import threading
import time

def msg():
    while True:
        b = c.get_recv_msg()
        if b:
            if b['Registered_Delivery'] == 0:
                msg_fmt = {0:'utf-8', 8:'utf-16-be', 15:'gbk'}
                msg_content = b['Msg_Content'].decode(msg_fmt[b['Msg_Fmt']])
                src_id = b['Src_terminal_Id']
                print('%s from %s' % (msg_content,src_id))
        time.sleep(0.5)


if __name__ == '__main__':
    c = cmpp('221.131.129.1',7890, '000000', '000000', '000000000000')
    #c.debug(True)
    c.connectgateway()
    c.connect()
    c.start()
    t = threading.Thread(target=msg)
    t.start()

    for i in range(0,2):
        c.sendmessage(content = '测试一条短信，测试一条短信，测试一条短信，测试一条短信', dest = ['8613900000000',], isdelivery = 1)


#c.sendmessage(content = '测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，测试一条长短信，', dest = '8613900000000')


