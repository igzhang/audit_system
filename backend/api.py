import json
import time,datetime
from django.views import View
from django.shortcuts import HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from backend import models
from src import unicode_id


@method_decorator(login_required,name="get")
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


@method_decorator(login_required,name="get")
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


@method_decorator(login_required,name="get")
class HostListAll(View):
    """
    获取当前用户所有的主机列表{-1:{},1:{}}
    """
    def get(self,request):
        """
        获取当前用户所有的主机列表
        :return:
        """
        ret = {"status":True,"msg":""}
        try:
            msg_dic = {}
            msg_dic[-1] = list(models.ServerToAccount.objects.filter(auditaccount__user=request.user).values(
                "server__nickname","server__ip","server__port","account__username","id","servergroup__id"
            ))
            group_hosts = list(models.ServerToAccount.objects.filter(servergroup__auditaccount__user=request.user).values(
                "server__nickname", "server__ip", "server__port", "account__username", "id","servergroup__id"
            ))
            for item in group_hosts:
                if msg_dic.get(item["servergroup__id"]):
                    msg_dic[item["servergroup__id"]].append(item)
                else:
                    msg_dic[item["servergroup__id"]] = [item]
            ret["msg"] = msg_dic
        except Exception as error_msg:
            ret["status"] = False
            ret["msg"] = str(error_msg)
        return HttpResponse(json.dumps(ret))


@login_required
def token(request):
    """
    获取token值
    :param request:
    :return:
    """
    if request.method == "POST":
        ret = {"status":True,"msg":""}
        try:
            connect_id = request.POST.get("connect_id")
            exist_token = models.Token.objects.filter(connect_id=connect_id,user=request.user).first()
            if exist_token:
                if datetime.datetime.now() - datetime.timedelta(seconds=settings.TOKEN_EXPIRED_TIME) < exist_token.create_time:
                    ret["msg"] = exist_token.token
                    return HttpResponse(json.dumps(ret))
            token = unicode_id.unicode_id()
            models.Token.objects.create(connect_id=connect_id,user=request.user,token=token)
            ret["msg"] = token
        except Exception as error_msg:
            ret["status"] = False
            ret["msg"] = str(error_msg)
        return HttpResponse(json.dumps(ret))