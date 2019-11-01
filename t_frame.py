# coding:utf8

from ctypes import c_byte
from ez_utils import read_conf

c = read_conf(r"./conf/conf.ini")
print(c)
defaultPwd = eval(c.CONF.defaultPwd)
print(defaultPwd)
defaultPwd = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
print(defaultPwd)

pwdList = defaultPwd
pwdBuffer = (c_byte * 6)(0x0)
if pwdList:
    for i, nr in enumerate(pwdList):
        pwdBuffer[i] = nr


print(list(pwdBuffer))