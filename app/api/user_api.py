# -*- coding: utf-8 -*-
"""认证接口蓝图：登录 / 登出 / 当前用户"""
from flask import Blueprint, request

from ..services import user_service
from ..utils.responses import ok

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """登录：POST /api/auth/login  body: {"username": "...", "password": "..."}"""
    data = request.get_json(silent=True) or {}
    user = user_service.login(data.get("username"), data.get("password"))
    return ok(user, "登录成功")


@auth_bp.post("/logout")
def logout():
    """登出：POST /api/auth/logout"""
    user_service.logout()
    return ok(msg="已退出登录")


@auth_bp.get("/me")
def me():
    """当前登录用户：GET /api/auth/me"""
    user = user_service.current_user()
    return ok(user)
