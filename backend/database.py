#用于配置连接PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接 URL 格式: postgresql://用户名:密码@主机地址/数据库名
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Hyf20060208@localhost/bookstore_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基本映射类
Base = declarative_base()

# 依赖注入：用于在每次请求时获取数据库会话，请求结束时自动关闭
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()