# -*- coding: utf-8 -*-
"""统一返回体：所有接口都返回 {code, msg, data} 三段式结构"""
from flask import jsonify


def ok(data=None, msg="success"):
    """成功返回，code=0 表示业务成功"""
    return jsonify({"code": 0, "msg": msg, "data": data})


def fail(code=1, msg="error", data=None):
    """失败返回，code 非 0 表示业务失败"""
    return jsonify({"code": code, "msg": msg, "data": data})
