# -*- coding: utf-8 -*-
"""
拼音战机 · FastAPI 后端主程序
================================
接口清单：
  POST /register          注册（用户名查重 + 密码 bcrypt 哈希入库）
  POST /login             登录（校验用户名与密码哈希）
  POST /save_game_record  保存本局对局记录到 game_records
  GET  /get_rank          全局排行榜 Top10（按最高分降序）
  GET  /health            健康检查

启动命令：
  cd backend
  python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""
from typing import Optional
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from db import query_one, query_all, execute
from security import hash_password, verify_password

# ========== 用户名规则（前后端保持一致）==========
# 允许：中文（基本区 + 扩展A）、英文字母、数字、下划线。
# 长度按"字符数"计：数据库为 utf8mb4 VARCHAR(32)，一个汉字占 1 个字符位，
# 与前端 input maxlength / JS 字符串长度、Python len() 完全一致。
USERNAME_RE = re.compile(r"^[A-Za-z0-9_\u3400-\u4DBF\u4E00-\u9FFF]{3,32}$")
USERNAME_RULE = "用户名只能包含中文、字母、数字、下划线，长度 3-32 位"

app = FastAPI(title="拼音战机 API", version="1.0.0")

# ========== 跨域处理（CORS）==========
# 允许前端 file:// 双击打开 或 http://localhost 访问后端。
# 生产环境可把 "*" 收敛为你的域名，例如 ["https://game.example.com"]。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 请求体模型 ==========
class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=6, max_length=64)

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        """去除首尾空格并校验字符集，避免只靠前端挡住非法用户名。"""
        v = v.strip()
        if not USERNAME_RE.match(v):
            raise ValueError(USERNAME_RULE)
        return v


class LoginIn(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()


class RecordIn(BaseModel):
    user_id: int
    total_score: int = Field(..., ge=0)
    correct_rate: float = Field(..., ge=0, le=100)
    play_duration: int = Field(..., ge=0, description="游玩时长(秒)")


# ========== 接口1：注册 ==========
@app.post("/register")
def register(body: RegisterIn):
    # 1) 用户名查重
    exists = query_one("SELECT user_id FROM users WHERE username=%s", (body.username,))
    if exists:
        return {"ok": False, "msg": "用户名已存在"}

    # 2) 密码哈希后入库（绝不存明文）
    hashed = hash_password(body.password)
    user_id, _ = execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (body.username, hashed),
    )
    return {"ok": True, "user": {"user_id": user_id, "username": body.username}}


# ========== 接口2：登录 ==========
@app.post("/login")
def login(body: LoginIn):
    row = query_one(
        "SELECT user_id, username, password_hash FROM users WHERE username=%s",
        (body.username,),
    )
    if not row:
        return {"ok": False, "msg": "用户名或密码错误"}
    if not verify_password(body.password, row["password_hash"]):
        return {"ok": False, "msg": "用户名或密码错误"}
    return {"ok": True, "user": {"user_id": row["user_id"], "username": row["username"]}}


# ========== 接口3：保存对局记录 ==========
@app.post("/save_game_record")
def save_game_record(body: RecordIn):
    # 校验用户存在（外键约束也会兜底，这里提前给出友好提示）
    user = query_one("SELECT user_id FROM users WHERE user_id=%s", (body.user_id,))
    if not user:
        return {"ok": False, "msg": "用户不存在"}

    record_id, _ = execute(
        """INSERT INTO game_records
           (user_id, total_score, correct_rate, play_duration, play_time)
           VALUES (%s, %s, %s, %s, NOW())""",
        (body.user_id, body.total_score, round(body.correct_rate, 2), body.play_duration),
    )
    return {"ok": True, "record_id": record_id}


# ========== 接口4：排行榜 Top10 ==========
@app.get("/get_rank")
def get_rank():
    rows = query_all(
        """SELECT r.record_id, u.username, r.total_score, r.correct_rate,
                  r.play_duration, r.play_time
           FROM game_records r JOIN users u ON r.user_id = u.user_id
           ORDER BY r.total_score DESC, r.play_duration ASC
           LIMIT 10"""
    )
    # 统一转为可 JSON 序列化结构（Decimal / datetime → float / str）
    rank = []
    for i, r in enumerate(rows, start=1):
        rank.append({
            "rank": i,
            "username": r["username"],
            "total_score": r["total_score"],
            "correct_rate": float(r["correct_rate"]),
            "play_duration": r["play_duration"],
            "play_time": r["play_time"].strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {"ok": True, "rank": rank}


# ========== 健康检查 ==========
@app.get("/health")
def health():
    try:
        query_one("SELECT 1 AS ok")
        return {"ok": True, "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="数据库不可用: %s" % e)
