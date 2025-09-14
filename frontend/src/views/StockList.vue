<template>
  <div class="stock-list">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <h1>股票列表</h1>
      <div class="header-actions">
        <button @click="refreshData" class="btn btn-primary" :disabled="loading">
          <span v-if="loading">刷新中...</span>
          <span v-else>刷新数据</span>
        </button>
        <button @click="showAddDialog = true" class="btn btn-success">
          添加股票
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filters">
      <div class="filter-group">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索股票代码或名称..."
          class="search-input"
          @input="handleSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="selectedMarket" @change="handleFilter" class="filter-select">
          <option value="">所有市场</option>
          <option value="SH">上海</option>
          <option value="SZ">深圳</option>
          <option value="BJ">北京</option>
        </select>
      </div>
      <div class="filter-group">
        <select v-model="selectedStatus" @change="handleFilter" class="filter-select">
          <option value="">所有状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading && stocks.length === 0" message="正在加载股票数据..." />
    
    <!-- 错误提示 -->
    <ErrorMessage 
      v-if="error" 
      :message="error" 
      type="error"
      :actions="[{ label: '重试', action: refreshData }]"
      @close="clearError"
    />

    <!-- 数据表格 -->
    <DataTable
      v-if="!loading || stocks.length > 0"
      :data="stocks"
      :columns="tableColumns"
      :loading="loading"
      :total="totalCount"
      :page="currentPage"
      :page-size="pageSize"
      :actions="tableActions"
      @page-change="handlePageChange"
      @sort-change="handleSortChange"
    />

    <!-- 添加股票对话框 -->
    <div v-if="showAddDialog" class="modal-overlay" @click="closeAddDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加股票</h3>
          <button @click="closeAddDialog" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleAddStock">
            <div class="form-group">
              <label for="stockCode">股票代码</label>
              <input 
                id="stockCode"
                v-model="newStock.code" 
                type="text" 
                placeholder="例如：000001"
                required
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="stockName">股票名称</label>
              <input 
                id="stockName"
                v-model="newStock.name" 
                type="text" 
                placeholder="例如：平安银行"
                required
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="stockMarket">市场</label>
              <select id="stockMarket" v-model="newStock.market" required class="form-select">
                <option value="">请选择市场</option>
                <option value="SH">上海证券交易所</option>
                <option value="SZ">深圳证券交易所</option>
                <option value="BJ">北京证券交易所</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeAddDialog" class="btn btn-secondary">
                取消
              </button>
              <button type="submit" class="btn btn-primary" :disabled="addingStock">
                <span v-if="addingStock">添加中...</span>
                <span v-else>添加</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { stocksAPI } from '@/services/api'
import Loading from '@/components/Loading.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import DataTable from '@/components/DataTable.vue'

// 响应式数据
const stocks = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const selectedMarket = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const sortField = ref('')
const sortOrder = ref('')

// 添加股票相关
const showAddDialog = ref(false)
const addingStock = ref(false)
const newStock = ref({
  code: '',
  name: '',
  market: ''
})

// 表格列配置
const tableColumns = [
  {
    key: 'code',
    title: '股票代码',
    sortable: true,
    width: '120px'
  },
  {
    key: 'name',
    title: '股票名称',
    sortable: true,
    width: '200px'
  },
  {
    key: 'market',
    title: '市场',
    sortable: true,
    width: '100px',
    formatter: (value: string) => {
      const marketMap: Record<string, string> = {
        'SH': '上海',
        'SZ': '深圳',
        'BJ': '北京'
      }
      return marketMap[value] || value
    }
  },
  {
    key: 'current_price',
    title: '当前价格',
    sortable: true,
    width: '120px',
    formatter: (value: number) => value ? `¥${value.toFixed(2)}` : '--'
  },
  {
    key: 'change_percent',
    title: '涨跌幅',
    sortable: true,
    width: '100px',
    formatter: (value: number) => {
      if (value === null || value === undefined) return '--'
      const sign = value >= 0 ? '+' : ''
      return `${sign}${value.toFixed(2)}%`
    },
    cellClass: (value: number) => {
      if (value > 0) return 'text-success'
      if (value < 0) return 'text-danger'
      return ''
    }
  },
  {
    key: 'volume',
    title: '成交量',
    sortable: true,
    width: '120px',
    formatter: (value: number) => {
      if (!value) return '--'
      if (value >= 100000000) return `${(value / 100000000).toFixed(1)}亿`
      if (value >= 10000) return `${(value / 10000).toFixed(1)}万`
      return value.toString()
    }
  },
  {
    key: 'is_active',
    title: '状态',
    width: '80px',
    formatter: (value: boolean) => value ? '活跃' : '非活跃',
    cellClass: (value: boolean) => value ? 'text-success' : 'text-muted'
  },
  {
    key: 'updated_at',
    title: '更新时间',
    sortable: true,
    width: '160px',
    formatter: (value: string) => {
      if (!value) return '--'
      return new Date(value).toLocaleString('zh-CN')
    }
  }
]

// 表格操作配置
const tableActions = [
  {
    label: '查看详情',
    action: (row: any) => handleViewDetail(row),
    type: 'primary'
  },
  {
    label: '编辑',
    action: (row: any) => handleEdit(row),
    type: 'default'
  },
  {
    label: '删除',
    action: (row: any) => handleDelete(row),
    type: 'danger',
    confirm: true,
    confirmMessage: '确定要删除这支股票吗？'
  }
]

// 生命周期
onMounted(() => {
  loadStocks()
})

// 方法
const loadStocks = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      market: selectedMarket.value,
      is_active: selectedStatus.value === 'active' ? true : selectedStatus.value === 'inactive' ? false : undefined,
      ordering: sortField.value ? `${sortOrder.value === 'desc' ? '-' : ''}${sortField.value}` : undefined
    }
    
    const response = await stocksAPI.getStocks(params)
    stocks.value = response.data.results || []
    totalCount.value = response.data.count || 0
    
  } catch (err: any) {
    console.error('加载股票列表失败:', err)
    error.value = err.response?.data?.message || '加载股票列表失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  currentPage.value = 1
  loadStocks()
}

const handleSearch = () => {
  currentPage.value = 1
  loadStocks()
}

const handleFilter = () => {
  currentPage.value = 1
  loadStocks()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadStocks()
}

const handleSortChange = (field: string, order: string) => {
  sortField.value = field
  sortOrder.value = order
  loadStocks()
}

const handleViewDetail = (row: any) => {
  // 跳转到股票详情页面
  console.log('查看详情:', row)
}

const handleEdit = (row: any) => {
  // 编辑股票信息
  console.log('编辑股票:', row)
}

const handleDelete = async (row: any) => {
  try {
    await stocksAPI.deleteStock(row.id)
    loadStocks()
  } catch (err: any) {
    console.error('删除股票失败:', err)
    error.value = err.response?.data?.message || '删除股票失败'
  }
}

const handleAddStock = async () => {
  try {
    addingStock.value = true
    await stocksAPI.createStock(newStock.value)
    closeAddDialog()
    loadStocks()
  } catch (err: any) {
    console.error('添加股票失败:', err)
    error.value = err.response?.data?.message || '添加股票失败'
  } finally {
    addingStock.value = false
  }
}

const closeAddDialog = () => {
  showAddDialog.value = false
  newStock.value = {
    code: '',
    name: '',
    market: ''
  }
}

const clearError = () => {
  error.value = ''
}
</script>

<style scoped>
.stock-list {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.page-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #1e7e34;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.search-input, .filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
}

.search-input:focus, .filter-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  color: #2c3e50;
  font-weight: 500;
}

.form-input, .form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

/* 表格样式增强 */
:deep(.text-success) {
  color: #28a745 !important;
}

:deep(.text-danger) {
  color: #dc3545 !important;
}

:deep(.text-muted) {
  color: #6c757d !important;
}

@media (max-width: 768px) {
  .stock-list {
    padding: 15px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .search-input, .filter-select {
    min-width: auto;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>