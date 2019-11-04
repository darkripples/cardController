# coding:utf8

import sys
import win32com.client as win
from tools.F3Manage import F3Manage
from ez_utils import read_conf

speak = win.Dispatch("SAPI.SpVoice")

confObj = read_conf("./conf/conf.ini")
# 扇区号
sectorNum = int(confObj.CONF.sectorNum)
# 起始块号
bStartBlockNumber = int(confObj.CONF.bStartBlockNumber)
# 默认密码
defaultPwd = eval(confObj.CONF.defaultPwd)
# 新密码
newPwd = eval(confObj.CONF.newPwd)
# dll文件
dllPath = confObj.F3.dllPath
# 串口
comNum = int(confObj.F3.comNum)
# 波特率
bps = int(confObj.F3.bps)
# 卡机地址
cAddr = int(confObj.F3.cAddr)


def consoleLog(*args):
    print(*args)


def work1(total, cardId):
    """
    指令1：初始化卡片并发卡
    :param total: 需小于255吨
    :param cardId:
    :return:
    """
    total = float(total)
    cardId = str(cardId)
    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    # 移动卡到射频位置
    f.moveToReadyWrite()

    # 初始化卡内容
    f.logPre = "*"
    resp = f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=defaultPwd,
                      newPwdList=newPwd)
    f.logPre = ">"
    if resp == hex(0):
        # 写卡
        total1 = int(str(total).split(".")[0])
        total2 = int(str(total).split(".")[1])

        writeNr = [int(cardId[:2] or 0), int(cardId[2:4] or 0), int(cardId[4:6] or 0),
                   int(cardId[6:8] or 0), int(cardId[8:10] or 0), int(cardId[10:12] or 0),
                   int(cardId[12:14] or 0), int(cardId[14:16] or 0), int(cardId[16:18] or 0),
                   int(cardId[18:20] or 0),
                   0x0, 0x0, 0x0, 0x0,
                   total1, total2]
        f.writeSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, pbBufferWrite=writeNr)
        # 弹出卡
        if f.moveToOut() == hex(0):
            consoleLog("*", "发卡成功,请取卡")

    # 关闭连接
    f.disconnect()

    speak.Speak("制卡完成，请取卡")


def work2():
    """
    指令2: 检测卡余量
    :return:
    """
    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    # 检测传感器信息:[49, 49, 49, 48, 48, 48, 49, 48, 48, 48, 48, 48]
    senserStatusResp, senserStatus = f.getSenserDetail()
    consoleLog("*", senserStatus)

    # 关闭连接
    f.disconnect()


def work3():
    """
    从射频位弹出卡
    :return:
    """
    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    # 弹出卡
    f.moveToOut()

    # 关闭连接
    f.disconnect()


def work4():
    """
    读卡
    :return:
    """
    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    # 移动卡到射频位置
    f.moveToReadyWrite()

    # 校验卡密码
    f.verifyPassWord(sectorNum=sectorNum, fWithKeyA=True, pwdList=defaultPwd)

    cardTxt = f.readSector(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber)
    consoleLog("*", cardTxt)

    # 关闭连接
    f.disconnect()


if __name__ == "__main__":
    """
    1)  python xxx.py 1 吨数 id
    2)  xxx.exe 1 吨数 id
    指令1：初始化卡片并发卡
    指令2: 检测卡余量
    指令3: 从射频位弹出卡
    """
    pars = sys.argv
    if len(pars) < 2 or len(pars) > 4:
        consoleLog("*", "请输入操作指令参数")
        consoleLog("*", "\t指令1：初始化卡片并发卡")
        consoleLog("*", "\t指令2：检测卡余量")
        consoleLog("*", "\t指令3：从射频位弹出卡")
    else:
        cmdNum = pars[1]
        try:
            if cmdNum == '1' and len(pars) == 4:
                total = pars[-2]
                cardId = pars[-1]
                eval("work" + cmdNum + "(" + total + ", '" + cardId + "')")
            else:
                eval("work" + cmdNum + "()")
        except Exception as e:
            import traceback

            traceback.print_exc()
            consoleLog("*", "未识别的指令")
