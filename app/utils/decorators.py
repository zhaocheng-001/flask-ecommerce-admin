# -*- coding: utf-8 -*-
"""登录认证与权限校验装饰器（基于 Flask session）"""
from functools import wraps

from ..utils.exceptions import ApiError


def login_required(view):
    """登录校验：session 中必须有 user_id"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session_user_id():
            raise ApiError("请先登录", code=401)
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """管理员权限校验：必须登录且 role 为 admin"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session_user_id():
            raise ApiError("请先登录", code=401)
        if session_role() != "admin":
            raise ApiError("无权限，该操作仅管理员可用", code=403)
        return view(*args, **kwargs)

    return wrapped


def session_user_id():
    from flask import session

    return session.get("user_id")


def session_role():
    from flask import session

    return session.get("role")
