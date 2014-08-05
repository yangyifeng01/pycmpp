#!/usr/bin/env python


import socket
import struct
import hashlib
import time
import cmppresp



class messageheader:
    """
    the common message header
    """
    def __init__(self, messagebodylength=0, command_id = b'', seq = 0):
        self.__total_length = struct.pack('!L', 12+messagebodylength)
        self.__command_id = struct.pack('!L', command_id)
        self.__sequence_id = struct.pack('!L', seq)

    def header(self):
        return self.__total_length + self.__command_id + self.__sequence_id

    def total_length(self):
        return self.__total_length

    def command_id(self):
        return self.__command_id

    def sequence_id(self):
        return self.__sequence_id

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
        authenticatorsource = self.__sourceaddr + \
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00' + \
                self.__password + get_strtime().encode('utf-8')
        self.__md5 = hashlib.md5(authenticatorsource).digest()
        self.__length = 27
        self.__body = self.__sourceaddr + self.__md5 + self.__version + self.__timestamp

    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmppsubmit:
    """
    submit short message to ISMG
    """

    def __init__(self,
            Msg_Id = 0,
            Pk_total = 1,
            Pk_number = 1,
            Registered_Delivery = 0,
            Msg_level = 0,
            Service_Id = 'MJS0019905',
            Fee_UserType = 2,
            Fee_terminal_Id = 0,
            TP_pId = 0, TP_udhi = 0,
            Msg_Fmt = 0, Msg_src = '000000',
            FeeType = '05', FeeCode = '000000',
            ValId_Time = 17*'\x00',
            At_Time = 17*'\x00',
            Src_Id = '000000000000',
            DestUsr_tl = 1,
            Dest_terminal_Id = '8613900000000',
            Msg_Length = 4,
            Msg_Content = 'test',
            Reserve = 8*'0'):
        self.__Msg_Id = struct.pack('!Q', Msg_Id)
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
        self.__Msg_Content = Msg_Content.encode('utf-8')
        self.__Reserve = Reserve.encode('utf-8')
        self.__length = 126 + 21 * DestUsr_tl + Msg_Length
        self.__body = self.__Msg_Id + \
                self.__Pk_total + self.__Pk_number + \
                self.__Registered_Delivery + \
                self.__Msg_level + self.__Service_Id + \
                self.__Fee_UserType + self.__Fee_terminal_Id + \
                self.__TP_pId + self.__TP_udhi + \
                self.__Msg_Fmt + self.__Msg_src + \
                self.__FeeType + self.__FeeCode + \
                self.__ValId_Time + self.__At_Time + \
                self.__Src_Id + self.__DestUsr_tl + \
                self.__Dest_terminal_Id + self.__Msg_Length + \
                self.__Msg_Content + self.__Reserve


    def body(self):
        return self.__body

    def length(self):
        return self.__length

class cmpp:
    """
    the base class to connect to ISMG
    """

    def __init__(self, gateway='221.131.129.1', port=7890):
        self.__gateway = gateway
        self.__port = port
        self.__sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__resp = cmppresp.response()

    def __del__(self):
        self.__sp.close()

    def connect(self):
        cmppaddr = (self.__gateway, self.__port)
        self.__sp.connect(cmppaddr)

    def send(self, message):
        self.__sp.send(message)

    def recv(self, resp):
        length = self.__sp.recv(4)
        maxlen,=struct.unpack('!L',length)
        self.__resp.parse(length + self.__sp.recv(maxlen-4))
        mh = self.__resp.parseheader()
        mb = self.__resp.parsebody(resp)
        return mh, mb


