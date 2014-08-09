#!/bin/usr/env python


import queue
import time
import threading
import cmpp
from cmppdefines import CMPP_CONNECT, CMPP_SUBMIT, CMPP_DELIVER, CMPP_QUERY
import cmppresp

class CMPPThread(threading.Thread):

    def __init__(self, num, interval):
        threading.Thread.__init__(self)
        self.__thread_num = num
        self.__interval = interval
        self.__thread_stop = False

    def run(self):
        while not self.__thread_stop:
            print('thread %d, time %s' % (self.__thread_num, time.ctime()))
            time.sleep(self.__interval)
        return

    def stop(self):
        self.__thread_stop = True


def test():
    thread1 = timer(1, 1)
    thread2 = timer(2, 2)
    thread1.start()
    thread2.start()
    time.sleep(10)
    thread1.stop()
    thread2.stop()

if __name__ =='__main__':
    test()
