#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socket
import cmppresp
import cmppsend
import struct

class cmpp:
    """
    the basic class to connect to ISMG
    """

    def __init__(self, 
            gateway='221.131.129.1', 
            port=7890, 
            sp_id='0', 
            sp_passwd='0', 
            src_id='0'):
        self.__gateway = gateway
        self.__port = port
        self.__sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__resp = cmppresp.response()
        self.__send = cmppsend.cmppsend(sp_id, sp_passwd, src_id)
        self.__sequence_id = 1
        self.__debug = False

    def __del__(self):
        self.__sp.close()

    def __internal_id(self):
        s = self.__sequence_id
        self.__sequence_id += 1
        return s

    def debug(self, isdebug):
        self.__debug = isdebug

    def connectgateway(self):
        cmppaddr = (self.__gateway, self.__port)
        self.__sp.connect(cmppaddr)

    def send(self, message):
        if self.__debug == True:
            print(message,len(message))
        self.__sp.send(message)

    def connect(self):
        msg = self.__send.connect(self.__internal_id)
        if self.__debug == True:
            print(msg,len(msg))
        self.__sp.send(msg)

    def normalmessage(self, dest, content, isdelivery = 1):
        msg = self.__send.normalmessage(dest, content, isdelivery, self.__internal_id)
        if self.__debug == True:
            print(msg,len(msg))
        self.__sp.send(msg)

    def longmessage(self, dest, content, isdelivery = 1):
        msg = self.__send.longmessage(dest, content, isdelivery, self.__internal_id)
        print(msg)
        if len(msg) == 1:
            self.normalmessage(dest, content, isdelivery)
        else:
            for count in range(0, len(msg)):
                if self.__debug == True:
                    print(msg[count],len(msg[count]))
                self.__sp.send(msg[count])

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
