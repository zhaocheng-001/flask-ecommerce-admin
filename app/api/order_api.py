# -*- coding: utf-8 -*-
"""订单接口蓝图：创建 / 查询 / 详情 / 状态更新"""
from flask import Blueprint, g, request

from ..services import order_service
from ..utils.decorators import admin_required, login_required
from ..utils.responses import ok

order_bp = Blueprint("order", __name__, url_prefix="/api/orders")


@order_bp.post("")
@login_required
def create_order():
    """
    创建订单：POST /api/orders
    body: {"items": [{"product_id": 1, "quantity": 2}, ...]}
    """
    data = request.get_json(silent=True) or {}
    return ok(order_service.create_order(g.user_id, data), "订单创建成功")


@order_bp.get("")
@login_required
def list_orders():
    """我的订单分页查询：GET /api/orders?page=1&size=10"""
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    return ok(order_service.list_orders(g.user_id, page, size))


@order_bp.get("/<int:order_id>")
@login_required
def get_order(order_id):
    """订单详情：GET /api/orders/<id>（仅本人或管理员可见）"""
    return ok(order_service.get_order(order_id, g.user_id, is_admin=(g.role == "admin")))


@order_bp.put("/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
    """更新订单状态（管理员）：PUT /api/orders/<id>/status  body: {"status": 1}"""
    data = request.get_json(silent=True) or {}
    return ok(
        order_service.update_order_status(order_id, data.get("status"), g.user_id, is_admin=True),
        "订单状态更新成功",
    )
