<template>
  <div class="user-manage">
    <el-card class="box-card" shadow="never">
      <div class="toolbar">
        <el-button v-if="userRole === 'super_admin'" type="primary" @click="createDialogVisible = true">
          创建普通管理员
        </el-button>
        <span v-else style="color: #6b7280; font-size: 14px;">
          在此可以查看并修改您的个人信息
        </span>
        <el-button :icon="Refresh" circle @click="fetchUsers" />
      </div>
    </el-card>

    <el-card class="box-card table-card" shadow="never" style="margin-top: 20px;">
      <el-table :data="userList" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="real_name" label="真实姓名" width="150" />
        <el-table-column prop="emp_id" label="工号" width="120" align="center" />
        <el-table-column prop="gender" label="性别" width="80" align="center" />
        <el-table-column prop="age" label="年龄" width="80" align="center" />
        <el-table-column prop="role" label="角色" width="150" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'super_admin' ? 'danger' : 'info'" effect="dark">
              {{ scope.row.role === 'super_admin' ? '超级管理员' : '普通管理员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">
              编辑资料
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="创建新管理员" width="500px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="createForm.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="createForm.password" type="password" show-password /></el-form-item>
        <el-form-item label="真实姓名"><el-input v-model="createForm.real_name" /></el-form-item>
        <el-form-item label="工号"><el-input v-model="createForm.emp_id" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="createForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="createForm.age" :min="18" :max="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑资料" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-alert title="注意：如果不需要修改密码，请将密码框留空。" type="warning" show-icon style="margin-bottom: 20px;" />
        <el-form-item label="用户名"><el-input v-model="editForm.username" disabled placeholder="账号不可改" /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="editForm.password" type="password" show-password placeholder="不修改则留空" /></el-form-item>
        <el-form-item label="真实姓名"><el-input v-model="editForm.real_name" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="editForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="editForm.age" :min="18" :max="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

// 获取当前登录角色
const userRole = localStorage.getItem('userRole') || 'admin'
const loading = ref(false)
const userList = ref([])

// === 查询列表 ===
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/users')
    userList.value = res
  } catch (error) {
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchUsers())

// === 创建用户逻辑 (仅超管可用) ===
const createDialogVisible = ref(false)
const createForm = reactive({ username: '', password: '', real_name: '', emp_id: '', gender: '男', age: 25, role: 'admin' })

const submitCreate = async () => {
  if (!createForm.username || !createForm.password || !createForm.real_name || !createForm.emp_id) {
    return ElMessage.warning('请将带必填信息的字段补充完整！')
  }
  try {
    await request.post('/api/auth/register', createForm)
    ElMessage.success('管理员创建成功！')
    createDialogVisible.value = false
    fetchUsers()
    Object.assign(createForm, { username: '', password: '', real_name: '', emp_id: '', gender: '男', age: 25, role: 'admin' })
  } catch (error) {}
}

// === 修改用户逻辑 ===
const editDialogVisible = ref(false)
const currentEditId = ref(null)
const editForm = reactive({ username: '', password: '', real_name: '', gender: '男', age: 25 })

const openEditDialog = (row) => {
  currentEditId.value = row.id
  // 把行数据拷进去，并清空密码框（因为密码是安全的单向哈希，无法展示明文）
  Object.assign(editForm, {
    username: row.username,
    real_name: row.real_name,
    gender: row.gender,
    age: row.age,
    password: '' 
  })
  editDialogVisible.value = true
}

const submitEdit = async () => {
  try {
    const res = await request.put(`/api/users/${currentEditId.value}`, {
      real_name: editForm.real_name,
      gender: editForm.gender,
      age: editForm.age,
      password: editForm.password || null
    })
    
    if (res.status === 'success') {
      ElMessage.success(res.message)
      editDialogVisible.value = false
      fetchUsers()
    }
  } catch (error) {}
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>