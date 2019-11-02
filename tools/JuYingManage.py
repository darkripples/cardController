# coding:utf8
"""
聚英继电器控制utils
"""

import socket, struct


def consoleLog(*args):
    print(*args)


def crc16_1(x: str, invert: bool):
    """
    计算字符串的crc16校验位
    :param x:
    :param invert:
    :return:
    """
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    # s = hex(a).upper()
    # return s[4:6] + s[2:4] if invert == True else s[2:4] + s[4:6]
    s = struct.pack("H", a)
    return bytearray([i for i in s]).hex()


class JuYingManage:
    def __init__(self, confObjJuYing, logPre=">"):
        self.connObj = None
        self.ip = confObjJuYing.ip
        self.port = int(confObjJuYing.port or 0)
        self.deviceAddr = int(confObjJuYing.deviceAddr or 254)
        self.switchNum = confObjJuYing.switchNum or 8
        if not (self.ip or self.port or self.deviceAddr):
            consoleLog(self.logPre, "载入参数文件失败")
        self.logPre = logPre

    def connect(self):
        """
        建立socket连接
        :return:
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((self.ip, int(self.port)))
            self.connObj = s
            consoleLog(self.logPre, "连接成功:(%s,%s)" % (self.ip, self.port))
            return 0
        except:
            consoleLog(self.logPre, "连接失败:(%s,%s)" % (self.ip, self.port))
            return 1

    def openSwitch(self, switchNum):
        """
        打开开关
        :param switchNum:
        :return:
        """
        self.singleControl(switchNum, "on")

    def offSwitch(self, switchNum):
        """
        关闭开关
        :param switchNum:
        :return:
        """
        self.singleControl(switchNum, "off")

    def singleControl(self, switchNum, way):
        """
        单路开关控制
        :param switchNum:
        :param way: on/off
        :return:
        """
        cmd = 0
        msg = "关闭"
        if way == "on":
            cmd = 255
            msg = "开启"
        buf = struct.pack("B" * 6, self.deviceAddr,
                          5,  # 5.单路控制
                          0, switchNum - 1,  # 要控制的开关位置
                          cmd, 0  # 255,0：开启指令； 0,0：关闭指令
                          )
        # 获取校验位
        check_byte = crc16_1(buf.decode("unicode-escape"), True)
        check_buf = struct.pack("B" * 2,
                                int(check_byte[:2], 16), int(check_byte[-2:], 16))
        buf = buf + check_buf

        self.connObj.send(buf)
        resp = self.connObj.recv(1024)
        if resp == buf:
            consoleLog(self.logPre, msg, switchNum, "路继电器成功")
        else:
            consoleLog(self.logPre, msg, switchNum, "路继电器失败:" + str(resp))

    def showIOInInfo(self):
        """
        查询io输入状态
        :return:
        """
        pass

    def allControl(self, way):
        """
        控制全体
        :param way: on/off
        :return:
        """
        cmd = 0
        msg = "关闭"
        if way == "on":
            cmd = 255
            msg = "开启"
        buf = struct.pack("B" * 8, self.deviceAddr,
                          15,  # 0f返回指令：如果查询错误，返回 0x82
                          0, 0,
                          0, 8,  # 控制的继电器数量
                          1,  # 发送命令字节数
                          cmd  # 255：开启指令； 0：关闭指令
                          )
        # 获取校验位
        check_byte = crc16_1(buf.decode("unicode-escape"), True)
        check_buf = struct.pack("B" * 2,
                                int(check_byte[:2], 16), int(check_byte[-2:], 16))
        buf = buf + check_buf
        self.connObj.send(buf)
        resp = self.connObj.recv(1024)
        if resp[1] == 15:
            consoleLog(self.logPre, msg, "全部继电器成功")
        else:
            consoleLog(self.logPre, msg, "全部继电器失败:" + str(resp))

    def disconnect(self):
        """
        关闭socket连接
        :return:
        """
        if self.connObj:
            self.connObj.close()


def testBuf():
    data = "FE050001FF00C9F5"
    num = 2
    # 设备地址
    device_addr = 254
    # 255开启；0关闭
    cmd = 255

    buf = struct.pack("B" * 6, device_addr,
                      5,
                      0, num - 1,
                      cmd, 0  # 255,0：开启指令； 0,0：关闭指令
                      )
    # 全开
    buf = struct.pack("B" * 8, device_addr,
                      15,  # 0f返回指令：如果查询错误，返回 0x82
                      0, 0,
                      0, 8,  # 控制的继电器数量
                      1,  # 发送命令字节数
                      cmd  # 255：开启指令； 0：关闭指令
                      )
    print("buf0:", buf)
    print('buf4:', buf.decode("unicode-escape"))
    # 校验位置
    # print('check:', '\xfe\x05\x00\x01\xff\x00')

    # check_byte = crc16_1('\xfe\x05\x00\x01\xff\x00', True)
    check_byte = crc16_1(buf.decode("unicode-escape"), True)
    print("check_byte:", check_byte, int(check_byte[:2], 16), int(check_byte[-2:], 16))
    b1 = struct.pack("B" * 2,
                     int(check_byte[:2], 16), int(check_byte[-2:], 16))
    print("crc16:", b1)
    b1 = buf + b1
    print('final:', b1)


if __name__ == "__main__":
    # open(2)
    testBuf()
