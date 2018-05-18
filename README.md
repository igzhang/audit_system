项目介绍
=================
简介：
python全栈模块9--IT审计+主机管理作业
根据alex大王所讲审计系统制作
***

# 一、环境依赖
    Linux
	python3.6
	sshpass
	shellinabox
	paramiko
	subprocess
	django2.0
	openssh（可选）
***

# 二、功能介绍

## 2.1 后台页面

### 2.1.1 批量上传下载文件
    依赖模块：paramiko  
    实现功能：对选对主机同时上传、下载同一文件

### 2.1.2 批量执行shell命令
	依赖模块：subprocess
	实现功能：对选对主机同时执行同一shell命令

### 2.1.3 网页shell页面
	依赖模块：shellinabox
	实现功能：网页执行shell互动界面

## 2.2 cmd/shell交互界面
	运行：python3 audit.py

### 2.2.1 通过ssh登陆主机
#### 2.2.1.1 通过更改paramiko源码方式
	存放：
	    更改后模块保存在lib--paramiko_master
	使用：
	    audit--settings里设置SSH_MODE = "paramiko"

#### 2.2.1.2 通过更改ssh源码方式
	存放：
		更改后源码保存在lib--openssh-7.6sp1
	使用：
		1、需要先安装修改后的ssh编码
		2、shell脚本src--strace.sh需要添加运行权限
***

# 三、测试账户
	审计系统账户：
		用户名：zhang
		密码：1234567a
		django-admin也可以使用
	堡垒机账户需要在Linux自行设置
***

# 四、不足之处
	通过paramiko源码方式登陆时，使用tab补足命令，日志记录TCP存在粘包问题
