# coding:utf8

from ez_utils import read_conf

c = read_conf(r"./conf/conf.ini")
print(c)
defaultPwd = c.CONF.defaultPwd
print(c.F3.dllPath)
print(c.F2.dllPath)
