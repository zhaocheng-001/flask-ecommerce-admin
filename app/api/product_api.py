# -*- coding: utf-8 -*-
"""商品接口蓝图：增删改查 + 热门列表（Redis 缓存）"""
from flask import Blueprint, request

from ..services import product_service
from ..utils.decorators import admin_required, login_required
from ..utils.responses import ok

product_bp = Blueprint("product", __name__, url_prefix="/api/products")


@product_bp.get("")
@login_required
def list_products():
    """商品分页列表：GET /api/products?page=1&size=10&keyword=xx&category=xx"""
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    keyword = request.args.get("keyword")
    category = request.args.get("category")
    return ok(product_service.list_products(page, size, keyword, category))


@product_bp.post("")
@admin_required
def create_product():
    """新增商品（管理员）：POST /api/products"""
    data = request.get_json(silent=True) or {}
    return ok(product_service.create_product(data), "商品创建成功")


@product_bp.get("/hot")
def hot_products():
    """
    热门商品：GET /api/products/hot?top=10
    优先走 Redis 缓存（60 秒），Redis 不可用时自动降级查 MySQL
    """
    top = request.args.get("top", 10, type=int)
    data, from_cache = product_service.hot_products(top)
    return ok({"list": data, "from_cache": from_cache})


@product_bp.get("/<int:product_id>")
@login_required
def get_product(product_id):
    """商品详情：GET /api/products/<id>"""
    return ok(product_service.get_product(product_id))


@product_bp.put("/<int:product_id>")
@admin_required
def update_product(product_id):
    """修改商品（管理员）：PUT /api/products/<id>"""
    data = request.get_json(silent=True) or {}
    return ok(product_service.update_product(product_id, data), "商品更新成功")


@product_bp.delete("/<int:product_id>")
@admin_required
def delete_product(product_id):
    """删除商品（管理员）：DELETE /api/products/<id>"""
    product_service.delete_product(product_id)
    return ok(msg="商品删除成功")
