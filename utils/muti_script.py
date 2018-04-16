import sys
import os
import multiprocessing
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audit.settings")
django.setup()
import paramiko
from django.conf import settings
from backend import models


def cmd_run(ip,port,username,password,cmd,task_id):
    """
    单个主机远程连接
    :param ip:
    :param port:
    :param username:
    :param password:
    :param cmd:
    :return:
    """
    result = ""
    status = 3
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, port=port, username=username, password=password,timeout=30)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()+stderr.read()
        result = result.decode("utf8")
        if not result:
            result = "运行结果为空"
        status = 1
    except Exception as error_msg:
        result = str(error_msg)
        status = 2
    finally:
        ssh.close()
        models.MultipleLog.objects.filter(
            task_id=task_id, connect__server__ip=ip, connect__account__username=username
        ).update(status=status,result=result)


def upload(ip,port,username,password,cmd,task_id):
    result = ""
    status = 3
    try:
        transport = paramiko.Transport((ip, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        upload_dic = json.loads(cmd)
        for filename in os.listdir(upload_dic["original_path"]):
            target_path = "%s/%s"%(upload_dic["target_path"],filename)
            try:
                if sftp.stat(target_path):
                    continue
            except IOError as e:
                pass
            sftp.put(r"%s/%s"%(upload_dic["original_path"],filename),target_path)
            result += " %s上传成功"%filename
        status = 1
    except Exception as error_msg:
        result = str(error_msg)
        status = 2
    finally:
        transport.close()
        models.MultipleLog.objects.filter(
            task_id=task_id, connect__server__ip=ip, connect__account__username=username
        ).update(status=status,result=result)

def download(ip,port,username,password,cmd,task_id):
    result = ""
    status = 3
    try:
        transport = paramiko.Transport((ip, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        local_path = os.path.join(settings.DOWNLOADFILES_DIR,task_id)
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        local_file = "%s\\%s-%s"%(local_path,ip,os.path.basename(cmd))
        if not os.path.exists(local_file):
            sftp.get(cmd,local_file)
        result += "下载成功"
        status = 1
    except Exception as error_msg:
        result = str(error_msg)
        status = 2
    finally:
        transport.close()
        models.MultipleLog.objects.filter(
            task_id=task_id, connect__server__ip=ip, connect__account__username=username
        ).update(status=status, result=result)


def start():
    task_id = sys.argv[1]  # 批处理记录表id
    hosts_log_list = models.MultipleLog.objects.filter(task_id=task_id).values(
        "task__type",
        "connect__account__username", "connect__account__password",
        "connect__server__ip", "connect__server__port", "task__cmds"
    )
    pool = multiprocessing.Pool(settings.MULTI_POOL_MAX)
    func_dic = {
        1:cmd_run,
        2:upload,
        3:download
    }

    for item in hosts_log_list:
        pool.apply_async(
            func_dic[item["task__type"]],
            args=(
                item["connect__server__ip"], item["connect__server__port"],
                item["connect__account__username"], item["connect__account__password"],
                item["task__cmds"],task_id
            )
        )
    pool.close()
    pool.join()


if __name__ == '__main__':
    start()
