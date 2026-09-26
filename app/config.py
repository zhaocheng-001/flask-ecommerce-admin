# -*- coding: utf-8 -*-
"""应用配置：数据库、Redis、密钥等，支持环境变量覆盖"""
import os


class Config:
    # session 签名密钥，生产环境务必通过环境变量设置
    SECRET_KEY = os.getenv("SECRET_KEY", "flask-shop-secret-key")

    # MySQL 连接：请把 root/123456 改成自己的数据库账号密码
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "mysql+pymysql://root:12345@localhost:3306/flask_shop?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Redis（热门商品缓存用），Redis 未启动时程序会自动降级直查 MySQL
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    # 热门商品缓存有效期（秒）
    HOT_PRODUCT_CACHE_TTL = 60


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# 通过环境变量 APP_ENV 切换配置，默认开发环境
config_map = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
}


def get_config():
    return config_map.get(os.getenv("APP_ENV", "dev"), DevelopmentConfig)
