# coding:utf8

import sys
from tools.F3Manage import F3Manage
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
dllPath = confObj.F3.dllPath
# 串口
comNum = int(confObj.F3.comNum)
# 波特率
bps = int(confObj.F3.bps)
# 卡机地址
cAddr = int(confObj.F3.cAddr)


def consoleLog(*args):
    print(*args)


def work1():
    """
    指令1：初始化卡片并发卡
    :return:
    """
    # 初始化
    f = F3Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps, cAddr=cAddr)
    if ret != hex(0):
        return

    # 移动卡到射频位置
    f.moveToReadyWrite()

    # 初始化卡内容
    f.logPre = "*"
    resp = f.initCard(sectorNum=sectorNum, bStartBlockNumber=bStartBlockNumber, defaultPwd=defaultPwd,
                      newPwdList=newPwd)
    f.logPre = ">"
    if resp == hex(0):
        # 弹出卡
        f.moveToOut()

    # 关闭连接
    f.disconnect()


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
        return

    # 检测传感器信息:[49, 49, 49, 48, 48, 48, 49, 48, 48, 48, 48, 48]
    senserStatusResp, senserStatus = f.getSenserDetail()
    consoleLog("*" + senserStatus)

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
        return

    # 弹出卡
    f.moveToOut()

    # 关闭连接
    f.disconnect()


if __name__ == "__main__":
    """
    1)  python xxx.py 1 
    2)  xxx.exe 1
    指令1：初始化卡片并发卡
    指令2: 检测卡余量
    指令3: 从射频位弹出卡
    """
    pars = sys.argv
    if len(pars) == 1:
        consoleLog("*请输入操作指令参数")
    elif len(pars) > 2:
        consoleLog("*指令参数有误")
    else:
        cmdNum = pars[1]
        try:
            eval("work" + cmdNum + "()")
        except Exception as e:
            consoleLog("*未识别的指令")
