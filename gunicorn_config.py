# Gunicorn 配置文件
import os
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 2
timeout = 120
limit_request_line = 0
limit_request_field_size = 0
limit_request_fields = 0
