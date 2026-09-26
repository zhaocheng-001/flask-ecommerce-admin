# Flask 百战电商后台

基于 Flask 的最小可用电商后端：包含用户认证（session + 密码加密）、商品管理、订单管理，热门商品列表使用 Redis 缓存（未启动 Redis 自动降级直查 MySQL），全部接口采用统一返回体，配套 Postman 测试集合。

## 技术栈

| 类别 | 选型 |
| ---- | ---- |
| Web 框架 | Flask 3.x + 蓝图 Blueprint |
| 数据库 | MySQL 8.x（SQLAlchemy ORM） |
| 缓存 | Redis（热门商品列表，60 秒 TTL，可降级） |
| 认证 | Flask session + werkzeug 密码哈希 |
| 权限 | 自定义装饰器 `login_required` / `admin_required` |
| 测试 | Postman（集合见 `postman/` 目录） |

## 项目结构（三层架构 model / service / api）

```
flask-ecommerce-admin/
├── app/
│   ├── __init__.py          # 应用工厂：扩展初始化、蓝图注册、全局异常捕获
│   ├── config.py            # 配置类（MySQL / Redis / 密钥，支持环境变量覆盖）
│   ├── extensions.py        # db、cors 扩展实例，避免循环导入
│   ├── cli.py               # 自定义命令：flask init-db 建表 + 写入初始数据
│   ├── api/                 # 接口层：只做参数接收和返回，不含业务逻辑
│   │   ├── user_api.py      #   认证蓝图 /api/auth/*
│   │   ├── product_api.py   #   商品蓝图 /api/products/*
│   │   └── order_api.py     #   订单蓝图 /api/orders/*
│   ├── services/            # 服务层：业务逻辑、事务、缓存
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   └── order_service.py
│   ├── models/              # 模型层：ORM 表定义
│   │   ├── user.py          #   用户表
│   │   ├── product.py       #   商品表
│   │   └── order.py         #   订单主表 + 订单明细表
│   └── utils/               # 工具层
│       ├── responses.py     #   统一返回体 {code, msg, data}
│       ├── exceptions.py    #   自定义业务异常 ApiError
│       └── decorators.py    #   登录 / 管理员权限装饰器
├── sql/init.sql             # MySQL 建表脚本（含索引与外键设计）
├── postman/                 # Postman 接口测试集合（导入即用）
├── docs/项目口述文档.md      # 面试/汇报口述稿
├── run.py                   # 启动入口
├── requirements.txt
└── .gitignore
```

## 快速开始

### 1. 准备环境

- Python 3.10+
- MySQL 8.x（已启动）
- Redis（可选，不启动也能跑，热门接口自动降级）

### 2. 安装依赖

```bash
cd flask-ecommerce-admin
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置数据库

修改 `app/config.py` 中的 MySQL 连接串（或用环境变量 `DATABASE_URI`）：

```
mysql+pymysql://root:你的密码@localhost:3306/flask_shop?charset=utf8mb4
```

### 4. 初始化数据并启动

```bash
# 建表 + 写入管理员账号(admin/123456) + 8 条示例商品
flask --app run.py init-db

# 启动服务
python run.py
```

看到 `Running on http://127.0.0.1:5000` 即启动成功。

### 5. Postman 测试

1. 导入 `postman/Flask百战电商后台.postman_collection.json`
2. 先调用 **登录（admin）** 接口，Postman 自动保存 session Cookie
3. 依次测试商品、订单各接口

## 接口一览

统一返回体：`{"code": 0, "msg": "success", "data": {...}}`，`code=0` 成功，非 0 失败。

| 方法 | 路径 | 说明 | 权限 |
| ---- | ---- | ---- | ---- |
| POST | `/api/auth/login` | 登录 | 公开 |
| POST | `/api/auth/logout` | 登出 | 登录 |
| GET | `/api/auth/me` | 当前用户信息 | 登录 |
| GET | `/api/products` | 商品分页列表（keyword/category 筛选） | 登录 |
| POST | `/api/products` | 新增商品 | 管理员 |
| GET | `/api/products/hot` | 热门商品（Redis 缓存 60s） | 公开 |
| GET | `/api/products/<id>` | 商品详情 | 登录 |
| PUT | `/api/products/<id>` | 修改商品 | 管理员 |
| DELETE | `/api/products/<id>` | 删除商品 | 管理员 |
| POST | `/api/orders` | 创建订单（扣库存，事务） | 登录 |
| GET | `/api/orders` | 我的订单分页 | 登录 |
| GET | `/api/orders/<id>` | 订单详情（本人或管理员） | 登录 |
| PUT | `/api/orders/<id>/status` | 更新订单状态 | 管理员 |

## 核心设计说明

- **密码安全**：使用 werkzeug 的 `generate_password_hash`（pbkdf2:sha256）加密存储，校验用 `check_password_hash`，数据库不存明文。
- **权限控制**：session 保存登录态，`admin_required` 装饰器拦截非管理员请求，返回 403。
- **事务一致性**：创建订单时「查商品 → 校验库存 → 扣库存 → 写订单+明细」在同一个 SQLAlchemy 事务中提交。
- **Redis 缓存**：热门商品按销量倒序缓存 60 秒（key = `hot_products:{top}`）；Redis 连接失败时自动降级直查 MySQL，接口永远可用；返回体中 `from_cache` 字段可验证缓存是否命中。
- **统一异常处理**：业务代码只需 `raise ApiError("xxx")`，全局 errorhandler 统一捕获后返回固定格式 JSON，404/405/500 同样接管。
