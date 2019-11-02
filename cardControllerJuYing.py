# coding:utf8

import sys
from tools.JuYingManage import JuYingManage
from ez_utils import read_conf

confObj = read_conf("./conf/conf.ini")
# 聚英继电器控制相关
confObjJuYing = confObj.JuYing


def consoleLog(*args):
    print(*args)


def workON(switchNum):
    """
    指令on：开启某路开关
    :param switchNum:
    :return:
    """
    # 初始化
    f = JuYingManage(confObjJuYing)
    # 连接
    ret = f.connect()
    if ret != 0:
        consoleLog("*", "连接设备失败")
        return

    # 打开开关
    if switchNum == 0:
        f.allControl("on")
    else:
        f.openSwitch(switchNum)

    # 关闭连接
    f.disconnect()


def workOFF(switchNum):
    """
    指令off: 关闭某路开关
    :param switchNum:
    :return:
    """
    # 初始化
    f = JuYingManage(confObjJuYing)
    # 连接
    ret = f.connect()
    if ret != 0:
        consoleLog("*", "连接设备失败")
        return

    # 关闭开关
    if switchNum == 0:
        f.allControl("off")
    else:
        f.offSwitch(switchNum)

    # 关闭连接
    f.disconnect()


def workSHOWIO(nonePar):
    """
    查询io输入状态
    :return:
    """
    # 初始化
    f = JuYingManage(confObjJuYing)
    # 连接
    ret = f.connect()
    if ret != 0:
        consoleLog("*", "连接设备失败")
        return

    #
    f.showIOInInfo()

    # 关闭连接
    f.disconnect()


if __name__ == "__main__":
    """
    1)  python xxx.py on/off 1
    2)  xxx.exe on/off 1
    指令on：开启某路开关.0表示全体
    指令off: 关闭某路开关.0表示全体
    """
    pars = sys.argv
    if len(pars) < 3:
        consoleLog("*", "请输入操作指令参数")
        consoleLog("*", "\t指令on：开启某路开关")
        consoleLog("*", "\t指令off: 关闭某路开关")
    elif len(pars) > 3:
        consoleLog("*", "指令参数有误")
    else:
        cmdNum = pars[1].upper()
        switchNum = pars[2]
        try:
            eval("work" + cmdNum + "(" + switchNum + ")")
        except Exception as e:
            import traceback
            traceback.print_exc()
            consoleLog("*", "未识别的指令")
