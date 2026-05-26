<template>
  <div class="accounting-manage">
    <el-row :gutter="20" class="summary-panel">
      <el-col :span="8">
        <el-card shadow="hover" class="data-card income-card">
          <div class="card-header">总收入 (售书款)</div>
          <div class="card-value">+ ¥ {{ totalIncome.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card expense-card">
          <div class="card-header">总支出 (进货款)</div>
          <div class="card-value">- ¥ {{ totalExpense.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card profit-card">
          <div class="card-header">净利润</div>
          <div class="card-value">¥ {{ (totalIncome - totalExpense).toFixed(2) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="box-card" shadow="never" style="margin-bottom: 20px;">
      <div class="toolbar">
        <div class="filter-area">
          <span class="filter-label">选择时间范围：</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="fetchRecords"
          />
          <el-button type="primary" :icon="Search" style="margin-left: 15px;" @click="fetchRecords">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="resetFilter">重置</el-button>
        </div>
      </div>
    </el-card>

    <el-card class="box-card table-card" shadow="never">
      <el-table :data="recordList" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="流水号" width="100" align="center" />
        <el-table-column prop="create_time" label="发生时间" width="200">
          <template #default="scope">
            {{ formatTime(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="record_type" label="收支类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.record_type === 'INCOME' ? 'success' : 'danger'" effect="dark">
              {{ scope.row.record_type === 'INCOME' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="交易金额(元)" min-width="150">
          <template #default="scope">
            <span :class="scope.row.record_type === 'INCOME' ? 'text-income' : 'text-expense'">
              {{ scope.row.record_type === 'INCOME' ? '+' : '-' }} {{ scope.row.amount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="operator_id" label="经办人ID" width="120" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import request from '../utils/request'

const loading = ref(false)
const recordList = ref([])
const dateRange = ref(null)

// === 计算属性：自动统计数据 ===
const totalIncome = computed(() => {
  return recordList.value
    .filter(item => item.record_type === 'INCOME')
    .reduce((sum, item) => sum + item.amount, 0)
})

const totalExpense = computed(() => {
  return recordList.value
    .filter(item => item.record_type === 'EXPENSE')
    .reduce((sum, item) => sum + item.amount, 0)
})

// === 获取数据 ===
const fetchRecords = async () => {
  loading.value = true
  try {
    let params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await request.get('/api/accounting', { params })
    
    // 按时间倒序，最新的流水在最前面
    recordList.value = res.sort((a, b) => new Date(b.create_time) - new Date(a.create_time))
  } catch (error) {
  } finally {
    loading.value = false
  }
}

// === 重置查询 ===
const resetFilter = () => {
  dateRange.value = null
  fetchRecords()
}

// === 时间格式化工具 ===
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.summary-panel {
  margin-bottom: 20px;
}
.data-card {
  border-radius: 12px;
  text-align: center;
  border: none;
}
.card-header {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 10px;
}
.card-value {
  font-size: 28px;
  font-weight: bold;
}
.income-card .card-value {
  color: var(--el-color-warning);
}
.expense-card .card-value {
  color: #ef4444; 
}
.profit-card .card-value {
  color: var(--el-color-primary); 
}

.filter-area {
  display: flex;
  align-items: center;
}
.filter-label {
  font-weight: bold;
  color: var(--el-color-primary);
  margin-right: 15px;
}
.text-income {
  color: #10b981;
  font-weight: bold;
}
.text-expense {
  color: #ef4444;
  font-weight: bold;
}
</style>