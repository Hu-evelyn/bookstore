#用于处理前端输入输出校验
from pydantic import BaseModel
from typing import Optional

# 用户登录时，前端需要传的字段
class UserLogin(BaseModel):
    username: str
    password: str

# 超级管理员创建新用户时，前端需要传的字段
class UserCreate(BaseModel):
    username: str
    password: str  # 前端传明文，后端负责将其加密为 MD5 存入数据库
    real_name: str
    emp_id: str
    gender: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = "admin" # 默认创建普通管理员

# 返回给前端的用户数据格式（过滤掉密码）
class UserOut(BaseModel):
    id: int
    username: str
    real_name: str
    emp_id: str
    gender: Optional[str]
    age: Optional[int]
    role: str

    class Config:
        from_attributes = True # 允许 Pydantic 兼容 SQLAlchemy 模型