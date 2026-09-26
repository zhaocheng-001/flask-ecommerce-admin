# -*- coding: utf-8 -*-
"""蓝图注册中心：所有 API 蓝图在此统一注册"""
from .order_api import order_bp
from .product_api import product_bp
from .user_api import auth_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
