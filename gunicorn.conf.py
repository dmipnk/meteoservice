# gunicorn.conf.py
import multiprocessing

# Базовые настройки
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Таймауты
timeout = 30
graceful_timeout = 30
keepalive = 2

# Перезапуск воркеров
max_requests = 1000
max_requests_jitter = 100

# Производительность
preload_app = True

# Логирование
accesslog = "-"  # в stdout
errorlog = "-"   # в stdout
loglevel = "info"

# Имя процесса
proc_name = "meteoservice"