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

#图书相关格式校验
class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    retail_price: float

class BookCreate(BookBase):
    isbn: str

class BookOut(BookCreate):
    stock: int

    class Config:
        from_attributes = True

# 售书时前端传来的数据
class SellBook(BaseModel):
    isbn: str
    count: int # 卖出几本
    
#进货与财务管理schemas
class ProcurementCreate(BaseModel):
    isbn: str
    count: int
    import_price: float
    # PPT规定：新书需填写以下信息，老书不需要 [cite: 25]
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None

class StockInRequest(BaseModel):
    # 到货入库时，必须设定新的零售价 [cite: 34]
    retail_price: float
    
# ==================== 用户管理 Schemas ====================
class UserUpdate(BaseModel):
    real_name: str
    gender: str
    age: int
    password: Optional[str] = None  # 如果不填，代表不修改密码