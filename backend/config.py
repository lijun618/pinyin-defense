# -*- coding: utf-8 -*-
"""
配置模块：从 backend/.env 读取数据库与服务配置。
迁移到云服务器时，只需修改 .env，无需改动任何代码。
"""
import os
from dotenv import load_dotenv

# 以本文件所在目录为基准加载 .env（保证任意工作目录下启动都能读到）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    # MySQL 连接配置
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "pinyin_war_game")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

    # FastAPI 服务配置
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))


config = Config()
