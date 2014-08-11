#!/bin/usr/env python


import queue
import time
import threading
import socket
from cmppdefines import CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_DELIVER, CMPP_QUERY_RESP, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class recvthread(threading.Thread):

    def __init__(self ,recv , deliverresp, activeresp, seq_list, interval = 0):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__thread_stop = False
        self.__recv = recv
        self.__seq_list = seq_list
        self.__deliverresp = deliverresp
        self.__activeresp = activeresp

    def run(self):
        print('recv thread start')
        while not self.__thread_stop:
            try:
                h,b = self.__recv()
                print(h,b)
                if h['command_id'] in (CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_QUERY_RESP, CMPP_ACTIVE_TEST_RESP):
                    self.__seq_list.remove(h['sequence_id'])
                elif h['command_id'] == CMPP_DELIVER:
                    self.__deliverresp(b['Msg_Id'], 0, h['sequence_id'])
                elif h['command_id'] == CMPP_ACTIVE_TEST:
                    self.__activeresp(h['sequence_id'])

            except socket.error as arg:
                print(arg)
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True


class sendthread(threading.Thread):

    def __init__(self, send, send_queue, seq_list, interval=0,internal=0, C=180, T=60, N=3):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__thread_stop = False
        self.__send = send
        self.__send_queue = send_queue
        self.__seq_list = seq_list

    def run(self):
        print('send thread start')
        while not self.__thread_stop:
            try:
#                while len(self.__seq_list) >=16:
#                    time.sleep(self.__interval)
                msg,seq = self.__send_queue.get()
                self.__send(msg)
                self.__seq_list.append(seq)
                print(self.__seq_list)
            except socket.error as arg:
                print(arg)
        return

    def stop(self):
        self.__thread_stop = True

