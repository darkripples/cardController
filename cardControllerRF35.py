# coding:utf8

from tools.RF35Manage import RF35Manage
from ez_utils import read_conf

confObj = read_conf("./conf/conf.ini")
# 扇区号
sectorNum = int(confObj.CONF.sectorNum)
# 新密码
newPwd = eval(confObj.CONF.newPwd)
# dll文件
dllPath = confObj.RF32.dllPath
# 串口
comNum = int(confObj.RF32.comNum) - 1
# 波特率
bps = int(confObj.RF32.bps)


def main():
    # 初始化
    # f = RF35Manage(r"D:\pythonWorkspaces\mwrf32\X86\2005, 4, 26, 1\mwrf32.dll")
    f = RF35Manage(dllPath)
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps)
    if ret < 0:
        return
    # f.getStatus()
    f.loadKey(keyAB=0, sectorNum=sectorNum, pwdList=newPwd)
    #f.loadKeyHex(keyAB=0, sectorNum=sectorNum, pwdList=newPwd)
    # f.beep(msec=50)
    try:
        needRfCard = False
        f.rfCard()
        while 1:
            if needRfCard:
                f.rfCard()
            f.authentication()
            resp, cardCont = f.read(sectorNum=sectorNum + 4)
            print(resp, cardCont)
            f.halt()
            needRfCard = True
            break


    finally:
        f.disconnect()


main()
