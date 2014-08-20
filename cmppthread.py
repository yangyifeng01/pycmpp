#!/bin/usr/env python
# -*- coding: utf-8 -*-

import queue
import time
import threading
import socket
from cmppdefines import CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_DELIVER, CMPP_TERMINATE_RESP, CMPP_QUERY_RESP, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class resendbox(threading.Thread):

    def __init__(self, terminate, send_queue, send_list, interval = 1, T = 60, N = 3):
        threading.Thread.__init__(self)
        self.__resend_box = []
        self.__send_queue = send_queue
        self.__send_list = send_list
        self.__terminate = terminate
        self.__interval = interval
        self.__T = T
        self.__N = N - 1
        self.__count = 0
        self.__thread_stop = False

    def run(self):
        while not self.__thread_stop:
            self.__count += 1

            for resend in self.__resend_box:
                if resend['seq'] in self.__send_list:
                    if (self.__count - resend['count']) > self.__T:
                        if resend['N'] == 0:
                            self.__terminate()
                        else:
                            self.__send_list.remove(resend['seq'])
                            self.__send_queue.put((resend['msg'],resend['seq']))
                            resend['N'] -= 1
                            resend['count'] = self.__count
                else:
                    self.__resend_box.remove(resend)

            if self.__count >= 604800:
                for resend in self.__resend_box:
                    sec = self.__count - resend['count']
                    resend['count'] = self.__T - sec
                self.__count = self.__T

            #print(self.__resend_box)
            time.sleep(self.__interval)
        return

    def append(self,seq, msg):
        self.__resend_box.append({'seq': seq,
            'msg': msg, 'count': self.__count, 'N': self.__N})

    def stop(self):
        self.__thread_stop = True

class scavenger(threading.Thread):

    def __init__(self, send_list, recv_list, interval = 0.5):
        threading.Thread.__init__(self)
        self.__send_list = send_list
        self.__recv_list = recv_list
        self.__interval = interval
        self.__thread_stop = False

    def run(self):
        while not self.__thread_stop:

            for sid in self.__recv_list:
                if sid in self.__send_list:
                    self.__send_list.remove(sid)

            #print(self.__resend_box)
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True

class heartbeat(threading.Thread):

    def __init__(self, active, send_queue, interval=0.5, C=30):
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
            if count < (self.__C/self.__interval):
                if self.__send_queue.qsize() != 0:
                    count = 0
                else:
                    count += 1
            else:
                self.__active()
                count = 0
            #print('idle:%d' % count)
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True

class recvthread(threading.Thread):

    def __init__(self, recv, deliverresp, activeresp, send_list, recv_list, interval = 0):
        threading.Thread.__init__(self)
        self.__recv = recv
        self.__send_list = send_list
        self.__recv_list = recv_list
        self.__deliverresp = deliverresp
        self.__activeresp = activeresp
        self.__interval = interval
        self.__thread_stop = False

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
                else:
                    print('unknown command : %d' % h['command_id'])

            except socket.error as arg:
                pass
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True


class sendthread(threading.Thread):

    def __init__(self, send, terminate, active, send_queue, send_list, recv_list, interval = 0, rate = 15, C=40, T=60, N=3):
        threading.Thread.__init__(self)
        self.__interval = interval
        self.__send = send
        self.__send_queue = send_queue
        self.__send_list = send_list
        self.__heartbeat = heartbeat(active, send_queue, 0.5, C)
        self.__scavenger = scavenger(send_list, recv_list)
        self.__resendbox = resendbox(terminate, send_queue, send_list, 1, T, N)
        self.__rate = rate
        self.__thread_stop = False

    def run(self):
        print('send thread start')
        self.__resendbox.setDaemon(True)
        self.__scavenger.setDaemon(True)
        self.__heartbeat.setDaemon(True)
        self.__resendbox.start()
        self.__scavenger.start()
        self.__heartbeat.start()
        sendstate = True
        while not self.__thread_stop:
            try:
                if len(self.__send_list) < self.__rate and sendstate:
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
                    if len(self.__send_list) > 0:
                        sendstate = False
                    else:
                        sendstate = True
                        time.sleep(self.__interval)

            except socket.error as arg:
                print(arg)
                time.sleep(1)
        return

    def stop(self):
        self.__scavenger.stop()
        self.__resendbox.stop()
        self.__heartbeat.stop()
        self.__thread_stop = True



