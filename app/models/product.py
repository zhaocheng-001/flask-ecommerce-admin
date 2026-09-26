# -*- coding: utf-8 -*-
"""商品模型：对应 MySQL 中的 products 表"""
from datetime import datetime

from ..extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment="商品名称")
    category = db.Column(db.String(50), default="未分类", comment="商品分类")
    price = db.Column(db.Numeric(10, 2), nullable=False, comment="商品价格（元）")
    stock = db.Column(db.Integer, default=0, nullable=False, comment="库存数量")
    sales = db.Column(db.Integer, default=0, nullable=False, comment="累计销量（热门排序依据）")
    description = db.Column(db.Text, comment="商品描述")
    status = db.Column(db.SmallInteger, default=1, comment="状态：1-上架 0-下架")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": float(self.price),
            "stock": self.stock,
            "sales": self.sales,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
