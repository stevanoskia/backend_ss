command = '/var/www/143.198.153.179-api/backend_sx/venv/bin/gunicorn'
pythonpath = '/var/www/143.198.153.179-api'
bind = '0.0.0.0:8000'
workers = 4
timeout = 60
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
