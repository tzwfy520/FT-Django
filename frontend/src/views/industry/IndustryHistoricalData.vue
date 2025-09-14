<template>
  <div class="industry-historical-data">
    <div class="page-header">
      <h2>行业历史数据</h2>
      <div class="header-actions">
        <el-select v-model="selectedIndustry" placeholder="选择行业" @change="loadHistoricalData">
          <el-option
            v-for="industry in industryList"
            :key="industry.code"
            :label="industry.name"
            :value="industry.code"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadHistoricalData"
        />
        <el-select v-model="period" placeholder="周期" @change="loadHistoricalData">
          <el-option label="日线" value="daily" />
          <el-option label="周线" value="weekly" />
          <el-option label="月线" value="monthly" />
          <el-option label="季线" value="quarterly" />
          <el-option label="年线" value="yearly" />
        </el-select>
        <el-button type="primary" @click="loadHistoricalData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          查询
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div class="industry-summary" v-if="currentIndustry">
      <el-card>
        <div class="summary-header">
          <div class="industry-info">
            <h3>{{ currentIndustry.name }}</h3>
            <span class="industry-code">{{ currentIndustry.code }}</span>
          </div>
          <div class="period-stats">
            <div class="stat-item">
              <span class="stat-label">期间涨跌幅</span>
              <span class="stat-value" :class="getChangeClass(periodStats.totalReturn)">
                {{ formatChange(periodStats.totalReturn) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最高价</span>
              <span class="stat-value high">{{ periodStats.highPrice.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最低价</span>
              <span class="stat-value low">{{ periodStats.lowPrice.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均成交额</span>
              <span class="stat-value">{{ formatAmount(periodStats.avgTurnover) }}亿</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">累计成交额</span>
              <span class="stat-value">{{ formatAmount(periodStats.totalTurnover) }}亿</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="chart-section">
      <el-row :gutter="20">
        <el-col :span="18">
          <el-card>
            <template #header>
              <div class="chart-header">
                <span>K线图</span>
                <div class="chart-controls">
                  <el-radio-group v-model="chartType" size="small" @change="updateChart">
                    <el-radio-button label="candlestick">K线</el-radio-button>
                    <el-radio-button label="line">分时</el-radio-button>
                    <el-radio-button label="area">面积</el-radio-button>
                  </el-radio-group>
                  <el-checkbox v-model="showMA" @change="updateChart">显示均线</el-checkbox>
                  <el-checkbox v-model="showVolume" @change="updateChart">显示成交量</el-checkbox>
                </div>
              </div>
            </template>
            <div ref="mainChartContainer" class="main-chart"></div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card title="技术指标">
            <div class="technical-indicators">
              <div class="indicator-group">
                <h5>趋势指标</h5>
                <div class="indicator-item">
                  <span class="indicator-name">MA5</span>
                  <span class="indicator-value">{{ technicalIndicators.ma5.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">MA10</span>
                  <span class="indicator-value">{{ technicalIndicators.ma10.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">MA20</span>
                  <span class="indicator-value">{{ technicalIndicators.ma20.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">MA60</span>
                  <span class="indicator-value">{{ technicalIndicators.ma60.toFixed(2) }}</span>
                </div>
              </div>
              
              <div class="indicator-group">
                <h5>震荡指标</h5>
                <div class="indicator-item">
                  <span class="indicator-name">RSI</span>
                  <span class="indicator-value" :class="getRSIClass(technicalIndicators.rsi)">
                    {{ technicalIndicators.rsi.toFixed(2) }}
                  </span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">KDJ-K</span>
                  <span class="indicator-value">{{ technicalIndicators.kdjK.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">KDJ-D</span>
                  <span class="indicator-value">{{ technicalIndicators.kdjD.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">KDJ-J</span>
                  <span class="indicator-value">{{ technicalIndicators.kdjJ.toFixed(2) }}</span>
                </div>
              </div>
              
              <div class="indicator-group">
                <h5>成交量指标</h5>
                <div class="indicator-item">
                  <span class="indicator-name">OBV</span>
                  <span class="indicator-value">{{ formatVolume(technicalIndicators.obv) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">MACD</span>
                  <span class="indicator-value" :class="getChangeClass(technicalIndicators.macd)">
                    {{ technicalIndicators.macd.toFixed(4) }}
                  </span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">DIF</span>
                  <span class="indicator-value">{{ technicalIndicators.dif.toFixed(4) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">DEA</span>
                  <span class="indicator-value">{{ technicalIndicators.dea.toFixed(4) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="analysis-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card title="收益率分析">
            <div ref="returnAnalysisChart" class="analysis-chart"></div>
            <div class="return-stats">
              <div class="return-item">
                <span class="return-label">日均收益率:</span>
                <span class="return-value" :class="getChangeClass(returnAnalysis.dailyAvg)">
                  {{ formatChange(returnAnalysis.dailyAvg) }}
                </span>
              </div>
              <div class="return-item">
                <span class="return-label">最大单日涨幅:</span>
                <span class="return-value positive">{{ formatChange(returnAnalysis.maxGain) }}</span>
              </div>
              <div class="return-item">
                <span class="return-label">最大单日跌幅:</span>
                <span class="return-value negative">{{ formatChange(returnAnalysis.maxLoss) }}</span>
              </div>
              <div class="return-item">
                <span class="return-label">波动率:</span>
                <span class="return-value">{{ returnAnalysis.volatility.toFixed(2) }}%</span>
              </div>
              <div class="return-item">
                <span class="return-label">夏普比率:</span>
                <span class="return-value">{{ returnAnalysis.sharpeRatio.toFixed(2) }}</span>
              </div>
              <div class="return-item">
                <span class="return-label">最大回撤:</span>
                <span class="return-value negative">{{ formatChange(returnAnalysis.maxDrawdown) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card title="成交量分析">
            <div ref="volumeAnalysisChart" class="analysis-chart"></div>
            <div class="volume-stats">
              <div class="volume-item">
                <span class="volume-label">平均成交量:</span>
                <span class="volume-value">{{ formatVolume(volumeAnalysis.avgVolume) }}</span>
              </div>
              <div class="volume-item">
                <span class="volume-label">最大成交量:</span>
                <span class="volume-value">{{ formatVolume(volumeAnalysis.maxVolume) }}</span>
              </div>
              <div class="volume-item">
                <span class="volume-label">最小成交量:</span>
                <span class="volume-value">{{ formatVolume(volumeAnalysis.minVolume) }}</span>
              </div>
              <div class="volume-item">
                <span class="volume-label">成交量标准差:</span>
                <span class="volume-value">{{ formatVolume(volumeAnalysis.volumeStd) }}</span>
              </div>
              <div class="volume-item">
                <span class="volume-label">量价相关性:</span>
                <span class="volume-value" :class="getCorrelationClass(volumeAnalysis.priceVolumeCorr)">
                  {{ volumeAnalysis.priceVolumeCorr.toFixed(3) }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="data-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>历史数据明细</span>
            <div class="table-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索日期"
                style="width: 200px;"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table
          :data="filteredTableData"
          stripe
          height="400"
          :default-sort="{ prop: 'date', order: 'descending' }"
        >
          <el-table-column prop="date" label="日期" width="120" sortable />
          <el-table-column prop="open" label="开盘" width="100">
            <template #default="{ row }">
              <span>{{ row.open.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="high" label="最高" width="100">
            <template #default="{ row }">
              <span class="high">{{ row.high.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="low" label="最低" width="100">
            <template #default="{ row }">
              <span class="low">{{ row.low.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="close" label="收盘" width="100">
            <template #default="{ row }">
              <span>{{ row.close.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="change" label="涨跌额" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.change)">{{ formatChange(row.change, false) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">{{ formatChange(row.changePercent) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="120">
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="120">
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}亿</span>
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="100">
            <template #default="{ row }">
              <span>{{ row.amplitude.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnoverRate" label="换手率" width="100">
            <template #default="{ row }">
              <span>{{ row.turnoverRate.toFixed(2) }}%</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="totalCount"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface HistoricalDataPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  change: number
  changePercent: number
  volume: number
  turnover: number
  amplitude: number
  turnoverRate: number
}

interface IndustryInfo {
  code: string
  name: string
}

const loading = ref(false)
const selectedIndustry = ref('BK0001')
const dateRange = ref<[string, string]>(['2024-01-01', '2024-12-31'])
const period = ref('daily')
const chartType = ref('candlestick')
const showMA = ref(true)
const showVolume = ref(true)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)

const mainChartContainer = ref<HTMLElement>()
const returnAnalysisChart = ref<HTMLElement>()
const volumeAnalysisChart = ref<HTMLElement>()
const mainChartInstance = ref<echarts.ECharts>()
const returnAnalysisChartInstance = ref<echarts.ECharts>()
const volumeAnalysisChartInstance = ref<echarts.ECharts>()

const industryList = ref<IndustryInfo[]>([
  { code: 'BK0001', name: '银行' },
  { code: 'BK0002', name: '证券' },
  { code: 'BK0003', name: '保险' },
  { code: 'BK0004', name: '房地产' },
  { code: 'BK0005', name: '建筑材料' },
  { code: 'BK0006', name: '钢铁' },
  { code: 'BK0007', name: '有色金属' },
  { code: 'BK0008', name: '煤炭' },
  { code: 'BK0009', name: '石油石化' },
  { code: 'BK0010', name: '电力' }
])

const currentIndustry = ref<IndustryInfo | null>(null)
const historicalData = ref<HistoricalDataPoint[]>([])

const periodStats = ref({
  totalReturn: 0,
  highPrice: 0,
  lowPrice: 0,
  avgTurnover: 0,
  totalTurnover: 0
})

const technicalIndicators = ref({
  ma5: 0,
  ma10: 0,
  ma20: 0,
  ma60: 0,
  rsi: 0,
  kdjK: 0,
  kdjD: 0,
  kdjJ: 0,
  obv: 0,
  macd: 0,
  dif: 0,
  dea: 0
})

const returnAnalysis = ref({
  dailyAvg: 0,
  maxGain: 0,
  maxLoss: 0,
  volatility: 0,
  sharpeRatio: 0,
  maxDrawdown: 0
})

const volumeAnalysis = ref({
  avgVolume: 0,
  maxVolume: 0,
  minVolume: 0,
  volumeStd: 0,
  priceVolumeCorr: 0
})

const filteredTableData = computed(() => {
  let filtered = [...historicalData.value]
  
  if (searchKeyword.value) {
    filtered = filtered.filter(item => item.date.includes(searchKeyword.value))
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  
  return filtered.slice(start, end)
})

const loadHistoricalData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const industryInfo = industryList.value.find(i => i.code === selectedIndustry.value)
    if (!industryInfo) return
    
    currentIndustry.value = industryInfo
    
    // 生成模拟历史数据
    const mockData: HistoricalDataPoint[] = []
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
    
    let basePrice = 100 + Math.random() * 50
    let prevClose = basePrice
    
    for (let i = 0; i <= daysDiff; i++) {
      const currentDate = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000)
      
      // 跳过周末
      if (currentDate.getDay() === 0 || currentDate.getDay() === 6) continue
      
      const volatility = 0.02 + Math.random() * 0.03
      const trend = Math.sin(i / 30) * 0.01
      const randomChange = (Math.random() - 0.5) * volatility + trend
      
      const open = prevClose * (1 + (Math.random() - 0.5) * 0.01)
      const close = open * (1 + randomChange)
      const high = Math.max(open, close) * (1 + Math.random() * 0.02)
      const low = Math.min(open, close) * (1 - Math.random() * 0.02)
      
      const change = close - prevClose
      const changePercent = (change / prevClose) * 100
      const amplitude = ((high - low) / prevClose) * 100
      
      const volume = Math.floor((Math.random() * 500000000 + 100000000) * (1 + Math.abs(changePercent) / 10))
      const turnover = (close * volume) / 100000000
      const turnoverRate = Math.random() * 5 + 1
      
      mockData.push({
        date: currentDate.toISOString().split('T')[0],
        open: Number(open.toFixed(2)),
        high: Number(high.toFixed(2)),
        low: Number(low.toFixed(2)),
        close: Number(close.toFixed(2)),
        change: Number(change.toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        volume,
        turnover: Number(turnover.toFixed(2)),
        amplitude: Number(amplitude.toFixed(2)),
        turnoverRate: Number(turnoverRate.toFixed(2))
      })
      
      prevClose = close
      basePrice = close
    }
    
    historicalData.value = mockData.reverse() // 最新日期在前
    totalCount.value = mockData.length
    
    // 计算期间统计
    if (mockData.length > 0) {
      const firstPrice = mockData[mockData.length - 1].close
      const lastPrice = mockData[0].close
      const allPrices = mockData.map(d => [d.high, d.low]).flat()
      
      periodStats.value = {
        totalReturn: ((lastPrice - firstPrice) / firstPrice) * 100,
        highPrice: Math.max(...allPrices),
        lowPrice: Math.min(...allPrices),
        avgTurnover: mockData.reduce((sum, d) => sum + d.turnover, 0) / mockData.length,
        totalTurnover: mockData.reduce((sum, d) => sum + d.turnover, 0)
      }
    }
    
    // 计算技术指标
    calculateTechnicalIndicators()
    
    // 计算收益率分析
    calculateReturnAnalysis()
    
    // 计算成交量分析
    calculateVolumeAnalysis()
    
    await nextTick()
    updateChart()
    renderReturnAnalysisChart()
    renderVolumeAnalysisChart()
    
    ElMessage.success('历史数据加载成功')
  } catch (error) {
    ElMessage.error('加载历史数据失败')
  } finally {
    loading.value = false
  }
}

const calculateTechnicalIndicators = () => {
  const data = historicalData.value
  if (data.length === 0) return
  
  const closes = data.map(d => d.close).reverse() // 按时间正序
  const volumes = data.map(d => d.volume).reverse()
  
  // 计算移动平均线
  technicalIndicators.value.ma5 = calculateMA(closes, 5)
  technicalIndicators.value.ma10 = calculateMA(closes, 10)
  technicalIndicators.value.ma20 = calculateMA(closes, 20)
  technicalIndicators.value.ma60 = calculateMA(closes, 60)
  
  // 计算RSI
  technicalIndicators.value.rsi = calculateRSI(closes, 14)
  
  // 计算KDJ
  const kdj = calculateKDJ(data.slice().reverse())
  technicalIndicators.value.kdjK = kdj.K
  technicalIndicators.value.kdjD = kdj.D
  technicalIndicators.value.kdjJ = kdj.J
  
  // 计算OBV
  technicalIndicators.value.obv = calculateOBV(closes, volumes)
  
  // 计算MACD
  const macd = calculateMACD(closes)
  technicalIndicators.value.macd = macd.MACD
  technicalIndicators.value.dif = macd.DIF
  technicalIndicators.value.dea = macd.DEA
}

const calculateMA = (prices: number[], period: number): number => {
  if (prices.length < period) return 0
  const sum = prices.slice(-period).reduce((a, b) => a + b, 0)
  return sum / period
}

const calculateRSI = (prices: number[], period: number): number => {
  if (prices.length < period + 1) return 50
  
  let gains = 0
  let losses = 0
  
  for (let i = prices.length - period; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1]
    if (change > 0) {
      gains += change
    } else {
      losses -= change
    }
  }
  
  const avgGain = gains / period
  const avgLoss = losses / period
  
  if (avgLoss === 0) return 100
  
  const rs = avgGain / avgLoss
  return 100 - (100 / (1 + rs))
}

const calculateKDJ = (data: HistoricalDataPoint[]): { K: number, D: number, J: number } => {
  if (data.length < 9) return { K: 50, D: 50, J: 50 }
  
  const period = 9
  const recent = data.slice(-period)
  
  const highestHigh = Math.max(...recent.map(d => d.high))
  const lowestLow = Math.min(...recent.map(d => d.low))
  const currentClose = recent[recent.length - 1].close
  
  const rsv = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100
  
  // 简化计算，实际应该使用前一日的K、D值
  const K = (rsv + 50) / 2 // 简化
  const D = (K + 50) / 2 // 简化
  const J = 3 * K - 2 * D
  
  return { K, D, J }
}

const calculateOBV = (prices: number[], volumes: number[]): number => {
  if (prices.length < 2) return 0
  
  let obv = 0
  for (let i = 1; i < prices.length; i++) {
    if (prices[i] > prices[i - 1]) {
      obv += volumes[i]
    } else if (prices[i] < prices[i - 1]) {
      obv -= volumes[i]
    }
  }
  
  return obv
}

const calculateMACD = (prices: number[]): { MACD: number, DIF: number, DEA: number } => {
  if (prices.length < 26) return { MACD: 0, DIF: 0, DEA: 0 }
  
  const ema12 = calculateEMA(prices, 12)
  const ema26 = calculateEMA(prices, 26)
  const dif = ema12 - ema26
  
  // 简化DEA计算
  const dea = dif * 0.8 // 简化
  const macd = 2 * (dif - dea)
  
  return { MACD: macd, DIF: dif, DEA: dea }
}

const calculateEMA = (prices: number[], period: number): number => {
  if (prices.length < period) return 0
  
  const multiplier = 2 / (period + 1)
  let ema = prices.slice(-period).reduce((a, b) => a + b, 0) / period
  
  for (let i = prices.length - period + 1; i < prices.length; i++) {
    ema = (prices[i] - ema) * multiplier + ema
  }
  
  return ema
}

const calculateReturnAnalysis = () => {
  const data = historicalData.value
  if (data.length < 2) return
  
  const returns = data.slice(1).map((d, i) => d.changePercent)
  
  returnAnalysis.value = {
    dailyAvg: returns.reduce((a, b) => a + b, 0) / returns.length,
    maxGain: Math.max(...returns),
    maxLoss: Math.min(...returns),
    volatility: calculateStandardDeviation(returns),
    sharpeRatio: calculateSharpeRatio(returns),
    maxDrawdown: calculateMaxDrawdown(data)
  }
}

const calculateVolumeAnalysis = () => {
  const data = historicalData.value
  if (data.length === 0) return
  
  const volumes = data.map(d => d.volume)
  const prices = data.map(d => d.close)
  
  volumeAnalysis.value = {
    avgVolume: volumes.reduce((a, b) => a + b, 0) / volumes.length,
    maxVolume: Math.max(...volumes),
    minVolume: Math.min(...volumes),
    volumeStd: calculateStandardDeviation(volumes),
    priceVolumeCorr: calculateCorrelation(prices, volumes)
  }
}

const calculateStandardDeviation = (values: number[]): number => {
  const mean = values.reduce((a, b) => a + b, 0) / values.length
  const squaredDiffs = values.map(value => Math.pow(value - mean, 2))
  const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / squaredDiffs.length
  return Math.sqrt(avgSquaredDiff)
}

const calculateSharpeRatio = (returns: number[]): number => {
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
  const volatility = calculateStandardDeviation(returns)
  const riskFreeRate = 0.03 // 假设无风险利率3%
  return volatility === 0 ? 0 : (avgReturn - riskFreeRate) / volatility
}

const calculateMaxDrawdown = (data: HistoricalDataPoint[]): number => {
  let maxDrawdown = 0
  let peak = data[data.length - 1].close
  
  for (let i = data.length - 2; i >= 0; i--) {
    const current = data[i].close
    if (current > peak) {
      peak = current
    } else {
      const drawdown = ((peak - current) / peak) * 100
      maxDrawdown = Math.max(maxDrawdown, drawdown)
    }
  }
  
  return -maxDrawdown
}

const calculateCorrelation = (x: number[], y: number[]): number => {
  if (x.length !== y.length || x.length === 0) return 0
  
  const n = x.length
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = y.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0)
  
  const numerator = n * sumXY - sumX * sumY
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))
  
  return denominator === 0 ? 0 : numerator / denominator
}

const updateChart = () => {
  if (!mainChartContainer.value || !historicalData.value.length) return
  
  if (!mainChartInstance.value) {
    mainChartInstance.value = echarts.init(mainChartContainer.value)
  }
  
  const data = historicalData.value.slice().reverse() // 按时间正序显示
  const dates = data.map(d => d.date)
  
  const series: any[] = []
  
  if (chartType.value === 'candlestick') {
    series.push({
      type: 'candlestick',
      data: data.map(d => [d.open, d.close, d.low, d.high]),
      itemStyle: {
        color: '#f56c6c',
        color0: '#67c23a',
        borderColor: '#f56c6c',
        borderColor0: '#67c23a'
      }
    })
  } else if (chartType.value === 'line') {
    series.push({
      type: 'line',
      data: data.map(d => d.close),
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#409eff'
      }
    })
  } else if (chartType.value === 'area') {
    series.push({
      type: 'line',
      data: data.map(d => d.close),
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#409eff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(64, 158, 255, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(64, 158, 255, 0.1)'
          }]
        }
      }
    })
  }
  
  // 添加均线
  if (showMA.value) {
    const ma5Data = calculateMAArray(data.map(d => d.close), 5)
    const ma10Data = calculateMAArray(data.map(d => d.close), 10)
    const ma20Data = calculateMAArray(data.map(d => d.close), 20)
    
    series.push(
      {
        name: 'MA5',
        type: 'line',
        data: ma5Data,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1, color: '#ff6b6b' }
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10Data,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1, color: '#4ecdc4' }
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20Data,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1, color: '#45b7d1' }
      }
    )
  }
  
  const option: any = {
    title: {
      text: `${currentIndustry.value?.name} - ${period.value === 'daily' ? '日线' : period.value === 'weekly' ? '周线' : '月线'}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: showMA.value ? ['MA5', 'MA10', 'MA20'] : [],
      top: 30
    },
    grid: [
      {
        left: '3%',
        right: '4%',
        height: showVolume.value ? '60%' : '80%',
        top: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: chartType.value === 'candlestick',
        axisLine: { onZero: false },
        splitLine: { show: false },
        splitNumber: 20,
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      }
    ],
    series
  }
  
  // 添加成交量
  if (showVolume.value) {
    option.grid.push({
      left: '3%',
      right: '4%',
      height: '20%',
      top: '80%'
    })
    
    option.xAxis.push({
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { onZero: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      min: 'dataMin',
      max: 'dataMax'
    })
    
    option.yAxis.push({
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false }
    })
    
    option.series.push({
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: data.map((d, i) => ({
        value: d.volume,
        itemStyle: {
          color: i > 0 && d.close >= data[i - 1].close ? '#f56c6c' : '#67c23a'
        }
      }))
    })
  }
  
  mainChartInstance.value.setOption(option, true)
}

const calculateMAArray = (prices: number[], period: number): (number | null)[] => {
  const result: (number | null)[] = []
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else {
      const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0)
      result.push(sum / period)
    }
  }
  
  return result
}

const renderReturnAnalysisChart = () => {
  if (!returnAnalysisChart.value || !historicalData.value.length) return
  
  if (!returnAnalysisChartInstance.value) {
    returnAnalysisChartInstance.value = echarts.init(returnAnalysisChart.value)
  }
  
  const returns = historicalData.value.slice(1).map(d => d.changePercent).reverse()
  const dates = historicalData.value.slice(1).map(d => d.date).reverse()
  
  const option = {
    title: {
      text: '日收益率分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: Math.floor(dates.length / 10)
      }
    },
    yAxis: {
      type: 'value',
      name: '收益率(%)',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      type: 'bar',
      data: returns.map(r => ({
        value: r,
        itemStyle: {
          color: r >= 0 ? '#f56c6c' : '#67c23a'
        }
      })),
      barWidth: '60%'
    }]
  }
  
  returnAnalysisChartInstance.value.setOption(option)
}

const renderVolumeAnalysisChart = () => {
  if (!volumeAnalysisChart.value || !historicalData.value.length) return
  
  if (!volumeAnalysisChartInstance.value) {
    volumeAnalysisChartInstance.value = echarts.init(volumeAnalysisChart.value)
  }
  
  const volumes = historicalData.value.map(d => d.volume / 100000000).reverse() // 转换为亿
  const dates = historicalData.value.map(d => d.date).reverse()
  
  const option = {
    title: {
      text: '成交量趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        return `日期: ${data.name}<br/>成交量: ${data.value.toFixed(2)}亿`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: Math.floor(dates.length / 10)
      }
    },
    yAxis: {
      type: 'value',
      name: '成交量(亿)',
      axisLabel: {
        formatter: '{value}亿'
      }
    },
    series: [{
      type: 'line',
      data: volumes,
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: '#e6a23c'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(230, 162, 60, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(230, 162, 60, 0.1)'
          }]
        }
      }
    }]
  }
  
  volumeAnalysisChartInstance.value.setOption(option)
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
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

const formatChange = (change: number, isPercent = true): string => {
  const sign = change >= 0 ? '+' : ''
  return sign + change.toFixed(2) + (isPercent ? '%' : '')
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getRSIClass = (rsi: number): string => {
  if (rsi > 70) return 'negative' // 超买
  if (rsi < 30) return 'positive' // 超卖
  return 'neutral'
}

const getCorrelationClass = (corr: number): string => {
  if (Math.abs(corr) > 0.7) return 'positive'
  if (Math.abs(corr) > 0.3) return 'neutral'
  return 'negative'
}

onMounted(() => {
  loadHistoricalData()
})

onUnmounted(() => {
  if (mainChartInstance.value) {
    mainChartInstance.value.dispose()
  }
  if (returnAnalysisChartInstance.value) {
    returnAnalysisChartInstance.value.dispose()
  }
  if (volumeAnalysisChartInstance.value) {
    volumeAnalysisChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.industry-historical-data {
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

.industry-summary {
  margin-bottom: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.industry-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.industry-info h3 {
  margin: 0;
  color: #303133;
}

.industry-code {
  color: #909399;
  font-size: 14px;
}

.period-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.stat-value.high {
  color: #f56c6c;
}

.stat-value.low {
  color: #67c23a;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.main-chart {
  height: 500px;
}

.technical-indicators {
  padding: 10px 0;
}

.indicator-group {
  margin-bottom: 20px;
}

.indicator-group h5 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 5px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  margin-bottom: 5px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.indicator-name {
  font-size: 12px;
  color: #606266;
}

.indicator-value {
  font-size: 12px;
  font-weight: bold;
  color: #303133;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-chart {
  height: 200px;
  margin-bottom: 15px;
}

.return-stats,
.volume-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.return-item,
.volume-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
}

.return-label,
.volume-label {
  color: #606266;
}

.return-value,
.volume-value {
  font-weight: bold;
  color: #303133;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-controls {
  display: flex;
  gap: 10px;
}

.pagination-container {
  text-align: right;
  margin-top: 15px;
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

.high {
  color: #f56c6c;
}

.low {
  color: #67c23a;
}
</style>