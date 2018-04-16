from django.contrib import admin
from backend import models

admin.site.register(models.ServerGroup)
admin.site.register(models.Server)
admin.site.register(models.ServerToAccount)
admin.site.register(models.ServerAccount)
admin.site.register(models.IDC)
admin.site.register(models.AuditAccount)
admin.site.register(models.SessionHistory)
admin.site.register(models.SessionDetail)
admin.site.register(models.Token)
admin.site.register(models.MultipleLog)
admin.site.register(models.MultipleHistory)
