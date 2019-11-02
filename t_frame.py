# coding:utf8

from ctypes import c_byte
from ez_utils import read_conf
from tools.F3Manage import F3Manage
import pyttsx3

def main():
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

    defaultPwd = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
    newPwdList = [0x1, 0x2, 0x3, 0x4, 0x5, 0x5]
    # 修改密码
    f.changePassword(sectorNum=sectorNum, fWithKeyA=True, oldPwdList=defaultPwd, newPwdList=newPwdList)
    # cardTxt = f.readSector(sectorNum=1, bStartBlockNumber=1, bBlocksToRead=1)
    # print(cardTxt)

    # 断开com连接
    f.disconnect()

if __name__=="__main__":
    main()