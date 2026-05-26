# fastapi程序入口、生命周期、工具函数、用户认证、以及主要的REST路由
import hashlib
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from sqlalchemy import or_

# 1. MD5加密辅助工具函数
def get_md5_hash(password: str) -> str:
    """将明文密码转化为 MD5 哈希值"""
    # 采用 MD5算法进行加密
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

# 3.使用生命周期管理器 (Lifespan)：系统启动时自动检查并创建超级管理员
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：确保数据库表已创建
    models.Base.metadata.create_all(bind=engine)
    
    # 超级管理员用户在系统完成时便已经存在
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
    

# 初始化 FastAPI并传入lifespan
app = FastAPI(title="图书销售管理系统 API", lifespan=lifespan)

# 配置CORS跨域
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


#超级管理员可以创建新用户，普通管理员只能修改自己的信息，超级管理员可以修改任何用户的信息
@app.post("/api/auth/register", response_model=schemas.UserOut)
def create_new_user(
    new_user: schemas.UserCreate, 
    current_user: models.User = Depends(get_current_user), # 必须登录才能操作
    db: Session = Depends(get_db)
):
    """
    创建新用户接口 (仅限超级管理员操作)
    """
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

#用户查询与更新
@app.get("/api/users")
def get_users(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    查询用户：超级管理员查所有，普通管理员只能查自己
    """
    if current_user.role == "super_admin":
        return db.query(models.User).order_by(models.User.id).all()
    else:
        return db.query(models.User).filter(models.User.id == current_user.id).all()


@app.put("/api/users/{user_id}")
def update_user(
    user_id: int, 
    data: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    修改用户信息
    """
    # 核心安全拦截：如果当前用户既不是超级管理员，试图修改的也不是自己的ID，直接拦截！
    if current_user.role != "super_admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="越权警告：您只能修改自己的信息！")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到该用户")
    
    # 更新基本信息
    user.real_name = data.real_name
    user.gender = data.gender
    user.age = data.age
    
    # 如果传了新密码，就对新密码进行MD5加密并更新
    if data.password:
        user.password_md5 = get_md5_hash(data.password)
        
    db.commit()
    return {"status": "success", "message": "用户信息更新成功"}


# ==================== 图书管理 API 接口 ====================

@app.get("/api/books", response_model=list[schemas.BookOut])
def search_books(
    keyword: str = None, 
    current_user: models.User = Depends(get_current_user), # 需要登录
    db: Session = Depends(get_db)
):
    """
    图书查询：支持 ISBN、书名、作者、出版社的模糊查询
    """
    query = db.query(models.Book)
    if keyword:
        # 使用 or_ 进行多条件模糊匹配
        query = query.filter(
            or_(
                models.Book.isbn.ilike(f"%{keyword}%"),
                models.Book.title.ilike(f"%{keyword}%"),
                models.Book.author.ilike(f"%{keyword}%"),
                models.Book.publisher.ilike(f"%{keyword}%")
            )
        )
    return query.all()

@app.put("/api/books/{isbn}")
def update_book_info(
    isbn: str, 
    book_info: schemas.BookBase, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    修改图书信息
    """
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        raise HTTPException(status_code=404, detail="未找到该书籍")
    
    # 更新字段
    book.title = book_info.title
    book.author = book_info.author
    book.publisher = book_info.publisher
    book.retail_price = book_info.retail_price
    db.commit()
    
    return {"status": "success", "message": "图书信息修改成功"}

# ==================== 销售业务 API 接口 ====================

@app.post("/api/sales/sell")
def sell_book(
    sell_data: schemas.SellBook, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    前台售书：扣库存 + 增加财务收入
    """
    if sell_data.count <= 0:
        raise HTTPException(status_code=400, detail="销售数量必须大于0")

    # 1. 查询书籍，使用 with_for_update() 加行级锁，防止高并发超卖
    book = db.query(models.Book).filter(models.Book.isbn == sell_data.isbn).with_for_update().first()
    
    if not book:
        raise HTTPException(status_code=404, detail="未找到该书籍")
    if book.stock < sell_data.count:
        raise HTTPException(status_code=400, detail=f"库存不足！当前库存仅剩 {book.stock} 本")

    try:
        # 2. 扣减库存
        book.stock -= sell_data.count
        
        # 3. 增加财务账单流水 (类型为 INCOME)
        total_price = book.retail_price * sell_data.count
        new_account_record = models.Accounting(
            record_type="INCOME",
            amount=total_price,
            operator_id=current_user.id
        )
        db.add(new_account_record)
        
        # 4. 提交事务 (库存和财务必须同时成功)
        db.commit()
        return {"status": "success", "message": f"成功售出 {sell_data.count} 本，收入 {total_price} 元"}
    
    except Exception as e:
        # 如果中间发生任何报错，回滚整个事务，确保数据不乱
        db.rollback()
        raise HTTPException(status_code=500, detail=f"系统内部错误，交易已回滚: {str(e)}")


# ==================== 进货生命周期 API 接口 ====================
@app.get("/api/procurement")
def get_procurement_list(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """查询所有进货单列表"""
    # 按时间倒序排列，最新建的单子在最前面
    return db.query(models.Procurement).order_by(models.Procurement.id.desc()).all()


@app.post("/api/procurement")
def create_procurement(
    data: schemas.ProcurementCreate, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    1. 创建进货单 (初始状态：未付款)
    """
    book = db.query(models.Book).filter(models.Book.isbn == data.isbn).first()
    
    # 如果库存里从来没这本书的信息，就建立一个占位符，库存初始为 0
    if not book:
        if not (data.title and data.author and data.publisher):
            raise HTTPException(status_code=400, detail="该书为新书，必须提供书名、作者和出版社信息")
        
        new_book = models.Book(
            isbn=data.isbn, title=data.title, 
            author=data.author, publisher=data.publisher, 
            stock=0, retail_price=0.0  # 零售价在入库时再确定
        )
        db.add(new_book)
    
    # 建立进货单
    new_procurement = models.Procurement(
        isbn=data.isbn, 
        count=data.count, 
        import_price=data.import_price, 
        status="未付款"
    )
    db.add(new_procurement)
    db.commit()
    return {"status": "success", "message": "进货清单已创建，当前状态为[未付款]"}


@app.put("/api/procurement/{proc_id}/pay")
def pay_procurement(
    proc_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    2. 进货付款：产生财务支出，状态流转为"已付款"
    """
    proc = db.query(models.Procurement).with_for_update().filter(models.Procurement.id == proc_id).first()
    if not proc or proc.status != "未付款":
        raise HTTPException(status_code=400, detail="单据不存在或当前状态无法付款")
    
    # 修改状态
    proc.status = "已付款"
    
    # 记录财务支出
    expense_amount = proc.count * proc.import_price
    expense_record = models.Accounting(
        record_type="EXPENSE", 
        amount=expense_amount, 
        operator_id=current_user.id
    )
    db.add(expense_record)
    
    db.commit()
    return {"status": "success", "message": f"付款成功，财务已支出 {expense_amount} 元"}


@app.delete("/api/procurement/{proc_id}/return")
def return_procurement(
    proc_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    3. 进货退货：仅限未付款单据
    """
    proc = db.query(models.Procurement).filter(models.Procurement.id == proc_id).first()
    if not proc or proc.status != "未付款":
        raise HTTPException(status_code=400, detail="只能对[未付款]状态的书籍进行退货")
    
    # 修改状态为已退货
    proc.status = "已退货"
    db.commit()
    return {"status": "success", "message": "已成功操作退货"}


@app.put("/api/procurement/{proc_id}/stock-in")
def stock_in_procurement(
    proc_id: int, 
    data: schemas.StockInRequest,
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    4. 到货入库：更新库存与零售价
    """
    proc = db.query(models.Procurement).filter(models.Procurement.id == proc_id).first()
    if not proc or proc.status != "已付款":
        raise HTTPException(status_code=400, detail="只有[已付款]的单据才能进行入库操作")
    
    book = db.query(models.Book).filter(models.Book.isbn == proc.isbn).first()
    
    # 增加库存，并设定零售价
    book.stock += proc.count
    book.retail_price = data.retail_price
    proc.status = "已入库"
    
    db.commit()
    return {"status": "success", "message": "已成功入库，库存与价格已更新"}


# ==================== 财务管理 API 接口 ====================

@app.get("/api/accounting")
def get_accounting_records(
    start_date: str = None, 
    end_date: str = None, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    查看财务账单流水
    """
    query = db.query(models.Accounting)
    
    # 支持按时间段筛选
    if start_date:
        query = query.filter(models.Accounting.create_time >= start_date)
    if end_date:
        query = query.filter(models.Accounting.create_time <= f"{end_date} 23:59:59")
        
    records = query.all()
    return records