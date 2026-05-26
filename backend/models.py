#用于定义数据库表结构
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, CheckConstraint
from datetime import datetime
from database import Base

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False) # 用户名
    password_md5 = Column(String(100), nullable=False)                     # MD5 密码
    role = Column(String(20), default="admin")                             # 角色: super_admin / admin
    
    # 补充的基本信息
    real_name = Column(String(50), nullable=False)                         # 真实姓名
    emp_id = Column(String(20), unique=True, index=True, nullable=False)   # 工号
    gender = Column(String(10))                                            # 性别
    age = Column(Integer)
    
# 图书表 (核心)
class Book(Base):
    __tablename__ = "books"
    isbn = Column(String(20), primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50))
    publisher = Column(String(50))
    stock = Column(Integer, default=0)
    retail_price = Column(Float, nullable=False)
    
    # 确保库存永远不能是负数
    __table_args__ = (
        CheckConstraint('stock >= 0', name='check_stock_positive'),
    )

# 进货单表
class Procurement(Base):
    __tablename__ = "procurement"
    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), ForeignKey("books.isbn"))
    count = Column(Integer, nullable=False)
    import_price = Column(Float, nullable=False)
    status = Column(String(20), default="未付款") # 状态流转: 未付款 -> 已付款 -> 已入库
    create_time = Column(DateTime, default=datetime.now)

# 财务流水表
class Accounting(Base):
    __tablename__ = "accounting"
    id = Column(Integer, primary_key=True, index=True)
    record_type = Column(String(10), nullable=False) # INCOME (收入) 或 EXPENSE (支出)
    amount = Column(Float, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id")) # 经办人
    create_time = Column(DateTime, default=datetime.now)