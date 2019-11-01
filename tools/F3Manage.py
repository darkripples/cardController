# coding:utf8
"""
F3发卡机utils
F3API.dll版本:2015/1/30
对应demo程序V3.05
"""

import os
from ctypes import windll, c_ulong, c_byte, c_int
from ez_utils import read_conf


def consoleLog(*args):
    print(*args)


class F3Manage:
    def __init__(self, dllPath="./F3API.dll", logPre=">"):
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

    def connect(self, comNum=3, bps=9600, cAddr=0):
        """
        建立连接
        :param comNum: com号
        :param bps: 波特率
        :param cAddr: 卡机地址 0-15
        :return:
        """
        if not self.dllObj:
            return "未载入dll文件"
        out = (c_ulong * 32)(0)
        resp = self.dllObj.F3_Connect(comNum, bps, cAddr, out)
        if hex(resp) == hex(0):
            self.sessionId = out[0]
            consoleLog(self.logPre, "连接成功com:", comNum, ";句柄:", self.sessionId)
            return hex(resp)
        else:
            consoleLog(self.logPre, "连接com:", comNum, ",失败：", hex(resp))
            return "连接com:" + comNum + ",失败：" + hex(resp)

    def getSenserDetail(self):
        """
        检测传感器信息
        是否有卡:值为 0x31，表示有卡；值为 0x30，表示无卡
        :return:
        """
        if not self.dllObj:
            return
        out = (c_byte * 12)(0x00)
        resp = self.dllObj.F3_GetSenserDetail(self.sessionId, out)
        if hex(resp) == hex(0):
            # [49, 49, 49, 48, (48), 48, (49), 48, 48, 48, 48, 48]
            consoleLog(self.logPre, "检测传感器信息:" + str(list(out)))
            if 0x31 in out:
                # out[3]    出卡槽
                # out[0],out[1],out[2]  射频位
                # out[4]    备用卡槽 卡余量充足
                # out[6]    备用卡槽 有卡
                msg = ""
                if out[4] == 0x30:
                    if out[6] == 0x31:
                        msg += ("卡余量不足" + ",")
                    else:
                        msg += ("无可用卡" + ",")
                if out[3] == 0x31:
                    msg += ("出卡槽有卡未取" + ",")
                if out[0] == out[1] == out[2] == 0x31:
                    msg += ("射频位有卡未处理完" + ",")
                msg = msg[:-1]
                consoleLog(self.logPre, msg)
                return (hex(0), msg)
                # 其他情况本程序未用到
            else:
                # 所有传感器都无卡
                consoleLog(self.logPre, "无可用卡")
                self.disconnect()
                self.sessionId = None
                return (hex(0), '无可用卡')
        else:
            consoleLog(self.logPre, "检测传感器信息失败:", hex(resp))
        return (hex(resp), '')

    def moveCard(self, movePar=0x32):
        """
        移动卡位置

        #移动卡到前端持卡位 MM_RETURN_TO_FRONT	0x30
        #移动卡到IC位 MM_RETURN_TO_IC_POS	0x31
        #移动卡到射频位 MM_RETURN_TO_RF_POS	0x32
        #回收卡 MM_CAPTURE_TO_BOX	0x33
        #从前端弹出卡片 MM_EJECT_TO_FRONT	0x39
        :param movePar:
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.F3_MoveCard(self.sessionId, c_int(movePar))
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "移动卡成功")
        return hex(resp)

    def moveToReadyWrite(self):
        """
        移动卡到射频位置
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.F3_MoveCard(self.sessionId, c_int(0x32))
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "移动卡到射频位")
        return hex(resp)

    def moveToOut(self):
        """
        移动卡到前端
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.F3_MoveCard(self.sessionId, c_int(0x39))
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "移动卡到前端")
        return hex(resp)

    def verifyPassWord(self, sectorNum=1, fWithKeyA=True, pwdList=None):
        """
        校验卡
        :param sectorNum: 要认证的扇区号
        :param pwdList: 密码
        :return:
        """
        if not self.sessionId:
            return
        pwdBuffer = (c_byte * 6)(0x0)
        if pwdList:
            for i, nr in enumerate(pwdList):
                pwdBuffer[i] = nr
        resp = self.dllObj.F3_MfVerifyPassword(self.sessionId, sectorNum, fWithKeyA, pwdBuffer)
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "校验卡成功")
        else:
            consoleLog(self.logPre, "校验卡密码失败:", hex(resp))
        return hex(resp)

    def changePassword(self, sectorNum=1, fWithKeyA=True, oldPwdList=None, newPwdList=None):
        """
        修改扇区密码
        :param sectorNum:
        :param oldPwdList:
        :param newPwdList:
        :return:
        """
        if not self.sessionId:
            return
        pwdBuffer = (c_byte * 6)(0x0)
        if oldPwdList:
            for i, nr in enumerate(oldPwdList):
                pwdBuffer[i] = nr
        else:
            consoleLog(self.logPre, "旧密码不可空")
            return
        # 校验旧密码
        resp = self.dllObj.F3_MfVerifyPassword(self.sessionId, sectorNum, fWithKeyA, pwdBuffer)
        if hex(resp) == hex(0):
            # 修改密码
            pwdBuffer = (c_byte * 6)(0x0)
            if newPwdList:
                for i, nr in enumerate(newPwdList):
                    pwdBuffer[i] = nr
            else:
                consoleLog(self.logPre, "新密码不可空")
                return
            resp2 = self.dllObj.F3_MfUpdatePassword(self.sessionId, sectorNum, pwdBuffer)
            if hex(resp2) == hex(0):
                consoleLog(self.logPre, "修改密码成功")
                return
            else:
                consoleLog(self.logPre, "修改密码失败:", hex(resp2))
                return
        else:
            consoleLog(self.logPre, "校验旧密码失败:", hex(resp))

    def setPassword(self, sectorNum=1, newPwdList=None):
        """
        强制重置密码-keyA
        :param sectorNum:
        :param newPwdList:
        :return:
        """
        if not self.sessionId:
            return
        pwdBuffer = (c_byte * 6)(0x0)
        if newPwdList:
            for i, nr in enumerate(newPwdList):
                pwdBuffer[i] = nr
        else:
            consoleLog(self.logPre, "新密码不可空")
            return "999"
        resp2 = self.dllObj.F3_MfUpdatePassword(self.sessionId, sectorNum, pwdBuffer)
        if hex(resp2) == hex(0):
            consoleLog(self.logPre, "置密码成功")
            return hex(0)
        else:
            consoleLog(self.logPre, "置密码失败:", hex(resp2))
            return hex(resp2)

    def readSector(self, sectorNum=1, bStartBlockNumber=1, bBlocksToRead=1):
        """
        读卡
        :param sectorNum: 扇区号
        :param bStartBlockNumber: 起始块号
        :param bBlocksToRead: 读取的块数
        :return:
        """
        if not self.sessionId:
            return
        pbBuffer = (c_byte * 16)(0x00)
        pcbLength = (c_int * 16)(16)
        resp = self.dllObj.F3_MfReadSector(self.sessionId, sectorNum, bStartBlockNumber, pbBuffer,
                                           pcbLength)
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "读卡成功")
            return [hex((i + 256) % 256).upper() for i in list(pbBuffer)]
            # return list(pbBuffer)
        consoleLog(self.logPre, "读卡失败:", hex(resp))
        return []

    def writeSector(self, sectorNum=1, bStartBlockNumber=1, bBytesToWrite=16, pbBufferWrite=None):
        """
        写卡
        :param sectorNum: 扇区号
        :param bStartBlockNumber: 起始块号
        :param bBytesToWrite: 写入的字节数
        :param pbBufferWrite: 写入的数据
        :return:
        """
        if not self.sessionId:
            return
        if not pbBufferWrite:
            consoleLog(self.logPre, "写卡失败:", "写卡内容不可为空")
            return
        if len(pbBufferWrite) > 16:
            consoleLog(self.logPre, "写卡失败:", "写卡内容过大")
            return
        pbBuffer = (c_byte * 16)(0x00)
        for i, nr in enumerate(pbBufferWrite):
            pbBuffer[i] = nr
        resp = self.dllObj.F3_MfWriteSector(self.sessionId, sectorNum, bStartBlockNumber, bBytesToWrite, pbBuffer)
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "写卡成功")
        else:
            consoleLog(self.logPre, "写卡失败:", hex(resp))
        return hex(resp)

    def initSectorData(self, sectorNum=1, bStartBlockNumber=1):
        """
        清空某块的数据
        :param sectorNum:
        :param bStartBlockNumber:
        :return:
        """
        if not self.sessionId:
            return
        bBytesToWrite = 16
        pbBuffer = (c_byte * 16)(0x00)
        resp = self.dllObj.F3_MfWriteSector(self.sessionId, sectorNum, bStartBlockNumber, bBytesToWrite, pbBuffer)
        if hex(resp) == hex(0):
            consoleLog(self.logPre, "清空卡数据成功")
        else:
            consoleLog(self.logPre, "清空卡数据失败:", hex(resp))
        return hex(resp)

    def initCard(self, sectorNum=1, bStartBlockNumber=1, defaultPwd=None, newPwdList=None):
        """
        初始化卡的数据-清空卡数据、把默认密码修改掉
        :param sectorNum:
        :param bStartBlockNumber:
        :param newPwdList:
        :return:
        """
        if not self.sessionId:
            return
        # 用默认密码校验
        r1 = self.verifyPassWord(sectorNum=sectorNum, fWithKeyA=True, pwdList=defaultPwd)
        if r1 != hex(0):
            return r1
        # 清空数据
        writeNr = [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
        r2 = self.writeSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, pbBufferWrite=writeNr)
        if r2 != hex(0):
            return r2
        # 重置密码
        r3 = self.setPassword(sectorNum=sectorNum, newPwdList=newPwdList)
        if r3 != hex(0):
            return r3
        return hex(0)

    def disconnect(self):
        """
        断开连接
        :return:
        """
        if not self.sessionId:
            return
        resp = self.dllObj.F3_Disconnect(self.sessionId)
        if hex(resp) == hex(0):
            self.sessionId = None
            consoleLog(self.logPre, "断开连接成功")
        else:
            consoleLog(self.logPre, "断开连接失败:", hex(resp))
        return hex(resp)


def initCard(confObj):
    # 扇区号
    sectorNum = confObj.CONF.sectorNum
    # 起始块号
    bStartBlockNumber = confObj.CONF.bStartBlockNumber
    # 默认密码
    defaultPwd = eval(confObj.CONF.defaultPwd)
    # 新密码
    newPwd = eval(confObj.CONF.newPwd)
    # dll文件
    dllPath = confObj.F3.dllPath
    # 串口
    comNum = eval(confObj.F3.comNum)
    # 波特率
    bps = eval(confObj.F3.bps)
    # 卡机地址
    cAddr = eval(confObj.F3.cAddr)

    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        return
    # 检测传感器信息:[49, 49, 49, 48, 48, 48, 49, 48, 48, 48, 48, 48]
    f.getSenserDetail()
    # 移动卡到射频位置
    f.moveToReadyWrite()

    # 初始化卡内容
    f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=defaultPwd, newPwdList=newPwd)

    # 断开com连接
    f.disconnect()


def main():
    confObj = read_conf("./conf/conf.ini")
    # 扇区号
    sectorNum = confObj.CONF.sectorNum
    # 起始块号
    bStartBlockNumber = confObj.CONF.bStartBlockNumber
    # 默认密码
    defaultPwd = eval(confObj.CONF.defaultPwd)
    # 新密码
    newPwd = eval(confObj.CONF.newPwd)
    # dll文件
    dllPath = confObj.F3.dllPath
    # 串口
    comNum = eval(confObj.F3.comNum)
    # 波特率
    bps = eval(confObj.F3.bps)
    # 卡机地址
    cAddr = eval(confObj.F3.cAddr)

    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        return
    # 检测传感器信息:[49, 49, 49, 48, 48, 48, 49, 48, 48, 48, 48, 48]
    senserStatusResp, senserStatus = f.getSenserDetail()
    if senserStatusResp != hex(0):
        return
    # 移动卡到射频位置
    f.moveToReadyWrite()

    # 初始化卡内容
    f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=defaultPwd, newPwdList=newPwd)

    # # 校验卡密码
    # f.verifyPassWord(sectorNum=sectorNum, fWithKeyA=True, pwdList=defaultPwd)
    # # 读卡
    # cardTxt = f.readSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber)
    # print(cardTxt)
    # # 写卡
    # writeNr = [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4]
    # f.writeSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, pbBufferWrite=writeNr)
    # # 读卡
    # cardTxt = f.readSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber)
    # print(cardTxt)

    # 弹出卡
    # f.moveToOut()

    # defaultPwd = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
    # newPwdList = [0x1, 0x2, 0x3, 0x4, 0x5, 0x5]
    # # 修改密码
    # f.changePassword(sectorNum=1, fWithKeyA=True, oldPwdList=defaultPwd, newPwdList=newPwdList)
    # cardTxt = f.readSector(sectorNum=1, bStartBlockNumber=1, bBlocksToRead=1)
    # print(cardTxt)

    # 断开com连接
    f.disconnect()


if __name__ == "__main__":
    main()
