<template>
  <div class="login-container">
    <div class="login-box">
      <div class="title">
        <el-icon color="#fde047" :size="32"><Reading /></el-icon>
        <h2>图书销售管理系统</h2>
      </div>
      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input v-model="form.username" placeholder="请输入用户名 (如: admin)" :prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="请输入密码 (如: admin123)" :prefix-icon="Lock" show-password size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-button type="warning" class="login-btn" size="large" @click="handleLogin">
          立即登录
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Reading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码！')
    return
  }
  try {
    // 调用后端的登录接口
    const res = await request.post('/api/auth/login', form)
    if (res.status === 'success') {
      ElMessage.success('登录成功！')
      localStorage.setItem('token', res.token) // 保存通行证
      localStorage.setItem('userRole', res.user.role) // 保存角色用于权限判断
      router.push('/books') // 跳往主界面
    }
  } catch (error) {
    // 报错信息已由拦截器统一处理
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #4c1d95 0%, #2e1065 100%);
}
.login-box {
  width: 380px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}
.title {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
  color: #4c1d95;
}
.login-btn {
  width: 100%;
  font-weight: bold;
  letter-spacing: 2px;
  margin-top: 10px;
}
</style>