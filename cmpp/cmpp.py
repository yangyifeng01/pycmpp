#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import socket
import struct
import queue
import cmppresp
import time
from cmppsend import messageheader, cmppconnect, cmppsubmit, cmppdeliverresp, cmppcancel, cmppactiveresp
import cmppthread
from cmppdefines import CMPP_CONNECT, CMPP_SUBMIT, CMPP_TERMINATE, CMPP_DELIVER_RESP, CMPP_QUERY, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class cmpp:
    """
    
    """

    def __init__(self, 
            gateway='221.131.129.1', 
            port=7890, 
            sp_id='000000', 
            sp_passwd='000000', 
            src_id='0'):
        self.__gateway = gateway
        self.__port = port
        self.__sp_id = sp_id
        self.__sp_passwd = sp_passwd
        self.__src_id = src_id
        self.__sequence_id = 2001
        self.__active_sequence_id = 1
        self.__sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__resp = cmppresp.response()
        self.__debug = False
        self.__send_queue = queue.Queue(50)
        self.__recv_queue = queue.Queue(100)
        self.__recvthread = cmppthread.recvthread(self.recv, self.deliverresp, self.activeresp, self.__recv_queue)
        self.__sendthread = cmppthread.sendthread(self.__sp.send, self.terminate, self.active, self.__send_queue)

    def __del__(self):
        if self.__recvthread.is_alive():
            self.__recvthread.stop()
        if self.__sendthread.is_alive():
            self.__sendthread.stop()
        self.__sp.close()

    def __internal_id(self, seq_type = 1):
        if seq_type == 0:
            if self.__active_sequence_id >= 100:
                self.__avtive_sequence_id = 1
            s = self.__active_sequence_id
            self.__active_sequence_id += 1
        elif seq_type == 1:
            s = self.__sequence_id
            self.__sequence_id += 1
        else:
            s = 0
        return s

    def debug(self, isdebug):
        self.__debug = isdebug

    def start(self):
        self.__sendthread.start()
        self.__recvthread.start()

    def stop(self):
        self.__sendthread.stop()
        self.__recvthread.stop()

    def connectgateway(self):
        try:
            cmppaddr = (self.__gateway, self.__port)
            self.__sp.settimeout(5)
            self.__sp.connect(cmppaddr)
        except socket.error as arg:
            print(arg)
            sys.exit(100)

    def disconnectgateway(self):
        try:
            self.__sp.close()
        except socket.error as arg:
            print(arg)

    def send(self, message):
        if self.__debug == True:
            print(message,len(message))
        else:
            self.__sp.send(message)

    def connect(self):
        mb = cmppconnect(self.__sp_id, self.__sp_passwd)
        mh = messageheader(mb.length(), CMPP_CONNECT, self.__internal_id(seq_type=0))
        try:
            msg =  mh.header() + mb.body()
            if self.__debug == True:
                print(msg,len(msg))
            self.__sp.send(msg)
            h,b = self.recv()
            print(h,b)
            if b['Status']!=0:
                print('connect failed, status: %d' % b['Status'])
                self.__sp.close()
                sys.exit(201)
            else:
                print('connect successfully')
            #self.__send_queue.put(msg_seq)
        except socket.error as arg:
            self.__sp.close()
            print(arg)
            sys.exit(100)

    def normalmessage(self, dest, content, isdelivery = 0):
        mb = cmppsubmit(
                Msg_src = self.__sp_id, 
                Src_Id = self.__src_id, 
                Registered_Delivery = isdelivery, 
                Msg_Content = content, 
                Msg_Length = len(content)*2, 
                DestUsr_tl = len(dest),
                Dest_terminal_Id = dest)
        seq = self.__internal_id()
        mh = messageheader(mb.length(), CMPP_SUBMIT, seq)
        msg = mh.header() + mb.body()
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put((msg, seq))

    def longmessage(self, dest, content, isdelivery = 0):
        tp_udhi = '\x05\x00\x03\x37'
        remain_len = len(content)*2
        times = remain_len // 134
        if remain_len % 134 > 0:
            times += 1
        msg = []
        seq = self.__internal_id()
        for count in range(0, times):

            if remain_len >= 134:
                current_len = 134
            else:
                current_len = remain_len
            remain_len -= 134

            content_header = tp_udhi + \
                    struct.pack('B', times).decode('utf-8') + \
                    struct.pack('B', count+1).decode('utf-8')
            content_slice = content[(0+count*67):(current_len//2+count*67)]

            mb = cmppsubmit(
                    Msg_src = self.__sp_id, 
                    Src_Id = self.__src_id, 
                    Registered_Delivery = isdelivery, 
                    Msg_Header = content_header, 
                    Msg_Content = content_slice, 
                    Msg_Length = current_len + 6, 
                    DestUsr_tl = len(dest),
                    Dest_terminal_Id = dest, 
                    TP_pId = 1,
                    TP_udhi = 1)
            mh = messageheader(mb.length(), CMPP_SUBMIT, seq)
            msg.append(mh.header() + mb.body())
         
        if self.__debug == True:
            print(msg[count],len(msg[count]))
        #self.__sp.send(msg[count])
        self.__send_queue.put((msg, seq))

    def sendmessage(self, dest, content, isdelivery = 0):
        if len(content) <= 70:
            self.normalmessage(dest, content, isdelivery)
        else:
            self.longmessage(dest, content, isdelivery)

    def active(self):
        seq = self.__internal_id(seq_type=0)
        mh = messageheader(0, CMPP_ACTIVE_TEST, seq)
        msg =  mh.header()
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put((msg, seq))

    def terminate(self):
        seq = self.__internal_id(seq_type=0)
        mh = messageheader(0, CMPP_TERMINATE, seq)
        msg =  mh.header()
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put((msg, seq))

    def activeresp(self, sequence_id):
        mb = cmppactiveresp()
        mh = messageheader(mb.length(), CMPP_ACTIVE_TEST_RESP, sequence_id)
        msg = mh.header() + mb.body()
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put((msg, sequence_id))

    def deliverresp(self, Msg_Id, Result, sequence_id):
        mb = cmppdeliverresp(Msg_Id, Result)
        mh = messageheader(mb.length(), CMPP_DELIVER_RESP, sequence_id)
        msg = mh.header() + mb.body()
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put((msg, sequence_id))

    def recv(self):
        if self.__debug == False:
            length = self.__sp.recv(4)
            maxlen,=struct.unpack('!L',length)
            self.__resp.parse(length + self.__sp.recv(maxlen-4))
            mh = self.__resp.parseheader()
            mb = self.__resp.parsebody()
        else:
            mh = mb = {}
        return mh, mb

    def get_recv_msg(self):
        try:
            b = self.__recv_queue.get_nowait()
        except queue.Empty:
            b = None
        return b
