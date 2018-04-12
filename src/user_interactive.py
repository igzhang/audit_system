import subprocess
import string
import random
import os
import datetime
import getpass
from django.contrib.auth import authenticate
from django.conf import settings
from backend import models


class UserShell:
    def auth(self):
        """
        用户登陆认证
        :return:
        """
        count = 0
        while count < 3:
            username = input("username>>>").strip()
            password = getpass.getpass("password>>>").strip()
            user_obj = authenticate(username=username, password=password)
            if user_obj:
                self.user_obj = user_obj
                return True
            else:
                print("用户名或密码错误")
                count += 1

    def show_menu(self, host_list):

        while True:
            for index, host in enumerate(host_list):
                print("%s>>>>>>%s" % (index, host))
            choice = input("请选择(b返回上一层)>>>").strip()
            if choice.isdigit():
                choice = int(choice)
                if 0 <= choice < len(host_list):
                    return host_list[choice]
                else:
                    print("输入数字不符")
            elif choice.lower() == "b":
                return "b"
            else:
                print("请输入数字")

    def ssh_login(self):
        """
        ssh登陆
        :param:account_obj:账户对象
        :return:
        """
        if self.server_to_account_obj.account.ssh_type == 0:
            if settings.SSH_MODE.lower() == "original":
                self.original_ssh()

            elif settings.SSH_MODE.lower() == "paramiko":
                from lib.paramiko_master.demos import demo
                demo.run(self.user_obj,self.server_to_account_obj)

    def unicode_id(self):
        """
        生成一个10位数的唯一标识符
        :return:
        """
        choices_str = string.ascii_lowercase + string.digits
        result_list = random.sample(choices_str, 10)
        return "".join(result_list)

    def start(self):
        """
        启动交互程序
        :return:
        """
        if self.auth():
            host_ungroup_list = self.user_obj.auditaccount.server_account.all()
            host_groups_list = self.user_obj.auditaccount.server_group.all()
            try:
                while True:
                    for index, group_obj in enumerate(host_groups_list):
                        print("%s>>>>>>%s(%s)" % (index, group_obj.groupname, group_obj.account.all().count()))
                    print("%s>>>>>>未分组主机(%s)" % (len(host_groups_list), len(host_ungroup_list)))
                    choice = input("请选择(exit退出)>>>").strip()
                    if choice.isdigit():
                        choice = int(choice)
                        if 0 <= choice < len(host_groups_list):
                            self.server_to_account_obj = self.show_menu(host_groups_list[choice].account.all())
                            if self.server_to_account_obj == "b":
                                continue
                            else:
                                self.ssh_login()
                        elif choice == len(host_groups_list):
                            self.server_to_account_obj = self.show_menu(host_ungroup_list)
                            if self.server_to_account_obj == "b":
                                continue
                            else:
                                self.ssh_login()
                        else:
                            print("输入有误")
                    elif choice == "exit":
                        break
                    else:
                        print("请输入数字")
            except KeyboardInterrupt as error:
                return

    def original_ssh(self):
        session_tag = self.unicode_id()
        session_history_obj = models.SessionHistory.objects.create(
            uid=session_tag, user=self.user_obj, connect=self.server_to_account_obj
        )
        log_path = os.path.join(settings.BASE_DIR, "logs", str(session_history_obj.id) + ".log")
        subprocess.Popen(
            "sh %s %s %s" % (
                settings.SHELL_FILE_PATH,
                log_path,
                session_tag,
            ),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        cmd = "sshpass -p %s %s %s@%s -o StrictHostKeyChecking=no -Z %s" % (
            self.server_to_account_obj.account.password,
            settings.SSH_FILE_PATH,
            self.server_to_account_obj.account.username,
            self.server_to_account_obj.server.ip,
            session_tag
        )
        subprocess.run(cmd, shell=True)
        models.SessionHistory.objects.filter(id=session_history_obj.id).update(end_time=datetime.datetime.now())
