import json
import os
import datetime
import zipfile
from wsgiref.util import FileWrapper
from django.views import View
from django.shortcuts import HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from backend import models
from backend import multiple_run
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


@login_required
def multirun(request):
    """
    批量处理命令或上传文件
    :param request:
    :return:
    """
    if request.method == "POST":
        ret = {"status":True,"msg":""}
        host_id_list = request.POST.getlist("host_id_list[]")
        cmds = request.POST.get("cmd")
        type = request.POST.get("type")
        uid = request.POST.get("uid")
        obj = multiple_run.MultipleRun(request,host_id_list,cmds,type,uid)
        if obj.is_valid():
            ret["msg"] = obj.run()
        else:
            ret["status"] = False
            ret["msg"] = obj.error
        return HttpResponse(json.dumps(ret))


@login_required
def cmdresult(request):
    """
    根据task_id获取cmd运行结果
    :param request:
    :return:
    """
    if request.method == "GET":
        ret = {"status":True,"msg":""}
        try:
            task_id = request.GET.get("task_id")
            result_list = list(models.MultipleLog.objects.filter(task_id=task_id).values(
                "status","result","connect__account__username","connect__server__ip"
            ))
            ret["msg"] = result_list
        except Exception as error_msg:
            ret["status"] = False
            ret["msg"] = str(error_msg)
        return HttpResponse(json.dumps(ret))


@login_required
def filerecv(request):
    """
    接收上传的文件
    :param request:
    :return:
    """
    file_obj = request.FILES.get("file")
    uid = request.GET.get("uid")
    recv_path = os.path.join(settings.UPLOADFILES_DIR,uid)
    if not os.path.exists(recv_path):
        os.makedirs(recv_path)
    file_path = os.path.join(recv_path,file_obj.name)
    with open(file_path,"wb") as file_stream:
        for chunk in file_obj.chunks():
            file_stream.write(chunk)
    return HttpResponse()


@login_required
def file_download(request):
    """
    从堡垒机下载文件到本地
    :param request:
    :return:
    """
    task_id = request.GET.get("taskid")
    zip_name = "%s-files"%task_id
    archive = zipfile.ZipFile(zip_name,"w",zipfile.ZIP_DEFLATED)
    task_dir = os.path.join(settings.DOWNLOADFILES_DIR,task_id)
    file_path = os.listdir(task_dir)
    for file_name in file_path:
        archive.write("%s/%s"%(task_dir,file_name),arcname=file_name)
    archive.close()

    wrapper = FileWrapper(open(zip_name,"rb"))
    response = HttpResponse(wrapper,content_type="application/zip")
    response["Content-Dispositon"] = "attachment;filename=%s.zip"%zip_name
    response["Content-Length"] = os.path.getsize(zip_name)
    return response