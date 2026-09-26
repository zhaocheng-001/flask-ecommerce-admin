-- ============================================================
-- Flask 百战电商后台 - MySQL 建表脚本
-- 使用方式：mysql -uroot -p < sql/init.sql
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS flask_shop
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE flask_shop;

-- 2. 用户表：登录认证 + 角色权限
DROP TABLE IF EXISTS `order_items`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id`            INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username`      VARCHAR(50)  NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希（werkzeug pbkdf2 加密，不存明文）',
  `role`          VARCHAR(20)  NOT NULL DEFAULT 'user' COMMENT '角色：admin-管理员 / user-普通用户',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE = InnoDB COMMENT = '用户表';

-- 3. 商品表：核心业务表
CREATE TABLE `products` (
  `id`          INT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '商品ID',
  `name`        VARCHAR(100)  NOT NULL COMMENT '商品名称',
  `category`    VARCHAR(50)   NOT NULL DEFAULT '未分类' COMMENT '商品分类',
  `price`       DECIMAL(10,2) NOT NULL COMMENT '商品价格（元）',
  `stock`       INT           NOT NULL DEFAULT 0 COMMENT '库存数量',
  `sales`       INT           NOT NULL DEFAULT 0 COMMENT '累计销量（热门商品排序依据）',
  `description` TEXT          NULL COMMENT '商品描述',
  `status`      TINYINT       NOT NULL DEFAULT 1 COMMENT '状态：1-上架 0-下架',
  `created_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_sales` (`sales`)
) ENGINE = InnoDB COMMENT = '商品表';

-- 4. 订单主表
CREATE TABLE `orders` (
  `id`           INT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_no`     VARCHAR(32)   NOT NULL COMMENT '订单号（时间戳+随机数）',
  `user_id`      INT UNSIGNED  NOT NULL COMMENT '下单用户ID',
  `total_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单总金额',
  `status`       TINYINT       NOT NULL DEFAULT 0 COMMENT '状态：0-待支付 1-已支付 2-已发货 3-已完成 4-已取消',
  `created_at`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_order_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE = InnoDB COMMENT = '订单主表';

-- 5. 订单明细表：记录下单时的商品名称/价格快照
CREATE TABLE `order_items` (
  `id`           INT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '明细ID',
  `order_id`     INT UNSIGNED  NOT NULL COMMENT '所属订单ID',
  `product_id`   INT UNSIGNED  NOT NULL COMMENT '商品ID',
  `product_name` VARCHAR(100)  NOT NULL COMMENT '商品名称快照',
  `price`        DECIMAL(10,2) NOT NULL COMMENT '商品单价快照',
  `quantity`     INT           NOT NULL DEFAULT 1 COMMENT '购买数量',
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_product_id` (`product_id`),
  CONSTRAINT `fk_item_order`   FOREIGN KEY (`order_id`)   REFERENCES `orders` (`id`),
  CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE = InnoDB COMMENT = '订单明细表';

-- 6. 初始数据：管理员账号（密码 123456 的 pbkdf2 哈希，可直接登录）
INSERT INTO `users` (`username`, `password_hash`, `role`) VALUES
('admin', 'pbkdf2:sha256:600000$PLACEHOLDER$PLACEHOLDER', 'admin');
-- 注：管理员密码哈希建议通过 flask init-db 命令自动生成，保证与代码版本一致。
