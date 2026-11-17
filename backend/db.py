# -*- coding: utf-8 -*-
"""
数据库模块：封装 pymysql 连接，提供轻量查询/执行工具。
- 每次操作新建连接并及时关闭，避免长连接断开问题；
- 使用参数化查询防止 SQL 注入。
"""
import pymysql
import pymysql.cursors
from config import config


def get_conn():
    """获取一个新的数据库连接（调用方负责关闭）。"""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset=config.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def query_one(sql, args=None):
    """查询单条记录，返回 dict 或 None。"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()
    finally:
        conn.close()


def query_all(sql, args=None):
    """查询多条记录，返回 dict 列表。"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, args=None):
    """执行 INSERT/UPDATE/DELETE，返回 lastrowid 与受影响行数。"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            affected = cur.execute(sql, args or ())
            last_id = cur.lastrowid
        conn.commit()
        return last_id, affected
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
