from django.db import models
from django.contrib.auth.models import User


class IDC(models.Model):
    """
    机房表
    """
    name = models.CharField(verbose_name="机房名", max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "机房表"


class Server(models.Model):
    """
    主机表
    """
    nickname = models.CharField(verbose_name="服务器别名", max_length=128, unique=True)
    ip = models.GenericIPAddressField(verbose_name="IP地址", unique=True)
    port = models.IntegerField(verbose_name="端口", default=22)
    idc = models.ForeignKey(verbose_name="所属机房", to="IDC", to_field="id", on_delete=models.CASCADE)
    enable = models.BooleanField(verbose_name="是否启用", default=True)

    def __str__(self):
        return "%s-%s" % (self.nickname, self.ip)

    class Meta:
        verbose_name_plural = "主机表"


class ServerAccount(models.Model):
    """
    主机上的账户表
    """
    ssh_type_choices = (
        (0, "密码登陆"),
        (1, "密钥登陆"),
    )
    ssh_type = models.SmallIntegerField(verbose_name="验证方式", choices=ssh_type_choices)
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=128, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        unique_together = ("username", "password")
        verbose_name_plural = "主机上的账户"


class ServerToAccount(models.Model):
    """
    主机和登陆信息关系表
    """
    server = models.ForeignKey(verbose_name="服务器", to="Server", on_delete=models.CASCADE)
    account = models.ForeignKey(verbose_name="登陆信息", to="ServerAccount", on_delete=models.CASCADE)

    def __str__(self):
        return "%s-%s" % (self.server, self.account)

    class Meta:
        verbose_name_plural = "主机和登陆信息关系"


class ServerGroup(models.Model):
    """
    主机组表
    """
    groupname = models.CharField(verbose_name="组名", max_length=128, unique=True)
    account = models.ManyToManyField(to="ServerToAccount")

    def __str__(self):
        return self.groupname

    class Meta:
        verbose_name_plural = "主机组"


class AuditAccount(models.Model):
    """
    堡垒机用户信息
    """
    user = models.OneToOneField(verbose_name="关联用户", to=User, on_delete=models.CASCADE)
    server_account = models.ManyToManyField(to=ServerToAccount, blank=True)
    server_group = models.ManyToManyField(verbose_name="关联主机组", to=ServerGroup, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "堡垒机用户信息"


class SessionHistory(models.Model):
    """
    用户操作日志生成
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    connect = models.ForeignKey(to="ServerToAccount", on_delete=models.CASCADE)
    uid = models.CharField(verbose_name="唯一标识", max_length=32,null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s-%s"%(self.user.username,self.connect)

    class Meta:
        verbose_name_plural = "链接日志"


class SessionDetail(models.Model):
    """
    paramiko连接方式命令表
    """
    link = models.ForeignKey("SessionHistory",on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    cmd = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s-%s"%(self.cmd,self.link)

    class Meta:
        verbose_name_plural = "命令详情表"


class Token(models.Model):
    """
    token值表
    """
    connect = models.ForeignKey("ServerToAccount",on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    token = models.CharField(verbose_name="token",max_length=64,unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    logged = models.BooleanField(default=False)