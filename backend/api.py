import json
from django.views import View
from django.shortcuts import HttpResponse
from django.db.models import Count
from backend import models

class GroupList(View):
    """
    获取主机组接口
    """
    def get(self,request):
        """
        获取用户拥有的主机组
        :return:
        """
        ret = {"status":True,"msg":""}
        try:
            group_list = models.ServerToAccount.objects.filter(servergroup__auditaccount__user=request.user).values(
                "servergroup__groupname","servergroup__id"
            ).annotate(num=Count(1))
            ungroup_num = models.ServerToAccount.objects.filter(auditaccount__user=request.user).count()
            ret["msg"] = {
                "group_list":list(group_list),
                "ungroup_num":ungroup_num
            }
        except Exception as error_msg:
            ret["status"] = False
            ret["msg"] = str(error_msg)
        return HttpResponse(json.dumps(ret))


class HostList(View):
    """
    获取所选主机接口
    """
    def get(self,request):
        """
        获取当前组的主机
        :return:
        """
        ret = {"status":True,"msg":""}
        try:
            group_id = request.GET.get("group_id")
            if group_id == "-1":
                host_list = models.ServerToAccount.objects.filter(auditaccount__user=request.user).values(
                    "server__nickname","server__ip","server__port","account__username","id"
                )
            else:
                host_list = models.ServerToAccount.objects.filter(servergroup__id=group_id).values(
                    "server__nickname", "server__ip", "server__port", "account__username", "id"
                )
            ret["msg"] = list(host_list)
        except Exception as error_msg:
            ret["status"] = False
            ret["msg"] = str(error_msg)
        return HttpResponse(json.dumps(ret))