# -*- coding: utf-8 -*-
"""项目启动入口：python run.py"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True 仅开发环境使用，生产环境请用 gunicorn 等部署
    app.run(host="0.0.0.0", port=5000, debug=True)
