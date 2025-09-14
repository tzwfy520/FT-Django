<template>
  <div class="my-stocks">
    <div class="page-header">
      <h2>自选股票</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索股票代码/名称"
          style="width: 200px;"
          @keyup.enter="searchStocks"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加股票
        </el-button>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 自选股票统计 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon total">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stockStats.total }}</div>
                <div class="stats-label">自选股票</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon rising">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value positive">{{ stockStats.rising }}</div>
                <div class="stats-label">上涨</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon falling">
                <el-icon><CaretBottom /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value negative">{{ stockStats.falling }}</div>
                <div class="stats-label">下跌</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon neutral">
                <el-icon><Minus /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stockStats.flat }}</div>
                <div class="stats-label">平盘</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 股票列表 -->
    <div class="stocks-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>自选股票列表 ({{ filteredStocks.length }}只)</span>
            <div class="table-actions">
              <el-button 
                size="small" 
                type="danger" 
                :disabled="!selectedStocks.length"
                @click="batchRemove"
              >
                <el-icon><Delete /></el-icon>
                批量移除 ({{ selectedStocks.length }})
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedStocks" 
          stripe 
          height="500"
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
          v-loading="loading"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="code" label="代码" width="100" sortable="custom" />
          <el-table-column prop="name" label="名称" width="120" sortable="custom">
            <template #default="{ row }">
              <el-button type="text" @click="viewStockDetail(row)">
                {{ row.name }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="现价" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getPriceClass(row.change_percent)">
                {{ formatPrice(row.price) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getPriceClass(row.change_percent)">
                {{ formatPercent(row.change_percent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="change_amount" label="涨跌额" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getPriceClass(row.change_percent)">
                {{ formatPrice(row.change_amount) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120" sortable="custom">
            <template #default="{ row }">
              {{ formatVolume(row.volume) }}
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="120" sortable="custom">
            <template #default="{ row }">
              {{ formatAmount(row.turnover) }}
            </template>
          </el-table-column>
          <el-table-column prop="turnover_rate" label="换手率" width="100" sortable="custom">
            <template #default="{ row }">
              {{ formatPercent(row.turnover_rate) }}
            </template>
          </el-table-column>
          <el-table-column prop="pe_ratio" label="市盈率" width="100" sortable="custom">
            <template #default="{ row }">
              {{ row.pe_ratio || '--' }}
            </template>
          </el-table-column>
          <el-table-column prop="market_cap" label="总市值" width="120" sortable="custom">
            <template #default="{ row }">
              {{ formatAmount(row.market_cap) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="text" @click="viewStockDetail(row)">
                详情
              </el-button>
              <el-button size="small" type="text" @click="removeFromWatchlist(row)" class="danger">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="filteredStocks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 添加股票对话框 -->
    <el-dialog v-model="showAddDialog" title="添加股票到自选" width="600px">
      <div class="add-stock-section">
        <el-input
          v-model="addSearchKeyword"
          placeholder="输入股票代码或名称搜索"
          @keyup.enter="searchAvailableStocks"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="searchAvailableStocks" :loading="searchLoading">
              搜索
            </el-button>
          </template>
        </el-input>
        
        <div class="search-results" v-if="availableStocks.length > 0">
          <el-table 
            :data="availableStocks" 
            height="300"
            @selection-change="handleAddSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="现价" width="100">
              <template #default="{ row }">
                <span :class="getPriceClass(row.change_percent)">
                  {{ formatPrice(row.price) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change_percent" label="涨跌幅" width="100">
              <template #default="{ row }">
                <span :class="getPriceClass(row.change_percent)">
                  {{ formatPercent(row.change_percent) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.inWatchlist" type="success" size="small">已添加</el-tag>
                <el-tag v-else type="info" size="small">未添加</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="empty-search" v-else-if="addSearchKeyword && !searchLoading">
          <el-empty description="未找到相关股票" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="addSelectedStocks" 
          :disabled="!selectedAddStocks.length"
        >
          添加选中股票 ({{ selectedAddStocks.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Plus, Refresh, Star, CaretTop, CaretBottom, 
  Minus, Delete 
} from '@element-plus/icons-vue'
import { stocksAPI } from '@/services/api'

interface Stock {
  id: number
  code: string
  name: string
  price: number
  change_percent: number
  change_amount: number
  volume: number
  turnover: number
  turnover_rate: number
  pe_ratio?: number
  market_cap: number
  inWatchlist?: boolean
}

interface StockStats {
  total: number
  rising: number
  falling: number
  flat: number
}

const loading = ref(false)
const searchLoading = ref(false)
const searchKeyword = ref('')
const addSearchKeyword = ref('')
const showAddDialog = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)
const selectedStocks = ref<Stock[]>([])
const selectedAddStocks = ref<Stock[]>([])
const sortField = ref('')
const sortOrder = ref('')

const myStocks = ref<Stock[]>([])
const availableStocks = ref<Stock[]>([])

const stockStats = computed((): StockStats => {
  const total = myStocks.value.length
  const rising = myStocks.value.filter(s => s.change_percent > 0).length
  const falling = myStocks.value.filter(s => s.change_percent < 0).length
  const flat = myStocks.value.filter(s => s.change_percent === 0).length
  
  return { total, rising, falling, flat }
})

const filteredStocks = computed(() => {
  let stocks = myStocks.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    stocks = stocks.filter(stock => 
      stock.code.toLowerCase().includes(keyword) || 
      stock.name.toLowerCase().includes(keyword)
    )
  }
  
  // 排序
  if (sortField.value) {
    stocks = [...stocks].sort((a, b) => {
      const aVal = (a as any)[sortField.value]
      const bVal = (b as any)[sortField.value]
      if (sortOrder.value === 'ascending') {
        return aVal - bVal
      } else {
        return bVal - aVal
      }
    })
  }
  
  return stocks
})

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStocks.value.slice(start, end)
})

const loadMyStocks = async () => {
  loading.value = true
  try {
    const response = await stocksAPI.getWatchlist()
    if (response.data.success) {
      myStocks.value = response.data.data.data || []
    } else {
      ElMessage.error('获取自选股票失败')
    }
  } catch (error) {
    console.error('获取自选股票失败:', error)
    ElMessage.error('获取自选股票失败')
  } finally {
    loading.value = false
  }
}

const searchStocks = () => {
  currentPage.value = 1
}

const searchAvailableStocks = async () => {
  if (!addSearchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  searchLoading.value = true
  try {
    const response = await stocksAPI.searchStocks({
      q: addSearchKeyword.value,
      limit: 20
    })
    
    if (response.data.success) {
      // 获取当前自选股票代码列表
      const myStockCodes = new Set(myStocks.value.map(stock => stock.code))
      
      // 转换搜索结果格式以匹配前端期望的格式
      const searchResults = response.data.data.map((stock: any) => ({
        id: stock.stock_code,
        code: stock.stock_code,
        name: stock.stock_name,
        market: stock.market,
        industry: stock.industry || '--',
        price: 0, // 搜索结果不包含价格信息
        change_percent: 0,
        change_amount: 0,
        volume: 0,
        turnover: 0,
        turnover_rate: 0,
        market_cap: 0,
        inWatchlist: myStockCodes.has(stock.stock_code) // 检查是否已在自选列表中
      }))
      availableStocks.value = searchResults
    } else {
      ElMessage.error('搜索股票失败')
    }
  } catch (error) {
    console.error('搜索股票失败:', error)
    ElMessage.error('搜索股票失败')
  } finally {
    searchLoading.value = false
  }
}

const refreshData = () => {
  loadMyStocks()
}

const handleSelectionChange = (selection: Stock[]) => {
  selectedStocks.value = selection
}

const handleAddSelectionChange = (selection: Stock[]) => {
  // 过滤掉已经在自选列表中的股票
  selectedAddStocks.value = selection.filter(stock => !stock.inWatchlist)
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortField.value = prop
  sortOrder.value = order
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const addSelectedStocks = async () => {
  if (selectedAddStocks.value.length === 0) {
    ElMessage.warning('请选择要添加的股票')
    return
  }
  
  try {
    for (const stock of selectedAddStocks.value) {
      await stocksAPI.addToWatchlist({
        stock_code: stock.code
      })
    }
    
    ElMessage.success(`成功添加 ${selectedAddStocks.value.length} 只股票到自选`)
    showAddDialog.value = false
    addSearchKeyword.value = ''
    availableStocks.value = []
    selectedAddStocks.value = []
    
    // 刷新自选股票列表
    await loadMyStocks()
  } catch (error) {
    console.error('添加股票失败:', error)
    ElMessage.error('添加股票失败')
  }
}

const removeFromWatchlist = async (stock: Stock) => {
  try {
    await ElMessageBox.confirm(`确定要从自选中移除 ${stock.name} 吗？`, '移除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await stocksAPI.removeFromWatchlist({ stock_code: stock.code })
    ElMessage.success('移除成功')
    
    // 刷新列表
    await loadMyStocks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除股票失败:', error)
      ElMessage.error('移除股票失败')
    }
  }
}

const batchRemove = async () => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请选择要移除的股票')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要移除选中的 ${selectedStocks.value.length} 只股票吗？`, '批量移除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    for (const stock of selectedStocks.value) {
      await stocksAPI.removeFromWatchlist({ stock_code: stock.code })
    }
    
    ElMessage.success(`成功移除 ${selectedStocks.value.length} 只股票`)
    selectedStocks.value = []
    
    // 刷新列表
    await loadMyStocks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量移除失败:', error)
      ElMessage.error('批量移除失败')
    }
  }
}

const viewStockDetail = (stock: Stock) => {
  ElMessage.info(`查看 ${stock.name} 详情功能开发中...`)
}

const formatPrice = (price: number): string => {
  return price?.toFixed(2) || '--'
}

const formatPercent = (percent: number): string => {
  if (percent === undefined || percent === null) return '--'
  const sign = percent >= 0 ? '+' : ''
  return `${sign}${percent.toFixed(2)}%`
}

const formatVolume = (volume: number): string => {
  if (!volume) return '--'
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}

const formatAmount = (amount: number): string => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toFixed(2)
}

const getPriceClass = (changePercent: number): string => {
  if (changePercent > 0) return 'positive'
  if (changePercent < 0) return 'negative'
  return 'neutral'
}

onMounted(() => {
  loadMyStocks()
})
</script>

<style scoped>
.my-stocks {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stats-section {
  margin-bottom: 20px;
}

.stats-card {
  height: 100px;
}

.stats-item {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 10px;
}

.stats-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stats-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.rising {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.falling {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.neutral {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stocks-table {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  text-align: right;
  margin-top: 15px;
}

.add-stock-section {
  margin-bottom: 20px;
}

.search-results {
  margin-top: 20px;
}

.empty-search {
  margin-top: 20px;
  text-align: center;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

.neutral {
  color: #909399;
}

.danger {
  color: #f56c6c;
}

:deep(.el-table .el-table__cell) {
  padding: 8px 0;
}
</style>