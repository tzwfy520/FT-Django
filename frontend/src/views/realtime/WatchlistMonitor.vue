<template>
  <div class="watchlist-monitor">
    <div class="page-header">
      <h2>自选股票实时监控</h2>
      <div class="header-actions">
        <div class="market-status">
          <el-tag :type="marketStatus.type" size="large">
            <el-icon><Clock /></el-icon>
            {{ marketStatus.text }}
          </el-tag>
        </div>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="manageWatchlist">
          <el-icon><Setting /></el-icon>
          管理自选
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 市场概况 -->
    <div class="market-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon up">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.rising }}</div>
                <div class="overview-label">上涨</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon down">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.falling }}</div>
                <div class="overview-label">下跌</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon neutral">
                <el-icon><Minus /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.flat }}</div>
                <div class="overview-label">平盘</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon">
                <el-icon><Star /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ watchlistStocks.length }}</div>
                <div class="overview-label">自选总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和排序 -->
    <div class="filter-section">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="4">
            <el-select v-model="filterType" placeholder="筛选类型" @change="applyFilter">
              <el-option label="全部" value="all" />
              <el-option label="上涨" value="rising" />
              <el-option label="下跌" value="falling" />
              <el-option label="平盘" value="flat" />
              <el-option label="涨停" value="limit_up" />
              <el-option label="跌停" value="limit_down" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="sortBy" placeholder="排序方式" @change="applySorting">
              <el-option label="涨跌幅" value="changePercent" />
              <el-option label="涨跌额" value="changeAmount" />
              <el-option label="成交量" value="volume" />
              <el-option label="成交额" value="turnover" />
              <el-option label="现价" value="currentPrice" />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-radio-group v-model="sortOrder" @change="applySorting">
              <el-radio-button label="desc">降序</el-radio-button>
              <el-radio-button label="asc">升序</el-radio-button>
            </el-radio-group>
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索股票代码/名称"
              @input="applySearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="3">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
          </el-col>
          <el-col :span="6">
            <div class="refresh-info">
              <span>更新时间: {{ lastUpdateTime }}</span>
              <span v-if="autoRefresh" class="countdown">({{ countdown }}s)</span>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 自选股票列表 -->
    <div class="stocks-list">
      <el-card>
        <template #header>
          <div class="list-header">
            <span>自选股票实时数据 ({{ filteredStocks.length }})</span>
            <div class="list-actions">
              <el-button size="small" @click="selectAll">
                {{ selectedStocks.length === filteredStocks.length ? '取消全选' : '全选' }}
              </el-button>
              <el-button size="small" @click="batchRemove" :disabled="selectedStocks.length === 0">
                批量移除
              </el-button>
              <el-button size="small" @click="batchAlert" :disabled="selectedStocks.length === 0">
                批量预警
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedStocks" 
          stripe 
          height="600"
          @selection-change="handleSelectionChange"
          @row-click="viewStockDetail"
          row-class-name="stock-row"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="code" label="代码" width="100" fixed="left">
            <template #default="{ row }">
              <div class="stock-code">
                <span>{{ row.code }}</span>
                <el-tag v-if="row.isLimitUp" type="danger" size="small">涨停</el-tag>
                <el-tag v-else-if="row.isLimitDown" type="success" size="small">跌停</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称" width="120" fixed="left">
            <template #default="{ row }">
              <div class="stock-name">
                <span>{{ row.name }}</span>
                <el-icon v-if="row.hasAlert" class="alert-icon"><Bell /></el-icon>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="currentPrice" label="现价" width="100" sortable>
            <template #default="{ row }">
              <span class="price" :class="getPriceClass(row.changePercent)">
                {{ row.currentPrice.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100" sortable>
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changeAmount" label="涨跌额" width="100" sortable>
            <template #default="{ row }">
              <span :class="getChangeClass(row.changeAmount)">
                {{ formatChangeAmount(row.changeAmount) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120" sortable>
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="120" sortable>
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}万</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnoverRate" label="换手率" width="100" sortable>
            <template #default="{ row }">
              <span>{{ row.turnoverRate.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="pe" label="市盈率" width="100" sortable>
            <template #default="{ row }">
              <span>{{ row.pe > 0 ? row.pe.toFixed(2) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pb" label="市净率" width="100" sortable>
            <template #default="{ row }">
              <span>{{ row.pb.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="分时图" width="150">
            <template #default="{ row }">
              <div class="mini-chart" :ref="el => setChartRef(el, row.code)"></div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click.stop="viewDetail(row)">
                详情
              </el-button>
              <el-button size="small" @click.stop="setAlert(row)">
                预警
              </el-button>
              <el-button size="small" type="danger" @click.stop="removeFromWatchlist(row)">
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

    <!-- 股票详情对话框 -->
    <el-dialog v-model="detailDialog" :title="selectedStock?.name" width="1000px">
      <div v-if="selectedStock" class="stock-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-chart" ref="detailChartContainer"></div>
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="股票代码">{{ selectedStock.code }}</el-descriptions-item>
              <el-descriptions-item label="股票名称">{{ selectedStock.name }}</el-descriptions-item>
              <el-descriptions-item label="现价">{{ selectedStock.currentPrice.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="涨跌幅">
                <span :class="getChangeClass(selectedStock.changePercent)">
                  {{ formatChange(selectedStock.changePercent) }}
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="开盘价">{{ selectedStock.openPrice.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="最高价">{{ selectedStock.highPrice.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="最低价">{{ selectedStock.lowPrice.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="昨收价">{{ selectedStock.prevClose.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="成交量">{{ formatVolume(selectedStock.volume) }}</el-descriptions-item>
              <el-descriptions-item label="成交额">{{ formatAmount(selectedStock.turnover) }}万</el-descriptions-item>
              <el-descriptions-item label="市盈率">{{ selectedStock.pe > 0 ? selectedStock.pe.toFixed(2) : '-' }}</el-descriptions-item>
              <el-descriptions-item label="市净率">{{ selectedStock.pb.toFixed(2) }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="detailDialog = false">关闭</el-button>
        <el-button type="primary" @click="viewFullDetail">
          查看完整详情
        </el-button>
      </template>
    </el-dialog>

    <!-- 预警设置对话框 -->
    <el-dialog v-model="alertDialog" title="设置价格预警" width="500px">
      <el-form :model="alertForm" label-width="100px">
        <el-form-item label="股票">
          <el-input v-model="alertForm.stockName" readonly />
        </el-form-item>
        <el-form-item label="当前价格">
          <el-input v-model="alertForm.currentPrice" readonly />
        </el-form-item>
        <el-form-item label="预警类型">
          <el-radio-group v-model="alertForm.type">
            <el-radio label="price_up">价格上涨到</el-radio>
            <el-radio label="price_down">价格下跌到</el-radio>
            <el-radio label="change_up">涨幅达到</el-radio>
            <el-radio label="change_down">跌幅达到</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="预警值">
          <el-input v-model="alertForm.value" placeholder="请输入预警值">
            <template #suffix>
              <span v-if="alertForm.type.includes('change')">%</span>
              <span v-else>元</span>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="预警方式">
          <el-checkbox-group v-model="alertForm.methods">
            <el-checkbox label="popup">弹窗提醒</el-checkbox>
            <el-checkbox label="sound">声音提醒</el-checkbox>
            <el-checkbox label="email">邮件通知</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="alertDialog = false">取消</el-button>
        <el-button type="primary" @click="saveAlert">
          保存预警
        </el-button>
      </template>
    </el-dialog>

    <!-- 管理自选对话框 -->
    <el-dialog v-model="manageDialog" title="管理自选股票" width="800px">
      <div class="manage-content">
        <div class="manage-header">
          <el-input
            v-model="addStockCode"
            placeholder="输入股票代码添加到自选"
            style="width: 200px;"
            @keyup.enter="addToWatchlist"
          >
            <template #append>
              <el-button @click="addToWatchlist">添加</el-button>
            </template>
          </el-input>
          <el-button @click="importWatchlist">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
        
        <el-table :data="watchlistStocks" stripe max-height="400">
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="addTime" label="添加时间" width="150" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="removeStock(row)">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="manageDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Clock, Refresh, Setting, Download, TrendCharts, Minus, Star, 
  Search, Bell, Upload 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface Stock {
  code: string
  name: string
  currentPrice: number
  changePercent: number
  changeAmount: number
  openPrice: number
  highPrice: number
  lowPrice: number
  prevClose: number
  volume: number
  turnover: number
  turnoverRate: number
  pe: number
  pb: number
  isLimitUp: boolean
  isLimitDown: boolean
  hasAlert: boolean
  addTime: string
}

interface MarketStatus {
  type: 'success' | 'warning' | 'danger'
  text: string
}

interface AlertForm {
  stockCode: string
  stockName: string
  currentPrice: string
  type: string
  value: string
  methods: string[]
}

const loading = ref(false)
const autoRefresh = ref(true)
const countdown = ref(30)
const lastUpdateTime = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const filterType = ref('all')
const sortBy = ref('changePercent')
const sortOrder = ref('desc')
const searchKeyword = ref('')
const detailDialog = ref(false)
const alertDialog = ref(false)
const manageDialog = ref(false)
const addStockCode = ref('')
const selectedStocks = ref<Stock[]>([])
const selectedStock = ref<Stock | null>(null)
const detailChartContainer = ref<HTMLElement>()
const chartRefs = ref<Map<string, HTMLElement>>(new Map())

const marketStatus = ref<MarketStatus>({
  type: 'success',
  text: '交易中 09:30-15:00'
})

const marketOverview = ref({
  rising: 0,
  falling: 0,
  flat: 0
})

const watchlistStocks = ref<Stock[]>([])

const alertForm = ref<AlertForm>({
  stockCode: '',
  stockName: '',
  currentPrice: '',
  type: 'price_up',
  value: '',
  methods: ['popup']
})

let refreshTimer: NodeJS.Timeout | null = null
let countdownTimer: NodeJS.Timeout | null = null

const filteredStocks = computed(() => {
  let result = [...watchlistStocks.value]
  
  // 筛选
  if (filterType.value !== 'all') {
    result = result.filter(stock => {
      switch (filterType.value) {
        case 'rising':
          return stock.changePercent > 0
        case 'falling':
          return stock.changePercent < 0
        case 'flat':
          return stock.changePercent === 0
        case 'limit_up':
          return stock.isLimitUp
        case 'limit_down':
          return stock.isLimitDown
        default:
          return true
      }
    })
  }
  
  // 搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(stock => 
      stock.code.toLowerCase().includes(keyword) || 
      stock.name.toLowerCase().includes(keyword)
    )
  }
  
  // 排序
  result.sort((a, b) => {
    const aValue = a[sortBy.value as keyof Stock] as number
    const bValue = b[sortBy.value as keyof Stock] as number
    return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
  })
  
  return result
})

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStocks.value.slice(start, end)
})

const loadWatchlistData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟自选股数据
    const mockStocks: Stock[] = [
      { code: '000001', name: '平安银行', addTime: '2024-01-15' },
      { code: '000002', name: '万科A', addTime: '2024-01-16' },
      { code: '000858', name: '五粮液', addTime: '2024-01-17' },
      { code: '600036', name: '招商银行', addTime: '2024-01-18' },
      { code: '600519', name: '贵州茅台', addTime: '2024-01-19' },
      { code: '000725', name: '京东方A', addTime: '2024-01-20' },
      { code: '002415', name: '海康威视', addTime: '2024-01-21' },
      { code: '300059', name: '东方财富', addTime: '2024-01-22' }
    ].map(stock => {
      const basePrice = Math.random() * 100 + 10
      const changePercent = (Math.random() - 0.5) * 10
      const changeAmount = (basePrice * changePercent) / 100
      const currentPrice = basePrice + changeAmount
      
      return {
        ...stock,
        currentPrice,
        changePercent,
        changeAmount,
        openPrice: basePrice + (Math.random() - 0.5) * 2,
        highPrice: currentPrice + Math.random() * 3,
        lowPrice: currentPrice - Math.random() * 3,
        prevClose: basePrice,
        volume: Math.floor(Math.random() * 50000000 + 1000000),
        turnover: Math.floor(Math.random() * 500000 + 10000),
        turnoverRate: Math.random() * 5,
        pe: Math.random() * 50 + 5,
        pb: Math.random() * 5 + 0.5,
        isLimitUp: Math.random() < 0.05,
        isLimitDown: Math.random() < 0.05,
        hasAlert: Math.random() < 0.3
      }
    })
    
    watchlistStocks.value = mockStocks
    
    // 更新市场概况
    marketOverview.value = {
      rising: mockStocks.filter(s => s.changePercent > 0).length,
      falling: mockStocks.filter(s => s.changePercent < 0).length,
      flat: mockStocks.filter(s => s.changePercent === 0).length
    }
    
    lastUpdateTime.value = new Date().toLocaleTimeString()
    
    // 渲染迷你图表
    await nextTick()
    renderMiniCharts()
    
  } catch (error) {
    ElMessage.error('加载自选股数据失败')
  } finally {
    loading.value = false
  }
}

const renderMiniCharts = () => {
  paginatedStocks.value.forEach(stock => {
    const container = chartRefs.value.get(stock.code)
    if (container) {
      const chart = echarts.init(container)
      
      // 生成模拟分时数据
      const timeData = []
      const priceData = []
      let basePrice = stock.prevClose
      
      for (let i = 0; i < 240; i++) { // 4小时 * 60分钟
        const time = new Date()
        time.setHours(9, 30 + i, 0, 0)
        timeData.push(time.toTimeString().slice(0, 5))
        
        basePrice += (Math.random() - 0.5) * 0.5
        priceData.push(basePrice)
      }
      
      const option = {
        grid: {
          left: 0,
          right: 0,
          top: 0,
          bottom: 0
        },
        xAxis: {
          type: 'category',
          data: timeData,
          show: false
        },
        yAxis: {
          type: 'value',
          show: false,
          scale: true
        },
        series: [{
          type: 'line',
          data: priceData,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1,
            color: stock.changePercent >= 0 ? '#f56c6c' : '#67c23a'
          },
          areaStyle: {
            opacity: 0.3,
            color: stock.changePercent >= 0 ? '#f56c6c' : '#67c23a'
          }
        }]
      }
      
      chart.setOption(option)
    }
  })
}

const setChartRef = (el: HTMLElement | null, code: string) => {
  if (el) {
    chartRefs.value.set(code, el)
  }
}

const refreshData = () => {
  loadWatchlistData()
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  countdown.value = 30
  
  refreshTimer = setInterval(() => {
    loadWatchlistData()
    countdown.value = 30
  }, 30000)
  
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = 30
    }
  }, 1000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

const applyFilter = () => {
  currentPage.value = 1
}

const applySorting = () => {
  // 排序逻辑已在computed中处理
}

const applySearch = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection: Stock[]) => {
  selectedStocks.value = selection
}

const selectAll = () => {
  // 全选逻辑
}

const batchRemove = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要移除选中的 ${selectedStocks.value.length} 只股票吗？`,
      '批量移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const codes = selectedStocks.value.map(s => s.code)
    watchlistStocks.value = watchlistStocks.value.filter(s => !codes.includes(s.code))
    selectedStocks.value = []
    
    ElMessage.success('批量移除成功')
  } catch {
    // 用户取消
  }
}

const batchAlert = () => {
  ElMessage.info('批量预警功能开发中...')
}

const viewStockDetail = (stock: Stock) => {
  selectedStock.value = stock
  detailDialog.value = true
  
  nextTick(() => {
    if (detailChartContainer.value) {
      const chart = echarts.init(detailChartContainer.value)
      
      // 生成详细分时图
      const timeData = []
      const priceData = []
      let basePrice = stock.prevClose
      
      for (let i = 0; i < 240; i++) {
        const time = new Date()
        time.setHours(9, 30 + i, 0, 0)
        timeData.push(time.toTimeString().slice(0, 5))
        
        basePrice += (Math.random() - 0.5) * 0.5
        priceData.push(basePrice)
      }
      
      const option = {
        title: {
          text: `${stock.name} 分时走势`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: timeData
        },
        yAxis: {
          type: 'value',
          scale: true
        },
        series: [{
          type: 'line',
          data: priceData,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            color: stock.changePercent >= 0 ? '#f56c6c' : '#67c23a'
          }
        }]
      }
      
      chart.setOption(option)
    }
  })
}

const viewDetail = (stock: Stock) => {
  viewStockDetail(stock)
}

const setAlert = (stock: Stock) => {
  alertForm.value = {
    stockCode: stock.code,
    stockName: stock.name,
    currentPrice: stock.currentPrice.toFixed(2),
    type: 'price_up',
    value: '',
    methods: ['popup']
  }
  alertDialog.value = true
}

const saveAlert = () => {
  if (!alertForm.value.value) {
    ElMessage.error('请输入预警值')
    return
  }
  
  ElMessage.success('预警设置成功')
  alertDialog.value = false
}

const removeFromWatchlist = async (stock: Stock) => {
  try {
    await ElMessageBox.confirm(
      `确定要从自选中移除 ${stock.name} 吗？`,
      '移除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    watchlistStocks.value = watchlistStocks.value.filter(s => s.code !== stock.code)
    ElMessage.success('移除成功')
  } catch {
    // 用户取消
  }
}

const manageWatchlist = () => {
  manageDialog.value = true
}

const addToWatchlist = () => {
  if (!addStockCode.value) {
    ElMessage.error('请输入股票代码')
    return
  }
  
  if (watchlistStocks.value.some(s => s.code === addStockCode.value)) {
    ElMessage.warning('该股票已在自选中')
    return
  }
  
  // 模拟添加股票
  const newStock: Stock = {
    code: addStockCode.value,
    name: '新股票',
    currentPrice: Math.random() * 100 + 10,
    changePercent: (Math.random() - 0.5) * 10,
    changeAmount: 0,
    openPrice: 0,
    highPrice: 0,
    lowPrice: 0,
    prevClose: 0,
    volume: 0,
    turnover: 0,
    turnoverRate: 0,
    pe: 0,
    pb: 0,
    isLimitUp: false,
    isLimitDown: false,
    hasAlert: false,
    addTime: new Date().toISOString().split('T')[0]
  }
  
  watchlistStocks.value.push(newStock)
  addStockCode.value = ''
  ElMessage.success('添加成功')
}

const removeStock = (stock: Stock) => {
  watchlistStocks.value = watchlistStocks.value.filter(s => s.code !== stock.code)
  ElMessage.success('移除成功')
}

const importWatchlist = () => {
  ElMessage.info('导入功能开发中...')
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const viewFullDetail = () => {
  ElMessage.info(`跳转到${selectedStock.value?.name}详情页面`)
  detailDialog.value = false
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  nextTick(() => {
    renderMiniCharts()
  })
}

const formatAmount = (amount: number): string => {
  return Math.abs(amount).toFixed(2)
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : ''
  return sign + change.toFixed(2) + '%'
}

const formatChangeAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2)
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getPriceClass = (change: number): string => {
  return change > 0 ? 'price-up' : change < 0 ? 'price-down' : 'price-flat'
}

// 检查市场状态
const checkMarketStatus = () => {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  const time = hour * 100 + minute
  
  if ((time >= 930 && time <= 1130) || (time >= 1300 && time <= 1500)) {
    marketStatus.value = {
      type: 'success',
      text: '交易中 09:30-15:00'
    }
  } else if (time >= 915 && time < 930) {
    marketStatus.value = {
      type: 'warning',
      text: '集合竞价 09:15-09:30'
    }
  } else {
    marketStatus.value = {
      type: 'danger',
      text: '休市中'
    }
  }
}

onMounted(() => {
  checkMarketStatus()
  loadWatchlistData()
  
  if (autoRefresh.value) {
    startAutoRefresh()
  }
  
  // 每分钟检查市场状态
  setInterval(checkMarketStatus, 60000)
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.watchlist-monitor {
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
  gap: 15px;
  align-items: center;
}

.market-status {
  display: flex;
  align-items: center;
}

.market-overview {
  margin-bottom: 20px;
}

.overview-card {
  height: 100px;
}

.overview-item {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.overview-icon {
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

.overview-icon.up {
  background: #f56c6c;
}

.overview-icon.down {
  background: #67c23a;
}

.overview-icon.neutral {
  background: #909399;
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: #909399;
}

.filter-section {
  margin-bottom: 20px;
}

.refresh-info {
  font-size: 12px;
  color: #909399;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.countdown {
  color: #409eff;
  font-weight: bold;
}

.stocks-list {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-actions {
  display: flex;
  gap: 10px;
}

.stock-row {
  cursor: pointer;
}

.stock-row:hover {
  background-color: #f5f7fa;
}

.stock-code {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stock-name {
  display: flex;
  align-items: center;
  gap: 5px;
}

.alert-icon {
  color: #e6a23c;
}

.price {
  font-weight: bold;
}

.price-up {
  color: #f56c6c;
}

.price-down {
  color: #67c23a;
}

.price-flat {
  color: #909399;
}

.mini-chart {
  width: 120px;
  height: 40px;
}

.pagination-container {
  text-align: right;
  margin-top: 15px;
}

.stock-detail {
  padding: 20px 0;
}

.detail-chart {
  height: 300px;
  width: 100%;
}

.manage-content {
  padding: 20px 0;
}

.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
</style>