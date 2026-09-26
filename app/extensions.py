# -*- coding: utf-8 -*-
"""扩展实例集中创建，避免循环导入"""
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cors = CORS()
