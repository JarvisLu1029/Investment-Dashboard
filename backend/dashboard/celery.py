from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 設置 Django 的預設設定模組
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

app = Celery('tasks')

# 使用 Django 的設定文件來配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動從所有已註冊的 Django app 加載任務
app.autodiscover_tasks()

