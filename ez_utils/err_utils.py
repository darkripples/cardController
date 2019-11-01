# coding:utf8

"""
# @Time : 2019/8/30 23:12 
# @Author : fls
# @Desc: 定义异常信息
"""

import traceback
from ez_utils import fls_log

flog = fls_log(handler_name="ez_utils.err_utils")


def err_check(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return

    return wrapper
