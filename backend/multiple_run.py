import subprocess
import os
import json
from django.db import transaction
from backend import models
from django.conf import settings


class MultipleRun:
    """
    为批量处理命令和上传文件，提供验证和选择脚本运行
    """
    def __init__(self,request,host_id_list,cmds,type,uid):
        """
        初始化
        :param request: 请求信息
        :param host_id_list: 要执行的主机Id列表
        :param cmds: 要执行的命令
        :param type: 执行命令还是上传操作
        :param uid: 上传文件对应的文件夹名
        """
        self.request = request
        self.host_id_list = host_id_list
        self.cmds = cmds
        self.type = type
        self.error = []
        self.uid = uid

    def is_valid(self):
        """
        数据验证
        :return: True验证成功
        """
        if not self.host_id_list:
            self.error.append("主机列表为空")
        if self.type == "cmd_mode":
            if not self.cmds:
                self.error.append("命令为空")
        elif self.type == "upload":
            if not self.cmds:
                self.error.append("上传路径为空")
            self.upload_store_path = os.path.join(settings.UPLOADFILES_DIR,self.uid)
            if not os.path.exists(self.upload_store_path):
                self.error.append("上传文件不存在")
        elif self.type == "download":
            if not self.cmds:
                self.error.append("下载路径为空")
        else:
            self.error.append("执行类型错误")
        if not self.error:
            return True

    def cmd_mode(self):
        """
        批量执行cmd命令
        :return:
        """
        with transaction.atomic():
            multi_his_obj = models.MultipleHistory.objects.create(user=self.request.user,type=1,cmds=self.cmds)
            create_list = []
            for connect_id in set(self.host_id_list):
                create_list.append(models.MultipleLog(task=multi_his_obj,connect_id=connect_id,status=3))
            models.MultipleLog.objects.bulk_create(create_list)
        subprocess_obj = subprocess.Popen(
            "python %s %s"%(settings.SCRIPT_PATH,multi_his_obj.id),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE
        )
        return multi_his_obj.id

    def upload(self):
        """
        从堡垒机上传文件至服务器
        :return:
        """
        with transaction.atomic():
            multi_his_obj = models.MultipleHistory.objects.create(
                user=self.request.user,type=2,
                cmds=json.dumps({"target_path":self.cmds,"original_path":self.upload_store_path})
            )
            create_list = []
            for connect_id in set(self.host_id_list):
                create_list.append(models.MultipleLog(task=multi_his_obj,connect_id=connect_id,status=3))
            models.MultipleLog.objects.bulk_create(create_list)
        subprocess_obj = subprocess.Popen(
            "python %s %s"%(settings.SCRIPT_PATH,multi_his_obj.id),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE
        )
        return multi_his_obj.id

    def download(self):
        """
        从服务器上下载文件
        :return:
        """
        with transaction.atomic():
            multi_his_obj = models.MultipleHistory.objects.create(
                user=self.request.user,type=3,
                cmds=self.cmds
            )
            create_list = []
            for connect_id in set(self.host_id_list):
                create_list.append(models.MultipleLog(task=multi_his_obj,connect_id=connect_id,status=3))
            models.MultipleLog.objects.bulk_create(create_list)
        subprocess_obj = subprocess.Popen(
            "python %s %s"%(settings.SCRIPT_PATH,multi_his_obj.id),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE
        )
        return multi_his_obj.id

    def run(self):
        """
        运行
        :return:
        """
        func = getattr(self,self.type)
        return func()