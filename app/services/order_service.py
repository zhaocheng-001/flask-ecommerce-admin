# -*- coding: utf-8 -*-
"""订单服务：创建订单（扣库存） / 订单分页查询 / 订单详情"""
import random
import time

from ..extensions import db
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..utils.exceptions import ApiError


def _generate_order_no():
    """生成唯一订单号：时间戳 + 随机数"""
    return f"{time.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"


def create_order(user_id, data):
    """
    创建订单：
    1. 校验 items 非空，每项包含 product_id 和 quantity
    2. 逐个查询商品，校验上架状态与库存
    3. 扣减库存、写入订单主表和明细表（同一事务）
    """
    items = data.get("items")
    if not items or not isinstance(items, list):
        raise ApiError("订单明细不能为空")

    total_amount = 0.0
    order_items = []

    for item in items:
        try:
            product_id = int(item.get("product_id"))
            quantity = int(item.get("quantity", 1))
        except (TypeError, ValueError):
            raise ApiError("订单明细格式错误：product_id / quantity 必须是数字")
        if quantity <= 0:
            raise ApiError("购买数量必须大于 0")

        product = Product.query.get(product_id)
        if product is None or product.status != 1:
            raise ApiError(f"商品 {product_id} 不存在或已下架")
        if product.stock < quantity:
            raise ApiError(f"商品「{product.name}」库存不足（剩余 {product.stock}）")

        # 扣库存
        product.stock -= quantity
        product.sales += quantity
        total_amount += float(product.price) * quantity

        order_items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=quantity,
            )
        )

    order = Order(
        order_no=_generate_order_no(),
        user_id=user_id,
        total_amount=round(total_amount, 2),
        status=Order.STATUS_PENDING,
    )
    order.items = order_items
    db.session.add(order)
    db.session.commit()
    return order.to_dict()


def list_orders(user_id, page=1, size=10):
    """订单分页查询（按当前登录用户过滤）"""
    query = Order.query.filter_by(user_id=user_id)
    pagination = query.order_by(Order.id.desc()).paginate(
        page=page, per_page=size, error_out=False
    )
    return {
        "list": [o.to_dict() for o in pagination.items],
        "total": pagination.total,
        "page": page,
        "size": size,
    }


def get_order(order_id, user_id, is_admin=False):
    """订单详情：普通用户只能看自己的订单，管理员可看全部"""
    order = Order.query.get(order_id)
    if order is None:
        raise ApiError("订单不存在", code=404)
    if not is_admin and order.user_id != user_id:
        raise ApiError("无权限查看该订单", code=403)
    return order.to_dict()


def update_order_status(order_id, status, user_id, is_admin=False):
    """更新订单状态（管理员权限）"""
    if status not in Order.STATUS_MAP:
        raise ApiError("非法的订单状态")
    order = Order.query.get(order_id)
    if order is None:
        raise ApiError("订单不存在", code=404)
    if not is_admin and order.user_id != user_id:
        raise ApiError("无权限操作该订单", code=403)
    order.status = status
    db.session.commit()
    return order.to_dict()
