# coding:utf8

from tools.ApiRequestManage import orderPlanListReq
from ez_utils import read_conf

confObj = read_conf("./conf/conf.ini")
# api相关
confObjApi = confObj.API


def orderPlanList():
    """
    查询提报的需求计划
    :return:
    """
    data = {}
    return orderPlanListReq(confObjApi.apiRoot + confObjApi.orderPlanList, data={})

if __name__ == "__main__":
    print(orderPlanList())