# -*- coding: utf-8 -*-
"""商品服务：新增 / 列表 / 详情 / 修改 / 删除 / 热门缓存"""
import json

import redis as redis_lib
from flask import current_app

from ..extensions import db
from ..models.product import Product
from ..utils.exceptions import ApiError

# 模块级 Redis 客户端，进程内复用连接
_redis_client = None


def _get_redis():
    """获取 Redis 客户端（懒加载）；连接超时设为 1 秒，Redis 未启动时快速失败"""
    global _redis_client
    if _redis_client is None:
        cfg = current_app.config
        _redis_client = redis_lib.Redis(
            host=cfg["REDIS_HOST"],
            port=cfg["REDIS_PORT"],
            db=cfg["REDIS_DB"],
            socket_connect_timeout=1,
            decode_responses=True,
        )
    return _redis_client


def create_product(data):
    """新增商品（管理员权限），data 校验通过后入库"""
    name = (data.get("name") or "").strip()
    if not name:
        raise ApiError("商品名称不能为空")

    try:
        price = float(data.get("price"))
        if price < 0:
            raise ValueError
    except (TypeError, ValueError):
        raise ApiError("价格必须是不小于 0 的数字")

    product = Product(
        name=name,
        category=(data.get("category") or "未分类").strip(),
        price=price,
        stock=int(data.get("stock") or 0),
        description=data.get("description") or "",
        status=int(data.get("status", 1)),
    )
    db.session.add(product)
    db.session.commit()
    return product.to_dict()


def list_products(page=1, size=10, keyword=None, category=None):
    """商品分页列表：支持按名称关键字、分类筛选"""
    query = Product.query
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category:
        query = query.filter(Product.category == category)

    pagination = query.order_by(Product.id.desc()).paginate(
        page=page, per_page=size, error_out=False
    )
    return {
        "list": [p.to_dict() for p in pagination.items],
        "total": pagination.total,
        "page": page,
        "size": size,
    }


def get_product(product_id):
    """商品详情"""
    product = Product.query.get(product_id)
    if product is None:
        raise ApiError("商品不存在", code=404)
    return product.to_dict()


def update_product(product_id, data):
    """修改商品（管理员权限）"""
    product = Product.query.get(product_id)
    if product is None:
        raise ApiError("商品不存在", code=404)

    if "name" in data and (data.get("name") or "").strip():
        product.name = data["name"].strip()
    if "category" in data and (data.get("category") or "").strip():
        product.category = data["category"].strip()
    if "price" in data:
        try:
            price = float(data["price"])
            if price < 0:
                raise ValueError
            product.price = price
        except (TypeError, ValueError):
            raise ApiError("价格必须是不小于 0 的数字")
    if "stock" in data:
        product.stock = int(data["stock"] or 0)
    if "description" in data:
        product.description = data["description"] or ""
    if "status" in data:
        product.status = int(data["status"])

    db.session.commit()
    return product.to_dict()


def delete_product(product_id):
    """删除商品（管理员权限）"""
    product = Product.query.get(product_id)
    if product is None:
        raise ApiError("商品不存在", code=404)
    db.session.delete(product)
    db.session.commit()


def hot_products(top=10):
    """
    热门商品列表：按销量倒序取前 N 条。
    优先读 Redis 缓存（key = hot_products:{top}，TTL 60 秒），
    Redis 未启动 / 异常时自动降级直查 MySQL，保证接口可用。
    返回 (数据, 是否命中缓存)。
    """
    cache_key = f"hot_products:{top}"
    ttl = current_app.config["HOT_PRODUCT_CACHE_TTL"]

    def query_db():
        rows = (
            Product.query.filter_by(status=1)
            .order_by(Product.sales.desc(), Product.id.desc())
            .limit(top)
            .all()
        )
        return [p.to_dict() for p in rows]

    try:
        client = _get_redis()
        cached = client.get(cache_key)
        if cached:
            return json.loads(cached), True
        data = query_db()
        client.setex(cache_key, ttl, json.dumps(data, ensure_ascii=False))
        return data, False
    except Exception:
        # Redis 不可用：降级直查数据库
        return query_db(), False
