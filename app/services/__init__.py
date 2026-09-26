# -*- coding: utf-8 -*-
"""服务层统一出口"""
from . import order_service, product_service, user_service

__all__ = ["user_service", "product_service", "order_service"]
