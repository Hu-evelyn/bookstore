#负责启动服务、处理跨域（让 Vue 能连上），并提供一个简单的测试接口
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import engine, get_db

# 核心：这一行会在启动时检查 PostgreSQL，如果没有表，就自动建表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="图书销售管理系统 API")

# 配置 CORS，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 实验阶段允许所有来源，方便调试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "success", "message": "后端服务已成功启动并连接数据库！"}

# 测试接口：获取所有图书列表
@app.get("/api/books")
def get_all_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books