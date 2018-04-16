import uuid
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from src import unicode_id


@login_required
def index(request):
    """
    主页
    :param request:
    :return:
    """
    return render(request, "index.html")


def user_login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_obj = authenticate(username=username, password=password)
        error_msg = ""
        if user_obj:
            login(request, user_obj)
            return redirect(request.GET.get("next") or "/")
        else:
            error_msg = "用户名或密码错误"
            return render(request, "login.html", {"error_msg": error_msg})


@login_required
def user_logout(request):
    """
    用户登出
    :param request:
    :return:
    """
    logout(request)
    return redirect("/login/")


@login_required
def hostlist(request):
    """
    主机列表页面
    :param request:
    :return:
    """
    return render(request,"hostlist.html")

@login_required
def multicmd(request):
    """
    批量命令页面
    :param request:
    :return:
    """
    return render(request,"multicmd.html")


@login_required
def multifile(request):
    """
    批量文件页面
    :param request: 请求文件，类型request.obj
    :return:
    """
    uid = uuid.uuid4()
    return render(request,"multifile.html",{"uid":uid})