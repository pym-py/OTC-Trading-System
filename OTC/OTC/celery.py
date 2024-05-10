import os
from celery import Celery

# 加载配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OTC.settings')
# 创建celery app
app = Celery('django_celery')
app.config_from_object('django.conf:settings', namespace='CELERY')
# 自动发现项目中的tasks
app.autodiscover_tasks()
