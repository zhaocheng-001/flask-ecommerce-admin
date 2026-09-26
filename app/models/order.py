# -*- coding: utf-8 -*-
"""订单模型：订单主表 + 订单明细表，一对多关系"""
from datetime import datetime

from ..extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    # 订单状态：0-待支付 1-已支付 2-已发货 3-已完成 4-已取消
    STATUS_PENDING = 0
    STATUS_PAID = 1
    STATUS_SHIPPED = 2
    STATUS_DONE = 3
    STATUS_CANCELED = 4

    STATUS_MAP = {
        0: "待支付",
        1: "已支付",
        2: "已发货",
        3: "已完成",
        4: "已取消",
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False, comment="订单号")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, comment="下单用户 id")
    total_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False, comment="订单总金额")
    status = db.Column(db.SmallInteger, default=0, nullable=False, comment="订单状态")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="下单时间")

    # 一对多：一个订单包含多条明细
    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "user_id": self.user_id,
            "total_amount": float(self.total_amount),
            "status": self.status,
            "status_text": self.STATUS_MAP.get(self.status, "未知"),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, comment="所属订单 id")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, comment="商品 id")
    product_name = db.Column(db.String(100), nullable=False, comment="下单时商品名称快照")
    price = db.Column(db.Numeric(10, 2), nullable=False, comment="下单时商品单价快照")
    quantity = db.Column(db.Integer, default=1, nullable=False, comment="购买数量")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": float(self.price),
            "quantity": self.quantity,
        }
