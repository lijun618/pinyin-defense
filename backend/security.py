# -*- coding: utf-8 -*-
"""
密码加密模块：基于 passlib 的 bcrypt 哈希。
- 密码绝不存明文，数据库 password_hash 字段只存 bcrypt 摘要；
- bcrypt 自带随机盐，same password 每次哈希结果都不同；
- verify 用恒定时间比较，防时序攻击。
"""
from passlib.context import CryptContext

# 兼容 bcrypt 4.x/5.x（passlib 1.7.4 读取 bcrypt.__about__ 会触发 AttributeError）
import bcrypt as _bcrypt
if not hasattr(_bcrypt, "__about__"):
    class _About:  # noqa
        __version__ = getattr(_bcrypt, "__version__", "5.0.0")
    _bcrypt.__about__ = _About  # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """把明文密码哈希成 bcrypt 摘要（用于注册入库）。"""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配（用于登录）。"""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


if __name__ == "__main__":
    h = hash_password("123456")
    print("hash:", h)
    print("verify ok:", verify_password("123456", h))
    print("verify bad:", verify_password("wrong", h))
