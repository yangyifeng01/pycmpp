#!/usr/bin/env python
# -*- coding: utf-8 -*-


import struct
import hashlib
import time
from cmppdefines import CMPP_CONNECT, CMPP_SUBMIT, CMPP_TERMINATE, CMPP_DELIVER_RESP, CMPP_QUERY, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class cmppsend:

    def __init__(self, 
            sp_id = '0', 
            sp_passwd = '0', 
            src_id = '0'):
        self.__sp_id = sp_id
        self.__sp_passwd = sp_passwd
        self.__src_id = src_id
        self.__sequence_id = 1

    def __internal_id(self):
        s = self.__sequence_id
        self.__sequence_id += 1
        return s

    def connect(self):
        mb = cmppconnect(self.__sp_id, self.__sp_passwd)
        mh = messageheader(mb.length(), CMPP_CONNECT, self.__internal_id())
        return mh.header() + mb.body(), mh.sequence_id()

    def normalmessage(self, dest, content, isdelivery):
        mb = cmppsubmit(
                Msg_src = self.__sp_id, 
                Src_Id = self.__src_id, 
                Registered_Delivery = isdelivery, 
                Msg_Content = content, 
                Msg_Length = len(content)*2, 
                Dest_terminal_Id = dest)
        mh = messageheader(mb.length(), CMPP_SUBMIT, self.__internal_id())
        return mh.header() + mb.body(), mh.sequence_id()

    def longmessage(self, dest, content, isdelivery):
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
                    Dest_terminal_Id = dest, 
                    TP_pId = 1,
                    TP_udhi = 1)
            mh = messageheader(mb.length(), CMPP_SUBMIT, seq)
            msg.append(mh.header() + mb.body())
        return msg, mh.sequence_id()

    def cmppdeliverresp(self, Msg_Id, Result, sequence_id):
        mb = cmppdeliverresp(Msg_Id, Result)
        mh = messageheader(mb.length(), CMPP_DELIVER_RESP, sequence_id)
        return mh.header() + mb.body(), mh.sequence_id()

    def cmppactiveresp(self, sequence_id):
        mb = cmppactiveresp()
        mh = messageheader(mb.length(), CMPP_ACTIVE_TEST_RESP, sequence_id)
        return mh.header() + mb.body(), mh.sequence_id()

    def cmppactive(self):
        mh = messageheader(0, CMPP_ACTIVE_TEST, self.__internal_id())
        return mh.header(), mh.sequence_id()

    def cmppterminate(self):
        mh = messageheader(0, CMPP_TERMINATE, self.__internal_id())
        return mh.header(), mh.sequence_id()

class messageheader:
    """
    the common message header
    """
    def __init__(self, messagebodylength=0, command_id = b'', seq = 0):
        self.__total_length = struct.pack('!L', 12+messagebodylength)
        self.__command_id = struct.pack('!L', command_id)
        self.__sequence_id = struct.pack('!L', seq)
        self.__sid = seq

    def header(self):
        return self.__total_length + self.__command_id + self.__sequence_id

    def total_length(self):
        return self.__total_length

    def command_id(self):
        return self.__command_id

    def sequence_id(self):
        return self.__sid

def get_numtime():
    """
    get the currenttime with the number style
    """
    return int(time.strftime('%m%d%H%M%S',time.localtime(time.time())))

def get_strtime():
    """
    get the currenttime with a string style
    """
    return time.strftime('%m%d%H%M%S',time.localtime(time.time()))

class cmppconnect:
    """
    create a connection to ISMG on application layer
    """
    def __init__(self, sp_id='000000', sp_passwd='000000'):
        self.__sourceaddr = sp_id.encode('utf-8')
        self.__password = sp_passwd.encode('utf-8')
        self.__version = struct.pack('!B', 0x21)
        self.__timestamp = struct.pack('!L',get_numtime())
        authenticatorsource = self.__sourceaddr + 9*b'\x00' + \
                self.__password + get_strtime().encode('utf-8')
        self.__md5 = hashlib.md5(authenticatorsource).digest()
        self.__length = 27
        self.__body = self.__sourceaddr + \
                self.__md5 + \
                self.__version + \
                self.__timestamp

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppsubmit:
    """
    submit short message to ISMG
    """
    def __init__(self,
            Pk_total = 1,
            Pk_number = 1,
            Registered_Delivery = 0,
            Msg_level = 0,
            Service_Id = 'MJS0019905',
            Fee_UserType = 2,
            Fee_terminal_Id = 0,
            TP_pId = 0,
            TP_udhi = 0,
            Msg_Fmt = 8,
            Msg_src = '000000',
            FeeType = '01',
            FeeCode = '000000',
            ValId_Time = 17*'\x00',
            At_Time = 17*'\x00',
            Src_Id = '000000000000',
            DestUsr_tl = 1,
            Dest_terminal_Id = '8613900000000',
            Msg_Length = 4,
            Msg_Header = '',
            Msg_Content = 'test'):
        self.__Msg_Id = 8*b'\x00'
        self.__Pk_total = struct.pack('!B', Pk_total)
        self.__Pk_number = struct.pack('!B', Pk_number)
        self.__Registered_Delivery = struct.pack('!B',Registered_Delivery)
        self.__Msg_level = struct.pack('!B',Msg_level)
        self.__Service_Id = Service_Id.encode('utf-8')
        self.__Fee_UserType = struct.pack('!B',Fee_UserType)
        self.__Fee_terminal_Id = ('%021d' % Fee_terminal_Id).encode('utf-8')
        self.__TP_pId =  struct.pack('!B', TP_pId)
        self.__TP_udhi = struct.pack('!B', TP_udhi)
        self.__Msg_Fmt = struct.pack('!B', Msg_Fmt)
        self.__Msg_src = Msg_src.encode('utf-8')
        self.__FeeType = FeeType.encode('utf-8')
        self.__FeeCode = FeeCode.encode('utf-8')
        self.__ValId_Time = ValId_Time.encode('utf-8')
        self.__At_Time = At_Time.encode('utf-8')
        self.__Src_Id = (Src_Id + (21-len(Src_Id)) * '\x00').encode('utf-8')
        self.__DestUsr_tl = struct.pack('!B', DestUsr_tl)
        self.__Dest_terminal_Id = (Dest_terminal_Id+8*'\x00').encode('utf-8')
        self.__Msg_Length = struct.pack('!B', Msg_Length)
        self.__Msg_Header = Msg_Header.encode('utf-8')
        self.__Msg_Content = Msg_Content.encode('utf-16-be')
        self.__Reserve = 8*b'\x00'
        self.__length = 126 + 21 * DestUsr_tl + Msg_Length
        self.__body = self.__Msg_Id + \
                self.__Pk_total + self.__Pk_number + \
                self.__Registered_Delivery + \
                self.__Msg_level + \
                self.__Service_Id + \
                self.__Fee_UserType + self.__Fee_terminal_Id + \
                self.__TP_pId + self.__TP_udhi + \
                self.__Msg_Fmt + self.__Msg_src + \
                self.__FeeType + self.__FeeCode + \
                self.__ValId_Time + self.__At_Time + \
                self.__Src_Id + self.__DestUsr_tl + \
                self.__Dest_terminal_Id + self.__Msg_Length + \
                self.__Msg_Header + \
                self.__Msg_Content + \
                self.__Reserve

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppquery:

    def __init__(self, 
            Time = '20140806', 
            Query_Type = 1, 
            Query_Code = '0000000000'):
        self.__Time = Time.encode('utf-8')
        self.__Query_Type = struct.pack('!B', Query_Type)
        self.__Query_Code = Query_Code.encode('utf-8')
        self.__Reserve = 8*b'\x00'
        self.__length = 27
        self.__body = self.__Time + \
                self.__Query_Type + \
                self.__Query_Code + \
                self.__Reserve

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppdeliverresp:

    def __init__(self, Msg_Id, Result = 0):
        self.__Msg_Id = struct.pack('!Q',Msg_Id)
        self.__Result = struct.pack('!B',Result)
        self.__length = 9
        self.__body = self.__Msg_Id + self.__Result

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppcancel:

    def __init__(self, Msg_Id):
        self.__Msg_Id = Msg_Id
        self.__length = 8
        self.__body = self.__Msg_Id

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppactiveresp:

    def __init__(self):
        self.__Reserved = b'\x00'
        self.__length = 1
        self.__body = self.__Reserved

    def body(self):
        return self.__body

    def length(self):
        return self.__length

