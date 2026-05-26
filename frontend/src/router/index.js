import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/books', // 登录后默认跳转到图书管理页
    children: [
      // 在 children 数组里找个位置加上这段：
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/UserManage.vue')
    },
      {
        path: 'books',
        name: 'Books',
        component: () => import('../views/BookManage.vue')
      },
      {
        path: 'procurement',
        name: 'Procurement',
        component: () => import('../views/Procurement.vue')
      },
      {
        path: 'accounting',
        name: 'Accounting',
        component: () => import('../views/Accounting.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 简易路由守卫：没登录时，强行跳回登录页 [cite: 13]
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router