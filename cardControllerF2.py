# coding:utf8

import sys, time
from tools.F2Manage import F2Manage
from ez_utils import read_conf

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
dllPath = confObj.F2.dllPath
# 串口
comNum = int(confObj.F2.comNum)
# 波特率
bps = int(confObj.F2.bps)
# 卡机地址
cAddr = int(confObj.F2.cAddr)


def consoleLog(*args):
    print(*args)


def work1():
    """
    指令1：回收卡
    :return:
    """
    # 初始化
    f = F2Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    # 初始化卡内容
    f.logPre = "*"
    resp = f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=newPwd,
                      newPwdList=defaultPwd)
    f.logPre = ">"
    if resp == hex(0):
        # 弹出卡
        if f.moveToOut() == hex(0):
            consoleLog("*", "回收卡成功")

    # 关闭连接
    f.disconnect()


def work2():
    """
    指令2: 检测卡余量
    :return:
    """
    # 初始化
    f = F2Manage(dllPath)
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
    指令3：轮询检测回收卡
    :return:
    """
    # 初始化
    f = F2Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        consoleLog("*", ret)
        return

    try:
        while 1:
            # 检测传感器信息:[49, 49, 49, 48, 48, 48, 49, 48, 48, 48, 48, 48]
            flag = f.checkCardForRecovery()
            if not flag:
                time.sleep(1)
                continue

            # 初始化卡内容
            f.logPre = "*"
            resp = f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=newPwd,
                              newPwdList=defaultPwd)
            f.logPre = ">"
            if resp == hex(0):
                # 弹出卡
                if f.moveToOut() == hex(0):
                    consoleLog("*", "回收卡成功")
    finally:
        # 关闭连接
        f.disconnect()


if __name__ == "__main__":
    """
    1)  python xxx.py 1 
    2)  xxx.exe 1
    指令1：回收卡
    指令2: 检测卡余量
    指令3：轮询
    """
    pars = sys.argv
    if len(pars) == 1:
        consoleLog("*", "请输入操作指令参数")
        consoleLog("*", "\t指令1：回收卡")
        consoleLog("*", "\t指令2：检测卡余量")
        consoleLog("*", "\t指令3：轮询")
    elif len(pars) > 2:
        consoleLog("*", "指令参数有误")
    else:
        cmdNum = pars[1]
        try:
            eval("work" + cmdNum + "()")
        except Exception as e:
            import traceback
            traceback.print_exc()
            consoleLog("*", "未识别的指令")
