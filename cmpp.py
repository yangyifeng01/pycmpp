#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import socket
import cmppresp
import cmppsend
import cmppthread
import struct
import queue

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
        self.__sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__resp = cmppresp.response()
        self.__send = cmppsend.cmppsend(sp_id, sp_passwd, src_id)
        self.__debug = False
        self.__send_queue = queue.Queue(50)
        self.__send_list = []
        self.__recv_list = []
        self.__recvthread = cmppthread.recvthread(self.recv, self.deliverresp, self.activeresp, self.__send_list, self.__recv_list, 1)
        self.__sendthread = cmppthread.sendthread(self.__sp.send, self.terminate, self.__send_queue, self.__send_list, self.__recv_list)
        self.__contactthread = cmppthread.contactthread(self.active, self.__send_queue, 1)

    def __del__(self):
        if self.__recvthread.is_alive():
            self.__recvthread.stop()
        if self.__sendthread.is_alive():
            self.__sendthread.stop()
        if self.__contactthread.is_alive():
            self.__contactthread.stop()
        self.__sp.close()

    def debug(self, isdebug):
        self.__debug = isdebug

    def start(self):
        self.__sendthread.start()
        self.__recvthread.start()
        self.__contactthread.start()

    def stop(self):
        self.__contactthread.stop()
        self.__sendthread.stop()
        self.__recvthread.stop()

    def connectgateway(self):
        try:
            cmppaddr = (self.__gateway, self.__port)
            self.__sp.settimeout(10)
            self.__sp.connect(cmppaddr)
        except socket.error as arg:
            print(arg)
            sys.exit(0)

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
        msg_seq = self.__send.connect()
        msg = msg_seq[0]
        if self.__debug == True:
            print(msg,len(msg))
        self.__sp.send(msg)
        h,b = self.recv()
        while b['Status']!=0:
            time.sleep(60)
            self.__sp.send(msg)
            h,b = self.recv()
            print('wait for connect')
        print(h,b)
        #self.__send_queue.put(msg_seq)

    def normalmessage(self, dest, content, isdelivery = 1):
        msg_seq = self.__send.normalmessage(dest, content, isdelivery)
        msg = msg_seq[0]
        if self.__debug == True:
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put(msg_seq)

    def longmessage(self, dest, content, isdelivery = 1):
        msg_seq = self.__send.longmessage(dest, content, isdelivery)
        msg = msg_seq[0]
        if self.__debug == True:
            print(msg[count],len(msg[count]))
        #self.__sp.send(msg[count])
        self.__send_queue.put(msg_seq)

    def sendmessage(self, dest, content, isdelivery = 0):
        if len(content) <= 70:
            self.normalmessage(dest, content, isdelivery)
        else:
            self.longmessage(dest, content, isdelivery)

    def active(self):
        msg_seq = self.__send.cmppactive()
        if self.__debug == True:
            msg = msg_seq[0]
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put(msg_seq)

    def terminate(self):
        msg_seq = self.__send.cmppterminate()
        if self.__debug == True:
            msg = msg_seq[0]
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put(msg_seq)

    def activeresp(self, sequence_id):
        msg_seq = self.__send.cmppactiveresp(sequence_id)
        if self.__debug == True:
            msg = msg_seq[0]
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put(msg_seq)

    def deliverresp(self, Msg_Id, Result, sequence_id):
        msg_seq = self.__send.cmppdeliverresp(Msg_Id, Result, sequence_id)
        if self.__debug == True:
            msg = msg_seq[0]
            print(msg,len(msg))
        #self.__sp.send(msg)
        self.__send_queue.put(msg_seq)

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
