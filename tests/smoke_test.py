# -*- coding: utf-8 -*-
"""
全接口冒烟测试：不依赖外部 MySQL/Redis
用法：
    set DATABASE_URI=sqlite:///smoke.db   (Windows)
    python tests/smoke_test.py
默认使用 SQLite，跑完自动清理。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 默认用内存 SQLite 测试（未显式指定 DATABASE_URI 时）
os.environ.setdefault("DATABASE_URI", "sqlite://")

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.user import User  # noqa: E402

app = create_app()


def seed():
    """写入测试数据：管理员 + 普通用户 + 3 个商品"""
    with app.app_context():
        db.create_all()
        admin = User(username="admin", role="admin")
        admin.set_password("123456")
        normal = User(username="zhangsan", role="user")
        normal.set_password("123456")
        db.session.add_all([admin, normal])
        db.session.add_all(
            [
                Product(name="手机", category="数码", price=4999, stock=10, sales=100),
                Product(name="耳机", category="数码", price=399, stock=50, sales=300),
                Product(name="键盘", category="外设", price=299, stock=30, sales=200),
            ]
        )
        db.session.commit()


def login(client, username="admin"):
    return client.post(
        "/api/auth/login", json={"username": username, "password": "123456"}
    )


passed = failed = 0


def check(name, resp, expect_code=0):
    global passed, failed
    body = resp.get_json()
    ok = resp.status_code == 200 and body.get("code") == expect_code
    mark = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"[{mark}] {name} -> {body}")


if __name__ == "__main__":
    seed()
    client = app.test_client()

    # 认证模块
    check("登录成功", login(client))
    check("登录失败(密码错)", client.post("/api/auth/login", json={"username": "admin", "password": "xxx"}), 1)
    check("当前用户", client.get("/api/auth/me"))

    # 商品模块
    check("商品列表", client.get("/api/products?page=1&size=2"))
    check("商品列表(关键字)", client.get("/api/products?keyword=耳"))
    check("商品详情", client.get("/api/products/1"))
    check("商品详情(不存在)", client.get("/api/products/999"), 404)
    check("新增商品", client.post("/api/products", json={"name": "鼠标", "price": 99, "stock": 10}))
    check("修改商品", client.put("/api/products/1", json={"price": 4599}))
    check("热门商品(Redis降级)", client.get("/api/products/hot?top=2"))

    # 权限校验：普通用户不能增删商品
    normal_client = app.test_client()
    login(normal_client, "zhangsan")
    check("普通用户新增商品被拦截", normal_client.post("/api/products", json={"name": "x", "price": 1}), 403)
    check("未登录访问被拦截", app.test_client().get("/api/auth/me"), 401)

    # 订单模块
    check("创建订单", client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 2}]}))
    check("创建订单(库存不足)", client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 999}]}), 1)
    check("我的订单列表", client.get("/api/orders"))
    check("订单详情", client.get("/api/orders/1"))
    check("更新订单状态", client.put("/api/orders/1/status", json={"status": 1}))
    check("接口404", client.get("/api/not-exist"), 404)

    print(f"\n结果：{passed} 通过，{failed} 失败")
    sys.exit(1 if failed else 0)
