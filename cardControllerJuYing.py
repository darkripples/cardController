# coding:utf8

import sys, json
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


def workSHOWIO(index):
    """
    查询io输入状态
    :param index: 11.查询io输入状态；7.查询开关状态
    :return:
    """
    index = int(index)
    # 初始化
    f = JuYingManage(confObjJuYing)
    # 连接
    ret = f.connect()
    if ret != 0:
        consoleLog("*", "连接设备失败")
        return

    # 查询io输入状态
    ret = f.statusInfo()
    ioStatus = bin(ret[index])
    ioMap = {1: '0', 2: '0', 3: '0', 4: '0',
             5: '0', 6: '0', 7: '0', 8: '0'}
    for i, r in enumerate(ioStatus[::-1]):
        if r == 'b':
            break
        if r == '1':
            ioMap[i + 1] = "1"
    consoleLog("*", json.dumps(ioMap, ensure_ascii=False))
    # 关闭连接
    f.disconnect()


if __name__ == "__main__":
    """
    1)  python xxx.py on/off 1
    2)  xxx.exe on/off 1
    指令on：开启某路开关.0表示全体
    指令off: 关闭某路开关.0表示全体
    指令showio：查询io状态，传11表示查询输入;传7表示查询开关状态
    """
    pars = sys.argv
    if len(pars) < 3:
        consoleLog("*", "请输入操作指令参数")
        consoleLog("*", "\t指令on：开启某路开关.0表示全体")
        consoleLog("*", "\t指令off: 关闭某路开关.0表示全体")
        consoleLog("*", "\t指令showio：查询io状态，传11表示查询输入;传7表示查询开关状态")
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
