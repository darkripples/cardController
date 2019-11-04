# coding:utf8

from tools.RF35Manage import RF35Manage
from ez_utils import read_conf

confObj = read_conf("./conf/conf.ini")
# 扇区号
sectorNum = int(confObj.CONF.sectorNum)
# 起始块号
bStartBlockNumber = int(confObj.CONF.bStartBlockNumber)
# 新密码
newPwd = eval(confObj.CONF.newPwd)
# dll文件
dllPath = confObj.RF32.dllPath
# 串口
comNum = int(confObj.RF32.comNum)
# 波特率
bps = int(confObj.RF32.bps)

def main():

    # 初始化
    f = RF35Manage(r"D:\pythonWorkspaces\final\cardController\libs\mwrf32.dll")
    # 连接com
    ret = f.connect(comNum=comNum, bps=bps)
    if ret < 0:
        return
    f.getStatus()
    f.loadKey(keyAB=0, sectorNum=sectorNum, pwdList=newPwd)
    f.beep(msec=2000)
    # f.authentication()
    # f.read()
    f.disconnect()


main()
