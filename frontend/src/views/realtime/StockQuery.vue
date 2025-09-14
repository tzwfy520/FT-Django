<template>
  <div class="stock-query">
    <div class="page-header">
      <h2>自助查询</h2>
      <div class="header-actions">
        <div class="market-status">
          <el-tag :type="marketStatus.type" size="large">
            <el-icon><Clock /></el-icon>
            {{ marketStatus.text }}
          </el-tag>
        </div>
        <el-button @click="clearAll">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 股票搜索 -->
    <div class="search-section">
      <el-card>
        <template #header>
          <span>股票查询</span>
        </template>
        
        <el-row :gutter="20" align="middle">
          <el-col :span="8">
            <el-input
              v-model="searchCode"
              placeholder="输入股票代码或名称"
              size="large"
              @keyup.enter="searchStock"
              @input="handleSearchInput"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button @click="searchStock" :loading="searching">
                  查询
                </el-button>
              </template>
            </el-input>
            
            <!-- 搜索建议 -->
            <div v-if="searchSuggestions.length > 0" class="search-suggestions">
              <div 
                v-for="suggestion in searchSuggestions" 
                :key="suggestion.code"
                class="suggestion-item"
                @click="selectSuggestion(suggestion)"
              >
                <span class="suggestion-code">{{ suggestion.code }}</span>
                <span class="suggestion-name">{{ suggestion.name }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <el-select v-model="queryType" placeholder="查询类型">
              <el-option label="实时行情" value="realtime" />
              <el-option label="分时数据" value="intraday" />
              <el-option label="五档行情" value="level2" />
              <el-option label="资金流向" value="moneyflow" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="addToComparison" :disabled="!currentStock">
              <el-icon><Plus /></el-icon>
              加入对比
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button @click="addToWatchlist" :disabled="!currentStock">
              <el-icon><Star /></el-icon>
              加入自选
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 当前查询股票 -->
    <div v-if="currentStock" class="current-stock">
      <el-card>
        <template #header>
          <div class="stock-header">
            <div class="stock-title">
              <span class="stock-name">{{ currentStock.name }}</span>
              <span class="stock-code">({{ currentStock.code }})</span>
              <el-tag v-if="currentStock.isLimitUp" type="danger" size="small">涨停</el-tag>
              <el-tag v-else-if="currentStock.isLimitDown" type="success" size="small">跌停</el-tag>
            </div>
            <div class="stock-actions">
              <span class="update-time">更新时间: {{ currentStock.updateTime }}</span>
              <span v-if="autoRefresh" class="countdown">({{ countdown }}s)</span>
            </div>
          </div>
        </template>
        
        <!-- 基本信息 -->
        <el-row :gutter="20" class="stock-info">
          <el-col :span="4">
            <div class="info-item main-price">
              <div class="info-label">现价</div>
              <div class="info-value" :class="getPriceClass(currentStock.changePercent)">
                {{ currentStock.currentPrice.toFixed(2) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌幅</div>
              <div class="info-value" :class="getChangeClass(currentStock.changePercent)">
                {{ formatChange(currentStock.changePercent) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌额</div>
              <div class="info-value" :class="getChangeClass(currentStock.changeAmount)">
                {{ formatChangeAmount(currentStock.changeAmount) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交量</div>
              <div class="info-value">{{ formatVolume(currentStock.volume) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交额</div>
              <div class="info-value">{{ formatAmount(currentStock.turnover) }}万</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">换手率</div>
              <div class="info-value">{{ currentStock.turnoverRate.toFixed(2) }}%</div>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" class="stock-info">
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">开盘价</div>
              <div class="info-value">{{ currentStock.openPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">最高价</div>
              <div class="info-value positive">{{ currentStock.highPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">最低价</div>
              <div class="info-value negative">{{ currentStock.lowPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">昨收价</div>
              <div class="info-value">{{ currentStock.prevClose.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">市盈率</div>
              <div class="info-value">{{ currentStock.pe > 0 ? currentStock.pe.toFixed(2) : '-' }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">市净率</div>
              <div class="info-value">{{ currentStock.pb.toFixed(2) }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 详细数据展示 -->
    <div v-if="currentStock" class="detail-section">
      <el-row :gutter="20">
        <!-- 分时图 -->
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="chart-header">
                <span>{{ queryType === 'realtime' ? '分时走势' : getChartTitle() }}</span>
                <div class="chart-actions">
                  <el-radio-group v-model="chartPeriod" @change="updateChart">
                    <el-radio-button label="1min">1分</el-radio-button>
                    <el-radio-button label="5min">5分</el-radio-button>
                    <el-radio-button label="15min">15分</el-radio-button>
                    <el-radio-button label="30min">30分</el-radio-button>
                    <el-radio-button label="60min">60分</el-radio-button>
                  </el-radio-group>
                  <el-button size="small" @click="fullScreen">
                    <el-icon><FullScreen /></el-icon>
                    全屏
                  </el-button>
                </div>
              </div>
            </template>
            
            <div ref="chartContainer" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <!-- 五档行情/资金流向 -->
        <el-col :span="8">
          <el-card v-if="queryType === 'level2'">
            <template #header>
              <span>五档行情</span>
            </template>
            
            <div class="level2-data">
              <div class="level2-section">
                <div class="level2-title">卖盘</div>
                <div v-for="(item, index) in level2Data.sell" :key="'sell' + index" class="level2-item sell">
                  <span class="level2-label">卖{{ 5 - index }}</span>
                  <span class="level2-price">{{ item.price.toFixed(2) }}</span>
                  <span class="level2-volume">{{ item.volume }}</span>
                </div>
              </div>
              
              <div class="level2-current">
                <div class="current-price" :class="getPriceClass(currentStock.changePercent)">
                  {{ currentStock.currentPrice.toFixed(2) }}
                </div>
                <div class="current-change" :class="getChangeClass(currentStock.changePercent)">
                  {{ formatChange(currentStock.changePercent) }}
                </div>
              </div>
              
              <div class="level2-section">
                <div class="level2-title">买盘</div>
                <div v-for="(item, index) in level2Data.buy" :key="'buy' + index" class="level2-item buy">
                  <span class="level2-label">买{{ index + 1 }}</span>
                  <span class="level2-price">{{ item.price.toFixed(2) }}</span>
                  <span class="level2-volume">{{ item.volume }}</span>
                </div>
              </div>
            </div>
          </el-card>
          
          <el-card v-else-if="queryType === 'moneyflow'">
            <template #header>
              <span>资金流向</span>
            </template>
            
            <div class="moneyflow-data">
              <div class="flow-item">
                <div class="flow-label">主力净流入</div>
                <div class="flow-value" :class="getChangeClass(moneyFlow.mainNet)">
                  {{ formatAmount(Math.abs(moneyFlow.mainNet)) }}万
                </div>
              </div>
              <div class="flow-item">
                <div class="flow-label">超大单净流入</div>
                <div class="flow-value" :class="getChangeClass(moneyFlow.superLargeNet)">
                  {{ formatAmount(Math.abs(moneyFlow.superLargeNet)) }}万
                </div>
              </div>
              <div class="flow-item">
                <div class="flow-label">大单净流入</div>
                <div class="flow-value" :class="getChangeClass(moneyFlow.largeNet)">
                  {{ formatAmount(Math.abs(moneyFlow.largeNet)) }}万
                </div>
              </div>
              <div class="flow-item">
                <div class="flow-label">中单净流入</div>
                <div class="flow-value" :class="getChangeClass(moneyFlow.mediumNet)">
                  {{ formatAmount(Math.abs(moneyFlow.mediumNet)) }}万
                </div>
              </div>
              <div class="flow-item">
                <div class="flow-label">小单净流入</div>
                <div class="flow-value" :class="getChangeClass(moneyFlow.smallNet)">
                  {{ formatAmount(Math.abs(moneyFlow.smallNet)) }}万
                </div>
              </div>
            </div>
          </el-card>
          
          <el-card v-else>
            <template #header>
              <span>实时指标</span>
            </template>
            
            <div class="indicators">
              <div class="indicator-item">
                <div class="indicator-label">振幅</div>
                <div class="indicator-value">{{ currentStock.amplitude.toFixed(2) }}%</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">量比</div>
                <div class="indicator-value">{{ currentStock.volumeRatio.toFixed(2) }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">委比</div>
                <div class="indicator-value" :class="getChangeClass(currentStock.bidRatio)">
                  {{ currentStock.bidRatio.toFixed(2) }}%
                </div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">委差</div>
                <div class="indicator-value">{{ currentStock.bidDiff }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 对比列表 -->
    <div v-if="comparisonStocks.length > 0" class="comparison-section">
      <el-card>
        <template #header>
          <div class="comparison-header">
            <span>股票对比 ({{ comparisonStocks.length }})</span>
            <el-button size="small" @click="clearComparison">
              清空对比
            </el-button>
          </div>
        </template>
        
        <el-table :data="comparisonStocks" stripe>
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="currentPrice" label="现价" width="100">
            <template #default="{ row }">
              <span :class="getPriceClass(row.changePercent)">
                {{ row.currentPrice.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changeAmount" label="涨跌额" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changeAmount)">
                {{ formatChangeAmount(row.changeAmount) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120">
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="120">
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}万</span>
            </template>
          </el-table-column>
          <el-table-column prop="pe" label="市盈率" width="100">
            <template #default="{ row }">
              <span>{{ row.pe > 0 ? row.pe.toFixed(2) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row, $index }">
              <el-button size="small" type="danger" @click="removeFromComparison($index)">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 查询历史 -->
    <div v-if="queryHistory.length > 0" class="history-section">
      <el-card>
        <template #header>
          <div class="history-header">
            <span>查询历史</span>
            <el-button size="small" @click="clearHistory">
              清空历史
            </el-button>
          </div>
        </template>
        
        <div class="history-list">
          <el-tag
            v-for="(item, index) in queryHistory"
            :key="index"
            class="history-item"
            closable
            @click="quickSearch(item)"
            @close="removeFromHistory(index)"
          >
            {{ item.code }} {{ item.name }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Clock, Delete, Download, Search, Plus, Star, FullScreen 
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
  amplitude: number
  volumeRatio: number
  bidRatio: number
  bidDiff: number
  isLimitUp: boolean
  isLimitDown: boolean
  updateTime: string
}

interface SearchSuggestion {
  code: string
  name: string
}

interface Level2Item {
  price: number
  volume: number
}

interface Level2Data {
  buy: Level2Item[]
  sell: Level2Item[]
}

interface MoneyFlow {
  mainNet: number
  superLargeNet: number
  largeNet: number
  mediumNet: number
  smallNet: number
}

interface MarketStatus {
  type: 'success' | 'warning' | 'danger'
  text: string
}

const searching = ref(false)
const autoRefresh = ref(false)
const countdown = ref(30)
const searchCode = ref('')
const queryType = ref('realtime')
const chartPeriod = ref('1min')
const currentStock = ref<Stock | null>(null)
const searchSuggestions = ref<SearchSuggestion[]>([])
const comparisonStocks = ref<Stock[]>([])
const queryHistory = ref<SearchSuggestion[]>([])
const chartContainer = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const marketStatus = ref<MarketStatus>({
  type: 'success',
  text: '交易中 09:30-15:00'
})

const level2Data = ref<Level2Data>({
  buy: [],
  sell: []
})

const moneyFlow = ref<MoneyFlow>({
  mainNet: 0,
  superLargeNet: 0,
  largeNet: 0,
  mediumNet: 0,
  smallNet: 0
})

let refreshTimer: NodeJS.Timeout | null = null
let countdownTimer: NodeJS.Timeout | null = null

const getChartTitle = () => {
  const titles = {
    realtime: '分时走势',
    intraday: '分时数据',
    level2: '五档行情',
    moneyflow: '资金流向'
  }
  return titles[queryType.value] || '分时走势'
}

const handleSearchInput = () => {
  if (searchCode.value.length >= 2) {
    // 模拟搜索建议
    const suggestions = [
      { code: '000001', name: '平安银行' },
      { code: '000002', name: '万科A' },
      { code: '000858', name: '五粮液' },
      { code: '600036', name: '招商银行' },
      { code: '600519', name: '贵州茅台' }
    ].filter(item => 
      item.code.includes(searchCode.value) || 
      item.name.includes(searchCode.value)
    )
    
    searchSuggestions.value = suggestions.slice(0, 5)
  } else {
    searchSuggestions.value = []
  }
}

const selectSuggestion = (suggestion: SearchSuggestion) => {
  searchCode.value = suggestion.code
  searchSuggestions.value = []
  searchStock()
}

const searchStock = async () => {
  if (!searchCode.value.trim()) {
    ElMessage.error('请输入股票代码或名称')
    return
  }
  
  searching.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 生成模拟股票数据
    const basePrice = Math.random() * 100 + 10
    const changePercent = (Math.random() - 0.5) * 10
    const changeAmount = (basePrice * changePercent) / 100
    const currentPrice = basePrice + changeAmount
    
    const stockNames = ['平安银行', '万科A', '五粮液', '招商银行', '贵州茅台']
    const stockName = stockNames[Math.floor(Math.random() * stockNames.length)]
    
    currentStock.value = {
      code: searchCode.value.toUpperCase(),
      name: stockName,
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
      amplitude: Math.random() * 10,
      volumeRatio: Math.random() * 3 + 0.5,
      bidRatio: (Math.random() - 0.5) * 20,
      bidDiff: Math.floor((Math.random() - 0.5) * 10000),
      isLimitUp: Math.random() < 0.05,
      isLimitDown: Math.random() < 0.05,
      updateTime: new Date().toLocaleTimeString()
    }
    
    // 生成五档行情数据
    generateLevel2Data()
    
    // 生成资金流向数据
    generateMoneyFlowData()
    
    // 添加到查询历史
    const historyItem = { code: currentStock.value.code, name: currentStock.value.name }
    const existingIndex = queryHistory.value.findIndex(item => item.code === historyItem.code)
    if (existingIndex >= 0) {
      queryHistory.value.splice(existingIndex, 1)
    }
    queryHistory.value.unshift(historyItem)
    if (queryHistory.value.length > 10) {
      queryHistory.value = queryHistory.value.slice(0, 10)
    }
    
    // 初始化图表
    await nextTick()
    initChart()
    
    searchSuggestions.value = []
    ElMessage.success('查询成功')
    
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    searching.value = false
  }
}

const generateLevel2Data = () => {
  if (!currentStock.value) return
  
  const basePrice = currentStock.value.currentPrice
  const buy: Level2Item[] = []
  const sell: Level2Item[] = []
  
  // 生成买盘数据
  for (let i = 0; i < 5; i++) {
    buy.push({
      price: basePrice - (i + 1) * 0.01,
      volume: Math.floor(Math.random() * 10000 + 100)
    })
  }
  
  // 生成卖盘数据
  for (let i = 0; i < 5; i++) {
    sell.push({
      price: basePrice + (i + 1) * 0.01,
      volume: Math.floor(Math.random() * 10000 + 100)
    })
  }
  
  level2Data.value = { buy, sell }
}

const generateMoneyFlowData = () => {
  moneyFlow.value = {
    mainNet: (Math.random() - 0.5) * 100000,
    superLargeNet: (Math.random() - 0.5) * 50000,
    largeNet: (Math.random() - 0.5) * 30000,
    mediumNet: (Math.random() - 0.5) * 20000,
    smallNet: (Math.random() - 0.5) * 10000
  }
}

const initChart = () => {
  if (!chartContainer.value || !currentStock.value) return
  
  chart.value = echarts.init(chartContainer.value)
  updateChart()
}

const updateChart = () => {
  if (!chart.value || !currentStock.value) return
  
  // 生成模拟分时数据
  const timeData = []
  const priceData = []
  const volumeData = []
  let basePrice = currentStock.value.prevClose
  
  const periods = {
    '1min': 240,
    '5min': 48,
    '15min': 16,
    '30min': 8,
    '60min': 4
  }
  
  const periodCount = periods[chartPeriod.value] || 240
  
  for (let i = 0; i < periodCount; i++) {
    const time = new Date()
    time.setHours(9, 30 + i * (parseInt(chartPeriod.value) || 1), 0, 0)
    timeData.push(time.toTimeString().slice(0, 5))
    
    basePrice += (Math.random() - 0.5) * 0.5
    priceData.push(basePrice)
    volumeData.push(Math.floor(Math.random() * 1000000 + 100000))
  }
  
  const option = {
    title: {
      text: `${currentStock.value.name} ${getChartTitle()}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['价格', '成交量'],
      top: 30
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '60%'
      },
      {
        left: '10%',
        right: '8%',
        top: '75%',
        height: '16%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: timeData,
        scale: true,
        boundaryGap: false
      },
      {
        type: 'category',
        gridIndex: 1,
        data: timeData,
        scale: true,
        boundaryGap: false,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 80,
        end: 100
      }
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        data: priceData,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: currentStock.value.changePercent >= 0 ? '#f56c6c' : '#67c23a'
        },
        areaStyle: {
          opacity: 0.3,
          color: currentStock.value.changePercent >= 0 ? '#f56c6c' : '#67c23a'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumeData,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  chart.value.setOption(option, true)
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
    if (currentStock.value) {
      refreshCurrentStock()
    }
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

const refreshCurrentStock = () => {
  if (!currentStock.value) return
  
  // 更新股票数据
  const changePercent = (Math.random() - 0.5) * 2
  const changeAmount = (currentStock.value.prevClose * changePercent) / 100
  currentStock.value.currentPrice = currentStock.value.prevClose + changeAmount
  currentStock.value.changePercent += changePercent
  currentStock.value.changeAmount += changeAmount
  currentStock.value.volume += Math.floor(Math.random() * 1000000)
  currentStock.value.updateTime = new Date().toLocaleTimeString()
  
  // 更新图表
  updateChart()
  
  // 更新五档行情
  generateLevel2Data()
  
  // 更新资金流向
  generateMoneyFlowData()
}

const addToComparison = () => {
  if (!currentStock.value) return
  
  if (comparisonStocks.value.some(s => s.code === currentStock.value!.code)) {
    ElMessage.warning('该股票已在对比列表中')
    return
  }
  
  if (comparisonStocks.value.length >= 10) {
    ElMessage.warning('对比列表最多支持10只股票')
    return
  }
  
  comparisonStocks.value.push({ ...currentStock.value })
  ElMessage.success('已加入对比列表')
}

const removeFromComparison = (index: number) => {
  comparisonStocks.value.splice(index, 1)
  ElMessage.success('已从对比列表移除')
}

const clearComparison = () => {
  comparisonStocks.value = []
  ElMessage.success('已清空对比列表')
}

const addToWatchlist = () => {
  if (!currentStock.value) return
  
  ElMessage.success(`已将${currentStock.value.name}加入自选`)
}

const quickSearch = (item: SearchSuggestion) => {
  searchCode.value = item.code
  searchStock()
}

const removeFromHistory = (index: number) => {
  queryHistory.value.splice(index, 1)
}

const clearHistory = () => {
  queryHistory.value = []
  ElMessage.success('已清空查询历史')
}

const clearAll = () => {
  currentStock.value = null
  comparisonStocks.value = []
  searchCode.value = ''
  searchSuggestions.value = []
  stopAutoRefresh()
  autoRefresh.value = false
  ElMessage.success('已清空所有数据')
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const fullScreen = () => {
  ElMessage.info('全屏功能开发中...')
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
  
  // 每分钟检查市场状态
  setInterval(checkMarketStatus, 60000)
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.stock-query {
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

.search-section {
  margin-bottom: 20px;
  position: relative;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

.suggestion-code {
  font-weight: bold;
  color: #409eff;
}

.suggestion-name {
  color: #606266;
}

.current-stock {
  margin-bottom: 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.stock-code {
  font-size: 14px;
  color: #909399;
}

.stock-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.countdown {
  color: #409eff;
  font-weight: bold;
}

.stock-info {
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item.main-price {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.info-item.main-price .info-value {
  color: white !important;
  font-size: 24px;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.info-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.detail-section {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.chart-container {
  height: 500px;
  width: 100%;
}

.level2-data {
  padding: 10px 0;
}

.level2-section {
  margin-bottom: 15px;
}

.level2-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
  text-align: center;
}

.level2-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  font-size: 12px;
}

.level2-item.sell {
  color: #67c23a;
}

.level2-item.buy {
  color: #f56c6c;
}

.level2-label {
  width: 30px;
}

.level2-price {
  font-weight: bold;
  flex: 1;
  text-align: center;
}

.level2-volume {
  width: 50px;
  text-align: right;
}

.level2-current {
  text-align: center;
  padding: 15px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin: 15px 0;
}

.current-price {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.current-change {
  font-size: 14px;
}

.moneyflow-data {
  padding: 10px 0;
}

.flow-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.flow-item:last-child {
  border-bottom: none;
}

.flow-label {
  font-size: 14px;
  color: #606266;
}

.flow-value {
  font-size: 14px;
  font-weight: bold;
}

.indicators {
  padding: 10px 0;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.indicator-item:last-child {
  border-bottom: none;
}

.indicator-label {
  font-size: 14px;
  color: #606266;
}

.indicator-value {
  font-size: 14px;
  font-weight: bold;
}

.comparison-section {
  margin-bottom: 20px;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-section {
  margin-bottom: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  padding: 10px 0;
}

.history-item {
  margin: 5px 5px 5px 0;
  cursor: pointer;
}

.history-item:hover {
  opacity: 0.8;
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

.price-up {
  color: #f56c6c;
}

.price-down {
  color: #67c23a;
}

.price-flat {
  color: #909399;
}
</style>