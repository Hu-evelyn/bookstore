<template>
  <div class="book-manage">
    <el-card class="box-card" shadow="never">
      <div class="toolbar">
        <div class="search-area">
          <el-input 
            v-model="searchKeyword" 
            placeholder="输入书名、作者、ISBN或出版社..." 
            class="search-input" 
            clearable
            @keyup.enter="fetchBooks"
            @clear="fetchBooks"
          >
            <template #append>
              <el-button :icon="Search" @click="fetchBooks" />
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <el-card class="box-card table-card" shadow="never">
      <el-table :data="bookList" border stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="title" label="书名" min-width="180" />
        <el-table-column prop="author" label="作者" width="150" />
        <el-table-column prop="publisher" label="出版社" width="180" />
        <el-table-column prop="retail_price" label="零售价(元)" width="100">
          <template #default="scope">
            <span class="price-text">¥ {{ scope.row.retail_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.stock < 5 ? 'danger' : 'success'">
              {{ scope.row.stock }} 本
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="openEditDialog(scope.row)">
              编辑
            </el-button>
            <el-button size="small" type="warning" @click="openSellDialog(scope.row)" :disabled="scope.row.stock <= 0">
              售书
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editDialogVisible" title="修改图书信息" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="书名">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="editForm.author" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="editForm.publisher" />
        </el-form-item>
        <el-form-item label="零售价">
          <el-input-number v-model="editForm.retail_price" :precision="2" :step="1" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">保存修改</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="sellDialogVisible" title="前台收银售书" width="400px">
      <div class="sell-info">
        <p><strong>书名：</strong>{{ sellForm.title }}</p>
        <p><strong>单价：</strong>¥ {{ sellForm.price }}</p>
        <p><strong>当前库存：</strong>{{ sellForm.maxStock }} 本</p>
      </div>
      <el-form :model="sellForm" label-width="80px" style="margin-top: 20px;">
        <el-form-item label="售出数量">
          <el-input-number v-model="sellForm.count" :min="1" :max="sellForm.maxStock" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="sellDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="submitSell">确认收款</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const loading = ref(false)
const bookList = ref([])
const searchKeyword = ref('')

// === 1. 查询图书数据 ===
const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/books', {
      params: { keyword: searchKeyword.value }
    })
    bookList.value = res // 将后端返回的数组赋值给表格数据
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 页面加载时自动请求一次数据
onMounted(() => {
  fetchBooks()
})

// === 2. 编辑图书信息逻辑 ===
const editDialogVisible = ref(false)
const editForm = reactive({ isbn: '', title: '', author: '', publisher: '', retail_price: 0 })

const openEditDialog = (row) => {
  // 把当前行的数据拷贝到表单里
  Object.assign(editForm, row)
  editDialogVisible.value = true
}

const submitEdit = async () => {
  try {
    const res = await request.put(`/api/books/${editForm.isbn}`, editForm)
    if (res.status === 'success') {
      ElMessage.success('修改成功')
      editDialogVisible.value = false
      fetchBooks() // 刷新表格
    }
  } catch (error) {}
}

// === 3. 售书逻辑 ===
const sellDialogVisible = ref(false)
const sellForm = reactive({ isbn: '', title: '', price: 0, count: 1, maxStock: 0 })

const openSellDialog = (row) => {
  sellForm.isbn = row.isbn
  sellForm.title = row.title
  sellForm.price = row.retail_price
  sellForm.maxStock = row.stock
  sellForm.count = 1 // 默认卖1本
  sellDialogVisible.value = true
}

const submitSell = async () => {
  try {
    await ElMessageBox.confirm(
      `确认售出 ${sellForm.count} 本《${sellForm.title}》吗？总计收款 ¥${(sellForm.price * sellForm.count).toFixed(2)}`,
      '收银确认',
      { confirmButtonText: '确认收款', cancelButtonText: '取消', type: 'warning' }
    )
    
    // 调用我们在后端写好的那个带有数据库事务的牛逼接口
    const res = await request.post('/api/sales/sell', {
      isbn: sellForm.isbn,
      count: sellForm.count
    })
    
    if (res.status === 'success') {
      ElMessage.success(res.message)
      sellDialogVisible.value = false
      fetchBooks() // 卖完后刷新表格，库存自动变少
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}
</script>

<style scoped>
.book-manage {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
}
.search-input {
  width: 400px;
}
.price-text {
  color: #eab308;
  font-weight: bold;
}
.sell-info p {
  margin: 8px 0;
  font-size: 16px;
}
</style>