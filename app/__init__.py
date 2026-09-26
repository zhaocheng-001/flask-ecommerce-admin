# -*- coding: utf-8 -*-
"""应用工厂：初始化扩展、蓝图、全局异常处理、请求钩子"""
from flask import Flask, g, session

from .config import get_config
from .extensions import cors, db
from .utils.exceptions import ApiError
from .utils.responses import fail


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # 1. 初始化扩展
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)  # 允许跨域携带 session cookie

    # 2. 注册蓝图
    from .api import register_blueprints

    register_blueprints(app)

    # 3. 注册自定义 CLI 命令（flask init-db）
    from .cli import register_commands

    register_commands(app)

    # 4. 请求钩子：把 session 中的登录信息注入 g，供各接口直接使用
    @app.before_request
    def load_current_user():
        g.user_id = session.get("user_id")
        g.role = session.get("role")

    # 5. 首页：项目欢迎页，展示接口清单
    @app.get("/")
    def index():
        return _INDEX_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

    # 6. 统一异常捕获：保证任何异常都返回统一格式的 JSON
    _register_error_handlers(app)

    return app


_INDEX_HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>Flask 百战电商后台</title>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; background: #f5f7fa; margin: 0; padding: 40px; }
  .card { max-width: 860px; margin: 0 auto; background: #fff; border-radius: 12px;
          box-shadow: 0 2px 12px rgba(0,0,0,.08); padding: 32px 40px; }
  h1 { margin: 0 0 4px; color: #1f2d3d; } .sub { color: #909399; margin-bottom: 24px; }
  .badge { display: inline-block; background: #409eff; color: #fff; border-radius: 4px;
           font-size: 12px; padding: 2px 8px; margin-right: 8px; }
  .badge.admin { background: #e6a23c; } .badge.pub { background: #67c23a; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #ebeef5; font-size: 14px; }
  th { background: #f5f7fa; color: #606266; }
  code { background: #f0f2f5; padding: 2px 6px; border-radius: 4px; color: #c7254e; }
  .tip { margin-top: 20px; padding: 14px 16px; background: #f0f9eb; border-radius: 8px;
         color: #67c23a; font-size: 14px; }
</style>
</head>
<body>
<div class="card">
  <h1>🛒 Flask 百战电商后台</h1>
  <div class="sub">Flask + MySQL + Redis ｜ 统一返回体 {code, msg, data} ｜ 服务运行中</div>
  <table>
    <tr><th>模块</th><th>方法</th><th>接口</th><th>说明</th><th>权限</th></tr>
    <tr><td>认证</td><td>POST</td><td><code>/api/auth/login</code></td><td>登录</td><td>公开</td></tr>
    <tr><td>认证</td><td>GET</td><td><code>/api/auth/me</code></td><td>当前用户</td><td>登录</td></tr>
    <tr><td>商品</td><td>GET</td><td><code>/api/products</code></td><td>分页列表（keyword/category）</td><td>登录</td></tr>
    <tr><td>商品</td><td>GET</td><td><code>/api/products/hot</code></td><td>热门商品（Redis 缓存 60s）</td><td>公开</td></tr>
    <tr><td>商品</td><td>POST</td><td><code>/api/products</code></td><td>新增商品</td><td>管理员</td></tr>
    <tr><td>商品</td><td>GET</td><td><code>/api/products/&lt;id&gt;</code></td><td>商品详情</td><td>登录</td></tr>
    <tr><td>商品</td><td>PUT / DELETE</td><td><code>/api/products/&lt;id&gt;</code></td><td>修改 / 删除</td><td>管理员</td></tr>
    <tr><td>订单</td><td>POST</td><td><code>/api/orders</code></td><td>创建订单（事务扣库存）</td><td>登录</td></tr>
    <tr><td>订单</td><td>GET</td><td><code>/api/orders</code></td><td>我的订单</td><td>登录</td></tr>
    <tr><td>订单</td><td>PUT</td><td><code>/api/orders/&lt;id&gt;/status</code></td><td>状态流转</td><td>管理员</td></tr>
  </table>
  <div class="tip">测试账号：管理员 <b>admin / 123456</b> ｜ 先登录拿到 session Cookie，再用 Postman 测其余接口</div>
</div>
</body>
</html>"""


def _register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        """业务异常：抛 ApiError 的地方都会被这里接住"""
        return fail(e.code, e.message)

    @app.errorhandler(404)
    def handle_404(_):
        return fail(404, "接口不存在")

    @app.errorhandler(405)
    def handle_405(_):
        return fail(405, "请求方法不允许")

    @app.errorhandler(400)
    def handle_400(_):
        return fail(400, "请求参数错误")

    @app.errorhandler(Exception)
    def handle_exception(e):
        """兜底异常：记录日志并返回 500，避免向前端暴露堆栈"""
        app.logger.exception(e)
        return fail(500, "服务器内部错误")
