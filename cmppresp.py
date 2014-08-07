#!/usr/bin/env python

import struct
from cmppdefines import CMPP_CONNECT_RESP, CMPP_SUBMIT_RESP, CMPP_DELIVER, CMPP_DELIVER, CMPP_QUERY_RESP, CMPP_CANCEL_RESP, CMPP_ACTIVE_TEST, CMPP_ACTIVE_TEST_RESP

class response:

    def __init__(self):
        self.__header = b''
        self.__body = b''
        self.__length = 12
        self.__bodylen = 0
        self.__command_id = 0
        self.__sequence_id = 0
        self.__resp_obj = {
                CMPP_CONNECT_RESP: connectresp,
                CMPP_SUBMIT_RESP: submitresp,
                CMPP_DELIVER: deliver,
                CMPP_QUERY_RESP: queryresp,
                CMPP_CANCEL_RESP: cancelresp,
                CMPP_ACTIVE_TEST: activetest,
                CMPP_ACTIVE_TEST_RESP: nothingresp
                }

    def parse(self,info):
        self.__length, = struct.unpack('!L', info[0:4])
        self.__header = info[0:12]
        self.__body = info[12:self.__length]
        self.__command_id, = struct.unpack('!L',info[4:8])
        self.__sequence_id, = struct.unpack('!L',info[8:12])

    def parseheader(self):
        return {'length': self.__length,
                'command_id': self.__command_id,
                'sequence_id': self.__sequence_id}

    def parsebody(self):
        resp = self.__resp_obj[self.__command_id]()
        return resp.parse(self.__body)
        #return resp.parse(self.__body)


class connectresp:
    
    def __init__(self):
        self.__Status = 5
        self.__AuthenticatorISMG = b''
        self.__Version = 0


    def parse(self, body):
        self.__Status, = struct.unpack('!B', body[0:1])
        self.__AuthenticatorISMG = body[1:17]
        self.__Version, = struct.unpack('!B', body[17:18])
        return {'Status': self.__Status,
                'AuthenticatorISMG': self.__AuthenticatorISMG,
                'Version': self.__Version
                }

class submitresp:

    def __init__(self):
        self.__Msg_Id = b''
        self.__Result = 0

    def parse(self, body):
        self.__Status = body[0:8]
        self.__Result, = struct.unpack('!B', body[8:9])
        return {'Status': self.__Status,
                'Result': self.__Result
                }

class queryresp:

    def __init__(self):
        self.__Time = b''
        self.__Query_Type = 0
        self.__Query_Code = b''
        self.__MT_TLMsg = 0
        self.__MT_Tlusr = 0
        self.__MT_Scs = 0
        self.__MT_WT = 0
        self.__MT_FL = 0
        self.__MO_Scs = 0
        self.__MO_WT = 0
        self.__MO_FL = 0

    def parse(self, body):
        self.__Time = body[0:8]
        self.__Query_Type = struct.unpack('!B', body[8:9])
        self.__Query_Code = body[9:19]
        self.__MT_TLMsg = struct.unpack('!L', body[19:23])
        self.__MT_Tlusr = struct.unpack('!L', body[23:27])
        self.__MT_Scs = struct.unpack('!L', body[27:31])
        self.__MT_WT = struct.unpack('!L', body[31:35])
        self.__MT_FL = struct.unpack('!L', body[35:39])
        self.__MO_Scs = struct.unpack('!L', body[39:43])
        self.__MO_WT = struct.unpack('!L', body[43:47])
        self.__MO_FL = struct.unpack('!L', body[47:51])
        return {'Time': self.__Time,
                'Query_Type': self.__Query_Type,
                'Query_Code': self.__Query_Code,
                'MT_TLMsg': self.__MT_TLMsg,
                'MT_Tlusr': self.__MT_Tlusr,
                'MT_Scs': self.__MT_Scs,
                'MT_WT': self.__MT_WT,
                'MT_FL': self.__MT_FL,
                'MO_Scs': self.__MO_Scs,
                'MO_WT': self.__MO_WT,
                'MO_FL': self.__MO_FL
                }


class msgcontent:

    def __init__(self):
        self.__Msg_Id = 0
        self.__Stat = ''
        self.__Submit_time = ''
        self.__Done_time = ''
        self.__Dest_terminal_Id = ''
        self.__SMSC_sequence = 0
        self.__myself = {}

    def parse(self, body):
        self.__Msg_Id = struct.unpack('!Q',body[0:8])
        self.__Stat = body[8:15]
        self.__Submit_time = body[15:25]
        self.__Done_time = body[25:35]
        self.__Dest_terminal_Id = body[35:56]
        self.__SMSC_sequence = struct.unpack('!L',body[56:60])
        self.__myself = {'Msg_Id': self.__Msg_Id,
                'Stat': self.__Stat,
                'Submit_time': self.__Submit_time,
                'Done_time': self.__Done_time,
                'Dest_terminal_Id': self.__Dest_terminal_Id,
                'SMSC_sequence': self.__SMSC_sequence
                }
    def value(self):
        return self.__myself

class deliver:

    def __init__(self):
        self.__Msg_Id = 0
        self.__Dest_Id = b''
        self.__Service_Id = b''
        self.__TP_pid = 0
        self.__TP_udhi = 0
        self.__Msg_Fmt = 0
        self.__Src_terminal_Id = b''
        self.__Registered_Delivery = 0
        self.__Msg_Length = 0
        self.__Msg_Content = msgcontent()

    def parse(self, body):
        self.__Msg_Id, = struct.unpack('!Q', body[0:8])
        self.__Dest_Id = body[8:29]
        self.__Service_Id = body[29:39]
        self.__TP_pid, = struct.unpack('!B', body[39:40])
        self.__TP_udhi, = struct.unpack('!B', body[40:41])
        self.__Msg_Fmt, = struct.unpack('!B', body[41:42])
        self.__Src_terminal_Id = body[42:63]
        self.__Registered_Delivery, = struct.unpack('!B', body[63:64])
        self.__Msg_Length, = struct.unpack('!B', body[64:65])
        self.__Msg_Content.parse(body[65:self.__Msg_Length+65])
        return {'Msg_Id' : self.__Msg_Id,
                'Dest_Id' : self.__Dest_Id,
                'Service_Id' : self.__Service_Id,
                'TP_pid' : self.__TP_pid,
                'TP_udhi' : self.__TP_udhi,
                'Msg_Fmt' : self.__Msg_Fmt,
                'Src_terminal_Id' : self.__Src_terminal_Id,
                'Registered_Delivery' : self.__Registered_Delivery,
                'Msg_Length' : self.__Msg_Length,
                'Msg_Content' : self.__Msg_Content.value()
                }

class cancelresp:

    def __init__(self):
        self.__Success_Id = 0


    def parse(self, body):
        self.__Success_Id = struct.unpack('!B', body)
        return {'Success_Id': self.__Success_Id
                }

class activetest:

    def __init__(self):
        self.__Reserved = 0;

    def parse(self, body):
        return {}

class nothingresp:

    def parse(self, body):
        return {}

