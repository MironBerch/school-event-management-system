command = '/usr/bin/gunicorn'
pythonpath = '/app'
bind = '0.0.0.0:8000'
workers = 1
limit_request_fields = 32000
limit_request_field_size = 0
