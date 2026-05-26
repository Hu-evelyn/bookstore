# Bookstore 图书销售管理系统

项目概览：图书销售管理系统，前端采用 Vue3 + Vite + Element Plus，后端采用 Python3 + FastAPI + SQLAlchemy，数据库为 PostgreSQL。

本实验中数据库设计以ORM模型实现，由 models.py 中的SQLAlchemy模型实现

目录结构：

```
.
├── README.md                # 本文件（项目说明）
├── backend                  # 后端服务
│   ├── main.py              # FastAPI 程序入口，路由与业务逻辑
│   ├── database.py          # 连接数据库
│   ├── models.py            # ORM模型（定义4个数据库表）：User/Book/Procurement/Accounting
│   └── schemas.py           # Pydantic 请求/响应模型
├── frontend                 # 前端页面
│   ├── package.json         # 依赖与启动脚本
│   └── src
│       ├── main.js          # Vue 应用挂载与插件注册
│       ├── App.vue          # 根组件（router-view）
│       ├── router
│       │   └── index.js     # 路由与守卫
│       ├── utils
│       │   └── request.js   # axios 封装（自动注入 token、错误处理）
│       └── views            # 视图
│           ├── Login.vue
│           ├── Layout.vue
│           ├── UserManage.vue
│           ├── BookManage.vue
│           ├── Procurement.vue
│           └── Accounting.vue
└── public / assets / ...    # 静态资源

```

快速启动

- 后端

  venv\Scripts\activate    #激活虚拟环境

  uvicorn main:app --reload    #运行启动命令
- 前端

  npm run dev
