# -*- coding: utf-8 -*-
"""自定义 CLI 命令：flask init-db 一键建表 + 写入初始数据"""
import click

from .extensions import db
from .models.product import Product
from .models.user import User


def register_commands(app):
    @app.cli.command("init-db")
    @click.option("--force", is_flag=True, help="删除已有表后重建（会清空数据）")
    def init_db(force):
        """创建数据表，并写入管理员账号与示例商品"""
        if force:
            db.drop_all()
            click.echo("已删除旧表。")

        db.create_all()
        click.echo("数据表创建完成。")

        # 写入管理员账号（已存在则跳过）
        if User.query.filter_by(username="admin").first() is None:
            admin = User(username="admin", role="admin")
            admin.set_password("123456")
            db.session.add(admin)
            click.echo("已创建管理员账号：admin / 123456")

        # 写入示例商品（表为空时才写入）
        if Product.query.count() == 0:
            samples = [
                Product(name="iPhone 16 Pro", category="手机数码", price=8999, stock=50, sales=320, description="苹果旗舰手机"),
                Product(name="华为 Mate 70", category="手机数码", price=6499, stock=80, sales=280, description="华为旗舰手机"),
                Product(name="小米手环 9", category="智能穿戴", price=249, stock=200, sales=560, description="高性价比手环"),
                Product(name="AirPods Pro 3", category="数码配件", price=1899, stock=120, sales=410, description="主动降噪耳机"),
                Product(name="机械键盘 K870", category="电脑外设", price=399, stock=150, sales=190, description="青轴机械键盘"),
                Product(name="27 寸 4K 显示器", category="电脑外设", price=1599, stock=60, sales=150, description="4K IPS 面板"),
                Product(name="罗技 G502 鼠标", category="电脑外设", price=299, stock=180, sales=470, description="电竞游戏鼠标"),
                Product(name="USB-C 快充数据线", category="数码配件", price=29, stock=500, sales=880, description="100W 快充线"),
            ]
            db.session.add_all(samples)
            click.echo(f"已写入 {len(samples)} 条示例商品")

        db.session.commit()
        click.echo("初始化完成！")
