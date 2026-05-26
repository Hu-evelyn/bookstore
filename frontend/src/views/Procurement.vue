<template>
  <div class="procurement-manage">
    <el-card class="box-card" shadow="never">
      <div class="toolbar">
        <el-button type="primary" :icon="Plus" @click="createDialogVisible = true">
          新建进货单
        </el-button>
        <el-button :icon="Refresh" circle @click="fetchProcurements" />
      </div>
    </el-card>

    <el-card class="box-card table-card" shadow="never">
      <el-table :data="procurementList" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="单号" width="80" align="center" />
        <el-table-column prop="isbn" label="进货书籍 ISBN" min-width="150" />
        <el-table-column prop="count" label="进货数量" width="100" align="center" />
        <el-table-column prop="import_price" label="进货单价" width="100">
          <template #default="scope">¥ {{ scope.row.import_price }}</template>
        </el-table-column>
        <el-table-column label="总金额" width="120">
          <template #default="scope">
            <span class="total-price">¥ {{ (scope.row.import_price * scope.row.count).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="scope">
            <el-button size="small" type="warning" plain :disabled="scope.row.status !== '未付款'" @click="handlePay(scope.row)">
              财务付款
            </el-button>
            <el-button size="small" type="danger" plain :disabled="scope.row.status !== '未付款'" @click="handleReturn(scope.row)">
              退货
            </el-button>
            <el-button size="small" type="success" :disabled="scope.row.status !== '已付款'" @click="openStockInDialog(scope.row)">
              确认入库
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="创建进货单" width="550px">
      <el-form :model="createForm" label-width="100px">
        <el-alert title="提示：如果是从未进过的新书，请务必填全书名、作者和出版社信息。" type="info" show-icon style="margin-bottom: 20px;" />
        
        <el-form-item label="ISBN (必填)">
          <el-input v-model="createForm.isbn" placeholder="请输入书籍ISBN" />
        </el-form-item>
        <el-form-item label="进货数量">
          <el-input-number v-model="createForm.count" :min="1" />
        </el-form-item>
        <el-form-item label="进货单价">
          <el-input-number v-model="createForm.import_price" :precision="2" :step="1" :min="0.1" />
        </el-form-item>
        
        <el-divider>新书补充信息 (旧书留空即可)</el-divider>
        <el-form-item label="书名">
          <el-input v-model="createForm.title" placeholder="若是新书必须填写" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="createForm.author" placeholder="若是新书必须填写" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="createForm.publisher" placeholder="若是新书必须填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">提交订单</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="stockInDialogVisible" title="确认到货入库" width="400px">
      <div style="margin-bottom: 20px; color: #666;">
        请为这批书籍设定上架销售的<strong>零售价</strong>：
      </div>
      <el-form label-width="80px">
        <el-form-item label="零售价">
          <el-input-number v-model="stockInPrice" :precision="2" :step="1" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInDialogVisible = false">取消</el-button>
        <el-button type="success" @click="submitStockIn">完成入库</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const loading = ref(false)
const procurementList = ref([])

// === 获取数据 ===
const fetchProcurements = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/procurement')
    procurementList.value = res
  } catch (error) {
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProcurements()
})

// 根据状态返回 Element Plus Tag 的颜色类型
const getStatusType = (status) => {
  if (status === '未付款') return 'danger'
  if (status === '已付款') return 'warning'
  if (status === '已退货') return 'info'
  if (status === '已入库') return 'success'
  return ''
}

// === 1. 创建进货单 ===
const createDialogVisible = ref(false)
const createForm = reactive({ isbn: '', count: 10, import_price: 20.0, title: '', author: '', publisher: '' })

const submitCreate = async () => {
  if (!createForm.isbn) {
    return ElMessage.warning('必须填写 ISBN！')
  }
  try {
    const res = await request.post('/api/procurement', createForm)
    if (res.status === 'success') {
      ElMessage.success(res.message)
      createDialogVisible.value = false
      fetchProcurements() // 刷新列表
      // 重置表单
      Object.assign(createForm, { isbn: '', count: 10, import_price: 20.0, title: '', author: '', publisher: '' })
    }
  } catch (error) {}
}

// === 2. 财务付款 ===
const handlePay = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定为单号 ${row.id} 支付进货款 ¥${(row.import_price * row.count).toFixed(2)} 吗？这将在财务系统中生成一笔支出。`,
      '财务付款确认',
      { confirmButtonText: '确认打款', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await request.put(`/api/procurement/${row.id}/pay`)
    if (res.status === 'success') {
      ElMessage.success(res.message)
      fetchProcurements()
    }
  } catch (error) { if (error !== 'cancel') console.error(error) }
}

// === 3. 退货 ===
const handleReturn = async (row) => {
  try {
    await ElMessageBox.confirm('确定要退掉这批货吗？单据状态将变为[已退货]。', '退货确认', { type: 'error' })
    const res = await request.delete(`/api/procurement/${row.id}/return`)
    if (res.status === 'success') {
      ElMessage.success(res.message)
      fetchProcurements()
    }
  } catch (error) {}
}

// === 4. 入库 ===
const stockInDialogVisible = ref(false)
const currentProcId = ref(null)
const stockInPrice = ref(0)

const openStockInDialog = (row) => {
  currentProcId.value = row.id
  stockInPrice.value = row.import_price * 1.5 // 智能默认设定零售价为进价的 1.5 倍
  stockInDialogVisible.value = true
}

const submitStockIn = async () => {
  try {
    const res = await request.put(`/api/procurement/${currentProcId.value}/stock-in`, {
      retail_price: stockInPrice.value
    })
    if (res.status === 'success') {
      ElMessage.success(res.message)
      stockInDialogVisible.value = false
      fetchProcurements()
    }
  } catch (error) {}
}
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 15px;
}
.total-price {
  font-weight: bold;
  color: #4c1d95;
}
</style>