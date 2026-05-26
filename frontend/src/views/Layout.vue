<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">书城管理台</div>
      <el-menu
        active-text-color="#fde047"
        background-color="#4c1d95"
        text-color="#fff"
        router
        :default-active="$route.path"
        class="el-menu-vertical"
      >
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>个人信息与用户管理</span>
        </el-menu-item>
        <el-menu-item index="/books">
          <el-icon><Reading /></el-icon>
          <span>库存书籍管理</span>
        </el-menu-item>

        <el-menu-item index="/procurement">
          <el-icon><Van /></el-icon>
          <span>进货与入库</span>
        </el-menu-item>
        <el-menu-item index="/accounting">
          <el-icon><Money /></el-icon>
          <span>财务账单查看</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <span class="welcome-text">欢迎回来，管理员！</span>
        <el-button type="danger" size="small" plain @click="handleLogout">退出登录</el-button>
      </el-header>
      
      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Reading, Van, Money } from '@element-plus/icons-vue'

const router = useRouter()
const userRole = localStorage.getItem('userRole')

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userRole')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.sidebar {
  background-color: #4c1d95;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  z-index: 10;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #facc15;
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.el-menu-vertical {
  border-right: none;
}
.header {
  background-color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
}
.welcome-text {
  font-weight: bold;
  color: var(--el-color-primary);
}
.main-content {
  background-color: var(--page-bg);
  padding: 20px;
}
</style>