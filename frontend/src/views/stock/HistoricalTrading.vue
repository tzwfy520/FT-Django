<template>
  <div class="historical-trading">
    <div class="page-header">
      <h2>历史交易数据</h2>
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
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="showTaskDialog">
          <el-icon><Setting /></el-icon>
          数据采集
        </el-button>
      </div>
    </div>

    <!-- 查询条件 -->
    <div class="query-section">
      <el-card>
        <template #header>
          <span>查询条件</span>
        </template>
        
        <el-form :model="queryForm" :inline="true" label-width="80px">
          <el-form-item label="股票代码">
            <el-input 
              v-model="queryForm.stockCode" 
              placeholder="请输入股票代码"
              style="width: 150px;"
              @blur="getStockInfo"
            />
          </el-form-item>
          <el-form-item label="股票名称">
            <el-input 
              v-model="queryForm.stockName" 
              placeholder="自动获取"
              style="width: 150px;"
              readonly
            />
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker
              v-model="queryForm.startDate"
              type="date"
              placeholder="选择开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker
              v-model="queryForm.endDate"
              type="date"
              placeholder="选择结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="queryHistoricalData" :loading="loading">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetQuery">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 股票基本信息 -->
    <div v-if="stockInfo" class="stock-info">
      <el-card>
        <template #header>
          <div class="stock-header">
            <span>{{ stockInfo.name }} ({{ stockInfo.code }})</span>
            <div class="stock-actions">
              <el-button size="small" @click="addToWatchlist">
                <el-icon><Star /></el-icon>
                加入自选
              </el-button>
              <el-button size="small" @click="viewRealtime">
                <el-icon><View /></el-icon>
                实时数据
              </el-button>
            </div>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">现价</div>
              <div class="info-value" :class="getChangeClass(stockInfo.changePercent)">
                {{ stockInfo.price?.toFixed(2) || '--' }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌幅</div>
              <div class="info-value" :class="getChangeClass(stockInfo.changePercent)">
                {{ formatChange(stockInfo.changePercent) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌额</div>
              <div class="info-value" :class="getChangeClass(stockInfo.changeAmount)">
                {{ formatChangeAmount(stockInfo.changeAmount) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交量</div>
              <div class="info-value">{{ formatVolume(stockInfo.volume) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交额</div>
              <div class="info-value">{{ formatAmount(stockInfo.turnover) }}万</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">换手率</div>
              <div class="info-value">{{ stockInfo.turnoverRate?.toFixed(2) || '--' }}%</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 历史数据Tab页签 -->
    <div v-if="queryForm.stockCode" class="data-tabs">
      <el-card>
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <!-- 每日数据 -->
          <el-tab-pane label="每日数据" name="daily">
            <HistoryDataTable
              :data="dailyData"
              :loading="dailyLoading"
              :pagination="dailyPagination"
              @page-change="handleDailyPageChange"
              @size-change="handleDailySizeChange"
            />
          </el-tab-pane>
          
          <!-- 每周数据 -->
          <el-tab-pane label="每周数据" name="weekly">
            <HistoryDataTable
              :data="weeklyData"
              :loading="weeklyLoading"
              :pagination="weeklyPagination"
              @page-change="handleWeeklyPageChange"
              @size-change="handleWeeklySizeChange"
            />
          </el-tab-pane>
          
          <!-- 每月数据 -->
          <el-tab-pane label="每月数据" name="monthly">
            <HistoryDataTable
              :data="monthlyData"
              :loading="monthlyLoading"
              :pagination="monthlyPagination"
              @page-change="handleMonthlyPageChange"
              @size-change="handleMonthlySizeChange"
            />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 数据采集任务对话框 -->
    <el-dialog v-model="taskDialogVisible" title="历史数据采集" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="股票代码">
          <el-input
            v-model="taskForm.stockCodes"
            placeholder="请输入股票代码，多个用逗号分隔"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="taskForm.taskType" style="width: 100%;">
            <el-option label="历史数据-前复权" value="stock_history_qfq" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createTask" :loading="taskCreating">
            创建任务
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Setting, Star, View } from '@element-plus/icons-vue'
import HistoryDataTable from './components/HistoryDataTable.vue'
import { stockApi } from '@/services/api'

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const activeTab = ref('daily')
const taskDialogVisible = ref(false)
const taskCreating = ref(false)

// 查询表单
const queryForm = reactive({
  stockCode: '',
  stockName: '',
  startDate: '',
  endDate: ''
})

// 股票信息
const stockInfo = ref(null)

// 每日数据
const dailyData = ref([])
const dailyLoading = ref(false)
const dailyPagination = reactive({
  currentPage: 1,
  pageSize: 50,
  total: 0
})

// 每周数据
const weeklyData = ref([])
const weeklyLoading = ref(false)
const weeklyPagination = reactive({
  currentPage: 1,
  pageSize: 50,
  total: 0
})

// 每月数据
const monthlyData = ref([])
const monthlyLoading = ref(false)
const monthlyPagination = reactive({
  currentPage: 1,
  pageSize: 50,
  total: 0
})

// 任务表单
const taskForm = reactive({
  stockCodes: '',
  taskType: 'stock_history_qfq'
})

// 方法
const searchStocks = () => {
  // 实现股票搜索逻辑
  console.log('搜索股票:', searchKeyword.value)
}

const refreshData = () => {
  if (queryForm.stockCode) {
    queryHistoricalData()
  }
}

const getStockInfo = async () => {
  if (!queryForm.stockCode) {
    stockInfo.value = null
    return
  }
  
  try {
    // 这里应该调用获取股票基本信息的API
    // const response = await stockApi.getStockInfo(queryForm.stockCode)
    // stockInfo.value = response.data
    
    // 临时模拟数据
    stockInfo.value = {
      code: queryForm.stockCode,
      name: '股票名称',
      price: 10.50,
      changePercent: 2.5,
      changeAmount: 0.26,
      volume: 1000000,
      turnover: 10500000,
      turnoverRate: 1.5
    }
    
    queryForm.stockName = stockInfo.value.name
  } catch (error) {
    console.error('获取股票信息失败:', error)
    ElMessage.error('获取股票信息失败')
  }
}

const queryHistoricalData = () => {
  if (!queryForm.stockCode) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  // 根据当前活跃的tab加载对应数据
  switch (activeTab.value) {
    case 'daily':
      loadDailyData()
      break
    case 'weekly':
      loadWeeklyData()
      break
    case 'monthly':
      loadMonthlyData()
      break
  }
}

const loadDailyData = async () => {
  dailyLoading.value = true
  try {
    const params = {
      stock_code: queryForm.stockCode,
      start_date: queryForm.startDate,
      end_date: queryForm.endDate,
      page: dailyPagination.currentPage,
      page_size: dailyPagination.pageSize
    }
    
    const response = await stockApi.getDailyHistoryData(queryForm.stockCode, params)
    if (response.success) {
      dailyData.value = response.data.data
      dailyPagination.total = response.data.pagination.total_count
    } else {
      ElMessage.error(response.message || '获取每日数据失败')
    }
  } catch (error) {
    console.error('获取每日数据失败:', error)
    ElMessage.error('获取每日数据失败')
  } finally {
    dailyLoading.value = false
  }
}

const loadWeeklyData = async () => {
  weeklyLoading.value = true
  try {
    const params = {
      stock_code: queryForm.stockCode,
      start_date: queryForm.startDate,
      end_date: queryForm.endDate,
      page: weeklyPagination.currentPage,
      page_size: weeklyPagination.pageSize
    }
    
    const response = await stockApi.getWeeklyHistoryData(queryForm.stockCode, params)
    if (response.success) {
      weeklyData.value = response.data.data
      weeklyPagination.total = response.data.pagination.total_count
    } else {
      ElMessage.error(response.message || '获取每周数据失败')
    }
  } catch (error) {
    console.error('获取每周数据失败:', error)
    ElMessage.error('获取每周数据失败')
  } finally {
    weeklyLoading.value = false
  }
}

const loadMonthlyData = async () => {
  monthlyLoading.value = true
  try {
    const params = {
      stock_code: queryForm.stockCode,
      start_date: queryForm.startDate,
      end_date: queryForm.endDate,
      page: monthlyPagination.currentPage,
      page_size: monthlyPagination.pageSize
    }
    
    const response = await stockApi.getMonthlyHistoryData(queryForm.stockCode, params)
    if (response.success) {
      monthlyData.value = response.data.data
      monthlyPagination.total = response.data.pagination.total_count
    } else {
      ElMessage.error(response.message || '获取每月数据失败')
    }
  } catch (error) {
    console.error('获取每月数据失败:', error)
    ElMessage.error('获取每月数据失败')
  } finally {
    monthlyLoading.value = false
  }
}

const handleTabChange = (tabName) => {
  activeTab.value = tabName
  if (queryForm.stockCode) {
    queryHistoricalData()
  }
}

// 分页处理
const handleDailyPageChange = (page) => {
  dailyPagination.currentPage = page
  loadDailyData()
}

const handleDailySizeChange = (size) => {
  dailyPagination.pageSize = size
  dailyPagination.currentPage = 1
  loadDailyData()
}

const handleWeeklyPageChange = (page) => {
  weeklyPagination.currentPage = page
  loadWeeklyData()
}

const handleWeeklySizeChange = (size) => {
  weeklyPagination.pageSize = size
  weeklyPagination.currentPage = 1
  loadWeeklyData()
}

const handleMonthlyPageChange = (page) => {
  monthlyPagination.currentPage = page
  loadMonthlyData()
}

const handleMonthlySizeChange = (size) => {
  monthlyPagination.pageSize = size
  monthlyPagination.currentPage = 1
  loadMonthlyData()
}

const resetQuery = () => {
  queryForm.stockCode = ''
  queryForm.stockName = ''
  queryForm.startDate = ''
  queryForm.endDate = ''
  stockInfo.value = null
  dailyData.value = []
  weeklyData.value = []
  monthlyData.value = []
}

const addToWatchlist = async () => {
  try {
    // 调用添加自选股API
    ElMessage.success('已添加到自选股')
  } catch (error) {
    ElMessage.error('添加自选股失败')
  }
}

const viewRealtime = () => {
  // 跳转到实时数据页面
  console.log('查看实时数据')
}

const showTaskDialog = () => {
  taskDialogVisible.value = true
  if (queryForm.stockCode) {
    taskForm.stockCodes = queryForm.stockCode
  }
}

const createTask = async () => {
  if (!taskForm.stockCodes.trim()) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  taskCreating.value = true
  try {
    const stockCodes = taskForm.stockCodes.split(',').map(code => code.trim()).filter(code => code)
    const response = await stockApi.createHistoryTask({
      stock_codes: stockCodes,
      task_type: taskForm.taskType
    })
    
    if (response.success) {
      ElMessage.success(response.data.message || '任务创建成功')
      taskDialogVisible.value = false
      taskForm.stockCodes = ''
    } else {
      ElMessage.error(response.message || '任务创建失败')
    }
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error('创建任务失败')
  } finally {
    taskCreating.value = false
  }
}

// 工具函数
const getChangeClass = (value) => {
  if (!value) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}

const formatChange = (value) => {
  if (!value) return '--'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

const formatChangeAmount = (value) => {
  if (!value) return '--'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}`
}

const formatVolume = (value) => {
  if (!value) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toString()
}

const formatAmount = (value) => {
  if (!value) return '--'
  return (value / 10000).toFixed(2)
}

onMounted(() => {
  // 组件挂载时的初始化逻辑
})
</script>

<style scoped>
.historical-trading {
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
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.query-section {
  margin-bottom: 20px;
}

.stock-info {
  margin-bottom: 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-actions {
  display: flex;
  gap: 10px;
}

.info-item {
  text-align: center;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.info-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.info-value.positive {
  color: #f56c6c;
}

.info-value.negative {
  color: #67c23a;
}

.data-tabs {
  margin-bottom: 20px;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>