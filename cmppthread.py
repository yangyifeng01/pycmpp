#!/bin/usr/env python
# -*- coding: utf-8 -*-

import queue
import time
import threading
import socket
from cmppdefines import CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_DELIVER, CMPP_TERMINATE_RESP, CMPP_QUERY_RESP, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class resendbox(threading.Thread):

    def __init__(self, send, terminate, send_list, recv_list, interval = 1, T = 30, N = 3):
        threading.Thread.__init__(self)
        self.__resend_list = []
        self.__send = send
        self.__send_list = send_list
        self.__recv_list = recv_list
        self.__count = 0
        self.__interval = interval
        self.__T = T
        self.__N = N - 1
        self.__thread_stop = False
        self.__terminate = terminate


    def run(self):
        while not self.__thread_stop:
            self.__count += 1

            for sid in self.__recv_list:
                if sid in self.__send_list:
                    self.__send_list.remove(sid)

            for resend in self.__resend_list:
                if resend['seq'] in self.__send_list:
                    if (self.__count - resend['count']) > self.__T:
                        if resend['N'] == 0:
                            self.__terminate()
                        else:
                            self.__send(resend['msg'])
                            resend['N'] -= 1
                            resend['count'] = self.__count
                else:
                    self.__resend_list.remove(resend)


            #print(self.__resend_list)
            time.sleep(self.__interval)
        return

    def append(self,seq, msg):
        self.__resend_list.append({'seq': seq,
            'msg': msg, 'count': self.__count, 'N': self.__N})

    def stop(self):
        self.__thread_stop = True

class recvthread(threading.Thread):

    def __init__(self, recv, deliverresp, activeresp, send_list, recv_list, interval = 0):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__thread_stop = False
        self.__recv = recv
        self.__send_list = send_list
        self.__recv_list = recv_list
        self.__deliverresp = deliverresp
        self.__activeresp = activeresp

    def run(self):
        print('recv thread start')
        while not self.__thread_stop:
            try:
                h,b = self.__recv()
                print(h,b)
                if h['command_id'] in (CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_QUERY_RESP, CMPP_ACTIVE_TEST_RESP, CMPP_TERMINATE_RESP):
                    self.__recv_list.append(h['sequence_id'])
                elif h['command_id'] == CMPP_DELIVER:
                    self.__deliverresp(b['Msg_Id'], 0, h['sequence_id'])
                    self.__recv_list.append(h['sequence_id'])
                elif h['command_id'] == CMPP_ACTIVE_TEST:
                    self.__activeresp(h['sequence_id'])
                    self.__recv_list.append(h['sequence_id'])

            except socket.error as arg:
                print(arg)
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True


class sendthread(threading.Thread):

    def __init__(self, send, terminate, send_queue, send_list, recv_list, interval = 1):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__thread_stop = False
        self.__send = send
        self.__send_queue = send_queue
        self.__send_list = send_list
        self.__resendbox = resendbox(send, terminate, send_list, recv_list)

    def run(self):
        print('send thread start')
        self.__resendbox.start()
        while not self.__thread_stop:
            try:
                if len(self.__send_list) <16:
                    msg,seq = self.__send_queue.get()
                    if type(msg) == type([]):
                        for index in range(0,len(msg)):
                            self.__send(msg[index])
                    else:
                        self.__send(msg)
                    self.__send_list.append(seq)
                    self.__resendbox.append(seq, msg)

                    print(self.__send_list)
                else:
                    time.sleep(self.__interval)
            except socket.error as arg:
                print(arg)
        return

    def stop(self):
        self.__resendbox.stop()
        self.__thread_stop = True

class contactthread(threading.Thread):

    def __init__(self, active, send_queue, interval=1, C=30):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__thread_stop = False
        self.__send_queue = send_queue
        self.__active = active
        self.__C = C

    def run(self):
        print('contact thread start')
        count = 0
        while not self.__thread_stop:
            if count < (self.__C*2):
                if self.__send_queue.qsize() != 0:
                    count = 0
                else:
                    count += 1
            else:
                self.__active()
                count = 0
            #print('idle:%d' % count)
            time.sleep(self.__interval/2)
        return

    def stop(self):
        self.__thread_stop = True

