# -*- coding: utf-8 -*-
"""用户服务：登录 / 登出 / 当前用户信息"""
from flask import session

from ..models.user import User
from ..utils.exceptions import ApiError


def login(username, password):
    """账号密码登录，校验成功后把用户信息写入 session"""
    if not username or not password:
        raise ApiError("用户名和密码不能为空")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        raise ApiError("用户名或密码错误")

    # 将登录态写入 session（服务端保存，浏览器通过 cookie 关联）
    session["user_id"] = user.id
    session["username"] = user.username
    session["role"] = user.role
    session.permanent = True
    return user.to_dict()


def logout():
    """登出：清空 session"""
    session.clear()


def current_user():
    """获取当前登录用户信息"""
    user_id = session.get("user_id")
    if not user_id:
        raise ApiError("请先登录", code=401)

    user = User.query.get(user_id)
    if user is None:
        session.clear()
        raise ApiError("登录状态失效，请重新登录", code=401)
    return user.to_dict()
