# coding:utf8
"""
RF32非接触式读卡器utils
"""

import os
from ctypes import windll, c_ulong, c_byte, c_int16, c_long, c_int, c_char, c_ubyte, c_short


def consoleLog(*args):
    print(*args)


class RF35Manage:
    def __init__(self, dllPath="./mwrf32.dll", logPre=">"):
        """
        载入dll
        :param dllPath:
        """
        self.sessionId = None
        self.logPre = logPre
        if os.path.exists(dllPath):
            self.dllObj = windll.LoadLibrary(dllPath)
            consoleLog(self.logPre, "已载入", dllPath)
        else:
            consoleLog(self.logPre, "载入[", dllPath, "]失败，文件不存在")

    def connect(self, comNum=2, bps=115200):
        """
        建立连接
        :param comNum: com号
        :param bps: 波特率
        :return:
        """
        if not self.dllObj:
            return
        resp = self.dllObj.rf_init(c_int16(comNum), c_long(bps))
        if resp and resp > 0:
            self.sessionId = c_int(resp)
            consoleLog(self.logPre, "打开连接", resp)
        else:
            consoleLog(self.logPre, "连接com:", comNum, ",bps:", bps, ",失败：", resp)
        return resp

    def getStatus(self):
        """
        获取版本等信息
        :return:
        """
        if not self.sessionId:
            return
        out = (c_char * 20)(0)
        resp = self.dllObj.rf_get_status(self.sessionId, out)
        consoleLog(self.logPre, "获取版本信息:", list(out))
        return resp

    def loadKey(self, keyAB=0, sectorNum=1, pwdList=None):
        """
        加载密码,不与卡片通讯
        :param keyAB: 0为keyA；4为keyB
        :param sectorNum:
        :param pwdList:
        :return:
        """
        if not self.sessionId:
            return
        pwdBuffer = (c_ubyte * 6)(0x0)
        if pwdList:
            pwdBuffer = (c_ubyte * 6)(*pwdList)
        resp = self.dllObj.rf_load_key(self.sessionId, keyAB, sectorNum, pwdBuffer)
        if resp >= 0:
            consoleLog(self.logPre, "加载密码成功")
        else:
            consoleLog(self.logPre, "加载密码失败:", resp, "|", str(list(pwdBuffer)))
        return hex(resp)

    def loadKeyHex(self, keyAB=0, sectorNum=1, pwdList=None):
        """
        加载密码,不与卡片通讯
        :param keyAB: 0为keyA；4为keyB
        :param sectorNum:
        :param pwdList:
        :return:
        """
        if not self.sessionId:
            return
        pwdBuffer = (c_byte * 6)(0x0)
        if pwdList:
            pwdBuffer = (c_byte * 6)(*pwdList)
        resp = self.dllObj.rf_load_key_hex(self.sessionId, keyAB, sectorNum, pwdBuffer)
        if resp >= 0:
            consoleLog(self.logPre, "加载密码成功:", resp)
        else:
            consoleLog(self.logPre, "加载密码失败:", resp, "|", str(list(pwdBuffer)))
        return hex(resp)

    def rfCard(self):
        """
        寻卡
        :return:
        """
        if not self.sessionId:
            return
        out = (c_ubyte * 5)(0x0)
        # 0.只对1张卡操作
        resp = self.dllObj.rf_card(self.sessionId, c_short(1), out)
        # consoleLog(self.logPre, "寻卡输出:", list(out))
        if resp >= 0:
            consoleLog(self.logPre, "寻卡成功")
        else:
            consoleLog(self.logPre, "寻卡失败:", resp)
        return hex(resp)

    def halt(self):
        """
        终止对卡片的操作
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.rf_halt(self.sessionId)
        # if resp == 0:
        #     consoleLog(self.logPre, "终止卡操作成功")
        # else:
        #     consoleLog(self.logPre, "终止卡操作失败:", resp)
        return hex(resp)

    def authentication(self, keyAB=0, sectorNum=1):
        """
        验证密码
        :param keyAB: 0为keyA；4为keyB
        :param sectorNum:
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.rf_authentication(self.sessionId, keyAB, sectorNum)
        if resp >= 0 and resp != 1:
            consoleLog(self.logPre, "验证密码成功:", resp)
        else:
            consoleLog(self.logPre, "验证密码失败:", resp)
        return hex(resp)

    def beep(self, msec=1000):
        """
        蜂鸣
        :param msec: 10毫秒数
        :return:
        """
        if not self.sessionId:
            return
        # msec单位是10毫秒
        resp = self.dllObj.rf_beep(self.sessionId, msec)
        if resp == 0:
            consoleLog(self.logPre, "蜂鸣时间:", msec, "x10 毫秒")

    def read(self, sectorNum=1):
        """
        读取
        :param sectorNum:
        :return:
        """
        if not self.sessionId:
            return
        out = (c_ubyte * 32)(0)
        resp = self.dllObj.rf_read(self.sessionId, c_int(sectorNum), out)
        if resp >= 0 and resp != 1:
            consoleLog(self.logPre, "读卡成功")
        else:
            out = []
            consoleLog(self.logPre, "读卡失败:", resp)
        return (resp, list(out))

    def readHex(self, sectorNum=1):
        """
        读取hex
        :param sectorNum:
        :return:
        """
        if not self.sessionId:
            return
        out = (c_ubyte * 32)(0)
        resp = self.dllObj.rf_read_hex(self.sessionId, c_int(sectorNum), out)
        if resp == 0:
            consoleLog(self.logPre, "hex读卡成功:", list(out))
        else:
            consoleLog(self.logPre, "hex读卡失败:", resp)
        return list(out)

    def disconnect(self):
        """
        关闭连接
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.rf_exit(self.sessionId)
        consoleLog(self.logPre, "关闭连接", resp)
        if resp == 0:
            self.sessionId = None


def main():
    newPwd = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
    # #pwdBuffer = (c_byte * 6)(*newPwd)
    # pwdBuffer = (c_ubyte * 6)(*newPwd)
    # print(list(pwdBuffer))
    # for i, nr in enumerate(newPwd):
    #     pwdBuffer[i] = nr
    # print(list(pwdBuffer))
    pwdBuffer = (c_char * 6)(*newPwd)
    print(list(pwdBuffer))


if __name__ == "__main__":
    main()
