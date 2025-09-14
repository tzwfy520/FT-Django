<template>
  <div class="realtime-trading">
    <div class="page-header">
      <h2>实时交易数据</h2>
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
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 市场概况 -->
    <div class="market-overview">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>市场概况</span>
            <div class="overview-actions">
              <el-switch
                v-model="autoRefresh"
                active-text="自动刷新"
                @change="toggleAutoRefresh"
              />
              <span class="update-time">更新时间: {{ updateTime }}</span>
            </div>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon total">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.totalStocks }}</div>
                <div class="overview-label">总股票数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon rising">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value positive">{{ marketOverview.risingStocks }}</div>
                <div class="overview-label">上涨</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon falling">
                <el-icon><CaretBottom /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value negative">{{ marketOverview.fallingStocks }}</div>
                <div class="overview-label">下跌</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon flat">
                <el-icon><Minus /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value neutral">{{ marketOverview.flatStocks }}</div>
                <div class="overview-label">平盘</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon volume">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatVolume(marketOverview.totalVolume) }}</div>
                <div class="overview-label">总成交量</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="overview-item">
              <div class="overview-icon turnover">
                <el-icon><Money /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatAmount(marketOverview.totalTurnover) }}万</div>
                <div class="overview-label">总成交额</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <el-card>
        <template #header>
          <span>筛选条件</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="4">
            <el-form-item label="市场">
              <el-select v-model="filters.market" placeholder="全部" @change="applyFilters">
                <el-option label="全部" value="" />
                <el-option label="沪市A股" value="SH" />
                <el-option label="深市A股" value="SZ" />
                <el-option label="创业板" value="CYB" />
                <el-option label="科创板" value="KCB" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="涨跌幅">
              <el-select v-model="filters.changeRange" placeholder="全部" @change="applyFilters">
                <el-option label="全部" value="" />
                <el-option label="涨停" value="limit_up" />
                <el-option label="跌停" value="limit_down" />
                <el-option label="涨幅>5%" value="up_5" />
                <el-option label="跌幅>5%" value="down_5" />
                <el-option label="涨幅3-5%" value="up_3_5" />
                <el-option label="跌幅3-5%" value="down_3_5" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="价格区间">
              <el-select v-model="filters.priceRange" placeholder="全部" @change="applyFilters">
                <el-option label="全部" value="" />
                <el-option label="<5元" value="0_5" />
                <el-option label="5-10元" value="5_10" />
                <el-option label="10-20元" value="10_20" />
                <el-option label="20-50元" value="20_50" />
                <el-option label=">50元" value="50_" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="成交额">
              <el-select v-model="filters.turnoverRange" placeholder="全部" @change="applyFilters">
                <el-option label="全部" value="" />
                <el-option label="<1千万" value="0_1000" />
                <el-option label="1千万-1亿" value="1000_10000" />
                <el-option label="1-10亿" value="10000_100000" />
                <el-option label=">10亿" value="100000_" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="换手率">
              <el-select v-model="filters.turnoverRateRange" placeholder="全部" @change="applyFilters">
                <el-option label="全部" value="" />
                <el-option label="<1%" value="0_1" />
                <el-option label="1-3%" value="1_3" />
                <el-option label="3-5%" value="3_5" />
                <el-option label="5-10%" value="5_10" />
                <el-option label=">10%" value="10_" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <div class="filter-actions">
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="primary" @click="applyFilters">筛选</el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 实时数据表格 -->
    <div class="trading-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>实时交易数据 ({{ filteredStocks.length }}只)</span>
            <div class="table-actions">
              <el-button size="small" @click="addToWatchlist" :disabled="!selectedStocks.length">
                <el-icon><Star /></el-icon>
                加入自选 ({{ selectedStocks.length }})
              </el-button>
              <el-button size="small" @click="compareStocks" :disabled="selectedStocks.length < 2">
                <el-icon><DataLine /></el-icon>
                对比分析
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedStocks" 
          stripe 
          height="600"
          @selection-change="handleSelectionChange"
          @sort-change="handleSortChange"
          @row-click="viewStockDetail"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="code" label="代码" width="100" sortable="custom" fixed="left" />
          <el-table-column prop="name" label="名称" width="120" sortable="custom" fixed="left">
            <template #default="{ row }">
              <el-button type="text" @click.stop="viewStockDetail(row)">
                {{ row.name }}
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="现价" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ row.price.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changeAmount" label="涨跌额" width="100" sortable="custom">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changeAmount)">
                {{ formatChangeAmount(row.changeAmount) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="openPrice" label="今开" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.openPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="highPrice" label="最高" width="100" sortable="custom">
            <template #default="{ row }">
              <span class="positive">{{ row.highPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lowPrice" label="最低" width="100" sortable="custom">
            <template #default="{ row }">
              <span class="negative">{{ row.lowPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="preClosePrice" label="昨收" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.preClosePrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120" sortable="custom">
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="120" sortable="custom">
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}万</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnoverRate" label="换手率" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.turnoverRate.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="pe" label="市盈率" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.pe > 0 ? row.pe.toFixed(2) : '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pb" label="市净率" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.pb.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="marketCap" label="总市值" width="120" sortable="custom">
            <template #default="{ row }">
              <span>{{ formatAmount(row.marketCap) }}万</span>
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.amplitude.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="text" @click.stop="viewStockDetail(row)">
                详情
              </el-button>
              <el-button size="small" type="text" @click.stop="addSingleToWatchlist(row)">
                自选
              </el-button>
              <el-button size="small" type="text" @click.stop="viewKLine(row)">
                K线
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[50, 100, 200, 500]"
            :total="filteredStocks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 股票详情对话框 -->
    <el-dialog v-model="detailDialog" :title="selectedStock?.name" width="800px">
      <div v-if="selectedStock" class="stock-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-section">
              <h4>基本信息</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="股票代码">{{ selectedStock.code }}</el-descriptions-item>
                <el-descriptions-item label="股票名称">{{ selectedStock.name }}</el-descriptions-item>
                <el-descriptions-item label="现价">
                  <span :class="getChangeClass(selectedStock.changePercent)">
                    {{ selectedStock.price.toFixed(2) }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="涨跌幅">
                  <span :class="getChangeClass(selectedStock.changePercent)">
                    {{ formatChange(selectedStock.changePercent) }}
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="今开">{{ selectedStock.openPrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="昨收">{{ selectedStock.preClosePrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="最高">{{ selectedStock.highPrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="最低">{{ selectedStock.lowPrice.toFixed(2) }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-section">
              <h4>交易数据</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="成交量">{{ formatVolume(selectedStock.volume) }}</el-descriptions-item>
                <el-descriptions-item label="成交额">{{ formatAmount(selectedStock.turnover) }}万</el-descriptions-item>
                <el-descriptions-item label="换手率">{{ selectedStock.turnoverRate.toFixed(2) }}%</el-descriptions-item>
                <el-descriptions-item label="振幅">{{ selectedStock.amplitude.toFixed(2) }}%</el-descriptions-item>
                <el-descriptions-item label="市盈率">{{ selectedStock.pe > 0 ? selectedStock.pe.toFixed(2) : '--' }}</el-descriptions-item>
                <el-descriptions-item label="市净率">{{ selectedStock.pb.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="总市值">{{ formatAmount(selectedStock.marketCap) }}万</el-descriptions-item>
                <el-descriptions-item label="流通市值">{{ formatAmount(selectedStock.marketCap * 0.8) }}万</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="detailDialog = false">关闭</el-button>
        <el-button type="primary" @click="addSingleToWatchlist(selectedStock!)">
          加入自选
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, Refresh, Download, TrendCharts, CaretTop, CaretBottom, 
  Minus, DataAnalysis, Money, Star, DataLine 
} from '@element-plus/icons-vue'

interface Stock {
  id: string
  code: string
  name: string
  price: number
  changePercent: number
  changeAmount: number
  openPrice: number
  highPrice: number
  lowPrice: number
  preClosePrice: number
  volume: number
  turnover: number
  turnoverRate: number
  pe: number
  pb: number
  marketCap: number
  amplitude: number
  market: string
}

interface MarketOverview {
  totalStocks: number
  risingStocks: number
  fallingStocks: number
  flatStocks: number
  totalVolume: number
  totalTurnover: number
}

interface Filters {
  market: string
  changeRange: string
  priceRange: string
  turnoverRange: string
  turnoverRateRange: string
}

const loading = ref(false)
const searchKeyword = ref('')
const autoRefresh = ref(false)
const refreshInterval = ref<NodeJS.Timeout | null>(null)
const updateTime = ref('')
const currentPage = ref(1)
const pageSize = ref(100)
const selectedStocks = ref<Stock[]>([])
const sortField = ref('')
const sortOrder = ref('')
const detailDialog = ref(false)
const selectedStock = ref<Stock | null>(null)

const stocks = ref<Stock[]>([])
const marketOverview = ref<MarketOverview>({
  totalStocks: 0,
  risingStocks: 0,
  fallingStocks: 0,
  flatStocks: 0,
  totalVolume: 0,
  totalTurnover: 0
})

const filters = ref<Filters>({
  market: '',
  changeRange: '',
  priceRange: '',
  turnoverRange: '',
  turnoverRateRange: ''
})

const filteredStocks = computed(() => {
  let result = stocks.value
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(stock => 
      stock.code.toLowerCase().includes(keyword) || 
      stock.name.toLowerCase().includes(keyword)
    )
  }
  
  // 市场过滤
  if (filters.value.market) {
    result = result.filter(stock => stock.market === filters.value.market)
  }
  
  // 涨跌幅过滤
  if (filters.value.changeRange) {
    const range = filters.value.changeRange
    result = result.filter(stock => {
      switch (range) {
        case 'limit_up': return stock.changePercent >= 9.9
        case 'limit_down': return stock.changePercent <= -9.9
        case 'up_5': return stock.changePercent > 5
        case 'down_5': return stock.changePercent < -5
        case 'up_3_5': return stock.changePercent >= 3 && stock.changePercent <= 5
        case 'down_3_5': return stock.changePercent >= -5 && stock.changePercent <= -3
        default: return true
      }
    })
  }
  
  // 价格区间过滤
  if (filters.value.priceRange) {
    const range = filters.value.priceRange
    result = result.filter(stock => {
      switch (range) {
        case '0_5': return stock.price < 5
        case '5_10': return stock.price >= 5 && stock.price < 10
        case '10_20': return stock.price >= 10 && stock.price < 20
        case '20_50': return stock.price >= 20 && stock.price < 50
        case '50_': return stock.price >= 50
        default: return true
      }
    })
  }
  
  // 成交额过滤
  if (filters.value.turnoverRange) {
    const range = filters.value.turnoverRange
    result = result.filter(stock => {
      switch (range) {
        case '0_1000': return stock.turnover < 1000
        case '1000_10000': return stock.turnover >= 1000 && stock.turnover < 10000
        case '10000_100000': return stock.turnover >= 10000 && stock.turnover < 100000
        case '100000_': return stock.turnover >= 100000
        default: return true
      }
    })
  }
  
  // 换手率过滤
  if (filters.value.turnoverRateRange) {
    const range = filters.value.turnoverRateRange
    result = result.filter(stock => {
      switch (range) {
        case '0_1': return stock.turnoverRate < 1
        case '1_3': return stock.turnoverRate >= 1 && stock.turnoverRate < 3
        case '3_5': return stock.turnoverRate >= 3 && stock.turnoverRate < 5
        case '5_10': return stock.turnoverRate >= 5 && stock.turnoverRate < 10
        case '10_': return stock.turnoverRate >= 10
        default: return true
      }
    })
  }
  
  // 排序
  if (sortField.value) {
    result = [...result].sort((a, b) => {
      const aVal = (a as any)[sortField.value]
      const bVal = (b as any)[sortField.value]
      if (sortOrder.value === 'ascending') {
        return aVal - bVal
      } else {
        return bVal - aVal
      }
    })
  }
  
  return result
})

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStocks.value.slice(start, end)
})

const loadTradingData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟股票数据
    const mockStocks: Stock[] = []
    const markets = ['SH', 'SZ', 'CYB', 'KCB']
    const stockNames = [
      '平安银行', '万科A', '中国平安', '招商银行', '五粮液', '贵州茅台', '美的集团',
      '格力电器', '海康威视', '恒瑞医药', '中兴通讯', '立讯精密', '宁德时代',
      '比亚迪', '药明康德', '迈瑞医疗', '爱尔眼科', '东方财富', '同花顺', '顺丰控股'
    ]
    
    for (let i = 0; i < 500; i++) {
      const basePrice = Math.random() * 100 + 5
      const changePercent = (Math.random() - 0.5) * 20
      const changeAmount = (basePrice * changePercent) / 100
      const price = basePrice + changeAmount
      const preClosePrice = basePrice
      const openPrice = basePrice + (Math.random() - 0.5) * 2
      const highPrice = Math.max(price, openPrice, basePrice + Math.random() * 3)
      const lowPrice = Math.min(price, openPrice, basePrice - Math.random() * 3)
      const volume = Math.floor(Math.random() * 100000000 + 1000000)
      const turnover = (volume * price) / 10000
      const marketCap = price * (Math.random() * 1000000 + 100000)
      
      mockStocks.push({
        id: (i + 1).toString(),
        code: `${Math.random() > 0.5 ? '00' : '60'}${String(Math.floor(Math.random() * 9999)).padStart(4, '0')}`,
        name: stockNames[i % stockNames.length] + (i > stockNames.length - 1 ? (Math.floor(i / stockNames.length) + 1) : ''),
        price,
        changePercent,
        changeAmount,
        openPrice,
        highPrice,
        lowPrice,
        preClosePrice,
        volume,
        turnover,
        turnoverRate: Math.random() * 10,
        pe: Math.random() * 50 + 5,
        pb: Math.random() * 5 + 0.5,
        marketCap,
        amplitude: ((highPrice - lowPrice) / preClosePrice) * 100,
        market: markets[Math.floor(Math.random() * markets.length)]
      })
    }
    
    stocks.value = mockStocks
    updateMarketOverview()
    updateTime.value = new Date().toLocaleTimeString()
    
    ElMessage.success('实时交易数据加载成功')
  } catch (error) {
    ElMessage.error('加载实时交易数据失败')
  } finally {
    loading.value = false
  }
}

const updateMarketOverview = () => {
  const totalStocks = stocks.value.length
  const risingStocks = stocks.value.filter(s => s.changePercent > 0).length
  const fallingStocks = stocks.value.filter(s => s.changePercent < 0).length
  const flatStocks = stocks.value.filter(s => s.changePercent === 0).length
  const totalVolume = stocks.value.reduce((sum, s) => sum + s.volume, 0)
  const totalTurnover = stocks.value.reduce((sum, s) => sum + s.turnover, 0)
  
  marketOverview.value = {
    totalStocks,
    risingStocks,
    fallingStocks,
    flatStocks,
    totalVolume,
    totalTurnover
  }
}

const searchStocks = () => {
  currentPage.value = 1
}

const refreshData = () => {
  loadTradingData()
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const toggleAutoRefresh = (enabled: boolean) => {
  if (enabled) {
    refreshInterval.value = setInterval(() => {
      loadTradingData()
    }, 10000) // 10秒刷新一次
    ElMessage.success('已开启自动刷新')
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  filters.value = {
    market: '',
    changeRange: '',
    priceRange: '',
    turnoverRange: '',
    turnoverRateRange: ''
  }
  currentPage.value = 1
}

const handleSelectionChange = (selection: Stock[]) => {
  selectedStocks.value = selection
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

const viewStockDetail = (stock: Stock) => {
  selectedStock.value = stock
  detailDialog.value = true
}

const addToWatchlist = () => {
  ElMessage.success(`已将${selectedStocks.value.length}只股票加入自选`)
  selectedStocks.value = []
}

const addSingleToWatchlist = (stock: Stock) => {
  ElMessage.success(`已将${stock.name}加入自选`)
}

const compareStocks = () => {
  ElMessage.info('股票对比分析功能开发中...')
}

const viewKLine = (stock: Stock) => {
  ElMessage.info(`跳转到${stock.name}的K线图页面`)
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

onMounted(() => {
  loadTradingData()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.realtime-trading {
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

.market-overview {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

.overview-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  height: 80px;
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

.overview-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.rising {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-icon.falling {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.overview-icon.flat {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.overview-icon.volume {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.overview-icon.turnover {
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 12px;
  color: #909399;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  height: 100%;
  padding-top: 30px;
}

.trading-table {
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

.stock-detail {
  padding: 20px 0;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
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