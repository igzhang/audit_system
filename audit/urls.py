"""audit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from backend import views
from backend import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.user_login),
    path('logout/', views.user_logout),
    path('hostlist.html', views.hostlist),
    path('multicmd.html', views.multicmd),
    path('api/grouplist', api.GroupList.as_view()),
    path('api/hostlist', api.HostList.as_view()),
    path('api/hostlistall', api.HostListAll.as_view()),
    path('api/token', api.token),
    path('', views.index),

]
