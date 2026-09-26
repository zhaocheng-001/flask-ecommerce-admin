# -*- coding: utf-8 -*-
"""用户模型：登录认证 + 密码加密（werkzeug）"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment="用户名")
    password_hash = db.Column(db.String(255), nullable=False, comment="密码哈希（werkzeug 加密）")
    role = db.Column(db.String(20), default="user", nullable=False, comment="角色：admin-管理员 / user-普通用户")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    def set_password(self, raw_password):
        """明文密码加密存储（werkzeug 的 pbkdf2 算法）"""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """校验明文密码是否与哈希一致"""
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
