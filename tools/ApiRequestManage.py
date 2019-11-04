# coding:utf8

import requests


def orderPlanListReq(url, data=None):
    """
    查询需求计划
    :param url:
    :param data:
    :return:
    """
    return requests.post(url, data=data).json()
