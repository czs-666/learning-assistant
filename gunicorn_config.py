# Gunicorn 配置文件
bind = "0.0.0.0:5000"
workers = 2
timeout = 120
limit_request_line = 0
limit_request_field_size = 0
limit_request_fields = 0
