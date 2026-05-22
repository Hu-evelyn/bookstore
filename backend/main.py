# 更新main,实现核心加密、初始化与接口
import hashlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# 1. MD5 加密辅助工具函数
def get_md5_hash(password: str) -> str:
    """将明文密码转化为 MD5 哈希值"""
    # 按照 PPT 要求采用 MD5 算法进行加密
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# 2. 模拟一个极其简单的 Token 验证机制（用于在中期实验中进行登录和权限检查）
def get_current_user(token: str = Header(None), db: Session = Depends(get_db)):
    """
    为了界面简便，我们约定：登录成功后，前端将 username 作为 Token 放在请求头(Header)里传回来。
    后端以此判断用户是否登录，并获取用户信息。
    """
    if not token:
        raise HTTPException(status_code=401, detail="请先登录系统！")
    
    user = db.query(models.User).filter(models.User.username == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="无效的登录凭证或用户不存在")
    return user

# 3. 使用生命周期管理器 (Lifespan)：系统启动时自动检查并创建超级管理员
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：确保数据库表已创建
    models.Base.metadata.create_all(bind=engine)
    
    # 满足 PPT 要求：“超级管理员用户在系统完成时便已经存在”
    db = next(get_db())
    try:
        admin_exist = db.query(models.User).filter(models.User.role == "super_admin").first()
        if not admin_exist:
            print("首次运行系统，正在自动初始化超级管理员账号...")
            default_admin = models.User(
                username="admin",
                password_md5=get_md5_hash("admin123"), # 默认初始密码 admin123
                role="super_admin",
                real_name="系统总管理员",
                emp_id="9999",
                gender="男",
                age=35
            )
            db.add(default_admin)
            db.commit()
            print("超级管理员账号初始化成功！用户名: admin, 密码: admin123")
    finally:
        db.close()
    yield
    # 关闭时执行的操作（这里不需要）

# 初始化 FastAPI 并传入 lifespan
app = FastAPI(title="图书销售管理系统 API", lifespan=lifespan)

# 配置 CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "success", "message": "后端服务已成功启动并连接数据库！"}


# ==================== 用户认证 API 接口 ====================

@app.post("/api/auth/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 1. 根据用户名查找用户
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 2. 将前端传来的明文密码进行 MD5 计算，并与数据库中的密文比对
    input_password_md5 = get_md5_hash(user_data.password)
    if user.password_md5 != input_password_md5:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    # 3. 登录成功，返回用户信息。实验阶段，直接把 username 返回作为简易 Token
    return {
        "status": "success",
        "message": "登录成功",
        "token": user.username, 
        "user": {
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role
        }
    }


@app.post("/api/auth/register", response_model=schemas.UserOut)
def create_new_user(
    new_user: schemas.UserCreate, 
    current_user: models.User = Depends(get_current_user), # 必须登录才能操作
    db: Session = Depends(get_db)
):
    """
    创建新用户接口 (仅限超级管理员操作)
    """
    # 满足 PPT 要求：“普通管理员用户的用户名和密码需要由超级管理员用户来创建”
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="权限不足！只有超级管理员才能创建新用户。")
    
    # 检查用户名是否已存在
    user_exist = db.query(models.User).filter(models.User.username == new_user.username).first()
    if user_exist:
        raise HTTPException(status_code=400, detail="该用户名已存在")
        
    # 检查工号是否已存在
    emp_exist = db.query(models.User).filter(models.User.emp_id == new_user.emp_id).first()
    if emp_exist:
        raise HTTPException(status_code=400, detail="该工号已绑定其他用户")

    # 密码加密后存入数据库
    db_user = models.User(
        username=new_user.username,
        password_md5=get_md5_hash(new_user.password), # 强制进行 MD5 加密
        real_name=new_user.real_name,
        emp_id=new_user.emp_id,
        gender=new_user.gender,
        age=new_user.age,
        role=new_user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user