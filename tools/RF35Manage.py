# coding:utf8
"""
RF32非接触式读卡器utils
"""

import os
from ctypes import windll, c_ulong, c_byte
from ez_utils import err_check


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

    @err_check
    def connect(self, comNum=2, bps=115200):
        """
        建立连接
        :param comNum: com号
        :param bps: 波特率
        :return:
        """
        if not self.dllObj:
            return
        resp = self.dllObj.rf_init(comNum, bps)
        if resp > 0:
            self.sessionId = resp
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
        out = (c_ulong * 32)(0)
        resp = self.dllObj.rf_get_status(self.sessionId, out)
        consoleLog("状态信息:", resp)

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
        pwdBuffer = (c_byte * 6)(0x0)
        if pwdList:
            for i, nr in enumerate(pwdList):
                pwdBuffer[i] = nr
        resp = self.dllObj.rf_load_key(self.sessionId, keyAB, sectorNum, pwdBuffer)
        if resp == 0:
            consoleLog(self.logPre, "加载密码成功", resp)
        else:
            consoleLog(self.logPre, "加载密码失败", resp)
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
        if resp == 0:
            consoleLog(self.logPre, "验证密码成功", resp)
        else:
            consoleLog(self.logPre, "验证密码失败", resp)
        return hex(resp)

    def beep(self, msec=1000):
        """
        蜂鸣
        :param msec: 毫秒数
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.rf_beep(self.sessionId, msec)
        consoleLog("蜂鸣:", resp)
        consoleLog(self.logPre, "蜂鸣时间:", msec, "毫秒")

    def read(self, sectorNum=1):
        """
        读取
        :param sectorNum:
        :return:
        """
        if not self.sessionId:
            return
        out = (c_ulong * 32)(0)
        resp = self.dllObj.rf_read(self.sessionId, c_byte(sectorNum), out)
        consoleLog("读取:", resp)
        consoleLog("读取:", list(out))
        return list(out)

    def readHex(self, sectorNum=1):
        """
        读取hex
        :param sectorNum:
        :return:
        """
        if not self.sessionId:
            return
        out = (c_ulong * 32)(0)
        resp = self.dllObj.rf_read_hex(self.sessionId, c_byte(sectorNum), out)
        consoleLog("读取:", resp)
        consoleLog("读取:", list(out))
        return list(out)

    def disconnect(self):
        """
        关闭连接
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.rf_exit(self.sessionId)
        consoleLog("关闭连接", resp)


def main():
    # 扇区号
    sectorNum = 1
    # 起始块号
    bStartBlockNumber = 1
    # 默认密码
    defaultPwd = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]

    # 初始化
    f = RF35Manage(r"./mwrf32/X86/2005, 4, 26, 1/mwrf32.dll")
    # 连接com
    ret = f.connect(comNum=2, bps=115200)
    if ret < 0:
        return
    f.getStatus()
    f.loadKey(keyAB=0, sectorNum=sectorNum, pwdList=defaultPwd)
    f.beep(msec=2000)
    # f.authentication()
    # f.read()
    f.disconnect()


if __name__ == "__main__":
    main()
