import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Создаем экземпляр приложения Celery
app = Celery('backend')

# Загружаем конфигурацию из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем и регистрируем задачи из всех приложений
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 