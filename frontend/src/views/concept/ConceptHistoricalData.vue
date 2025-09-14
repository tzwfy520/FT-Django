<template>
  <div class="concept-historical-data">
    <div class="page-header">
      <h2>概念历史数据</h2>
      <div class="header-actions">
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
        <el-select v-model="selectedConcept" placeholder="选择概念" @change="loadHistoricalData">
          <el-option
            v-for="concept in conceptList"
            :key="concept.code"
            :label="concept.name"
            :value="concept.code"
          />
        </el-select>
        <el-button type="primary" @click="queryData" :loading="loading">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div v-if="selectedConcept" class="concept-summary">
      <el-card>
        <div class="summary-header">
          <div class="concept-info">
            <h3>{{ conceptInfo.name }}</h3>
            <span class="concept-code">{{ conceptInfo.code }}</span>
          </div>
          <div class="period-info">
            <span class="period-label">统计周期:</span>
            <span class="period-value">{{ formatDateRange() }}</span>
          </div>
        </div>
        
        <el-row :gutter="20" class="summary-metrics">
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon period">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ historicalSummary.tradingDays }}</div>
                <div class="metric-label">交易日数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon return">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value" :class="getChangeClass(historicalSummary.totalReturn)">
                  {{ formatChange(historicalSummary.totalReturn) }}
                </div>
                <div class="metric-label">累计收益率</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon volatility">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ historicalSummary.volatility.toFixed(2) }}%</div>
                <div class="metric-label">波动率</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon max">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ historicalSummary.maxPrice.toFixed(2) }}</div>
                <div class="metric-label">最高价</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon min">
                <el-icon><CaretBottom /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ historicalSummary.minPrice.toFixed(2) }}</div>
                <div class="metric-label">最低价</div>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="metric-card">
              <div class="metric-icon turnover">
                <el-icon><Money /></el-icon>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ formatAmount(historicalSummary.avgTurnover) }}</div>
                <div class="metric-label">日均成交额(亿)</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <div v-if="selectedConcept" class="chart-section">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="chart-header">
                <span>K线图</span>
                <div class="chart-controls">
                  <el-radio-group v-model="chartType" @change="updateChart">
                    <el-radio-button label="candlestick">K线</el-radio-button>
                    <el-radio-button label="line">分时</el-radio-button>
                  </el-radio-group>
                  <el-select v-model="period" @change="updateChart" style="width: 100px; margin-left: 10px;">
                    <el-option label="日K" value="1d" />
                    <el-option label="周K" value="1w" />
                    <el-option label="月K" value="1M" />
                  </el-select>
                </div>
              </div>
            </template>
            <div ref="klineChart" class="kline-chart"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card title="技术指标">
            <div class="technical-indicators">
              <div class="indicator-group">
                <h4>移动平均线</h4>
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
                <h4>技术指标</h4>
                <div class="indicator-item">
                  <span class="indicator-name">RSI</span>
                  <span class="indicator-value">{{ technicalIndicators.rsi.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">MACD</span>
                  <span class="indicator-value" :class="getChangeClass(technicalIndicators.macd)">
                    {{ technicalIndicators.macd.toFixed(4) }}
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
                  <span class="indicator-name">BOLL上轨</span>
                  <span class="indicator-value">{{ technicalIndicators.bollUpper.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-name">BOLL下轨</span>
                  <span class="indicator-value">{{ technicalIndicators.bollLower.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-if="selectedConcept" class="analysis-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card title="收益率分析">
            <div ref="returnChart" class="return-chart"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card title="成交量分析">
            <div ref="volumeChart" class="volume-chart"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-if="selectedConcept" class="data-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>历史数据明细 ({{ historicalData.length }}条记录)</span>
            <div class="table-actions">
              <el-button size="small" @click="exportHistoricalData">
                <el-icon><Download /></el-icon>
                导出明细
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table :data="paginatedHistoricalData" stripe height="400">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="openPrice" label="开盘价" width="100">
            <template #default="{ row }">
              <span>{{ row.openPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="highPrice" label="最高价" width="100">
            <template #default="{ row }">
              <span>{{ row.highPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lowPrice" label="最低价" width="100">
            <template #default="{ row }">
              <span>{{ row.lowPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="closePrice" label="收盘价" width="100">
            <template #default="{ row }">
              <span>{{ row.closePrice.toFixed(2) }}</span>
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
          <el-table-column prop="risingStocks" label="上涨股数" width="100">
            <template #default="{ row }">
              <span class="positive">{{ row.risingStocks }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="fallingStocks" label="下跌股数" width="100">
            <template #default="{ row }">
              <span class="negative">{{ row.fallingStocks }}</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="historicalData.length"
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
import { 
  Search, Download, Calendar, TrendCharts, DataAnalysis, 
  CaretTop, CaretBottom, Money 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface ConceptOption {
  code: string
  name: string
}

interface ConceptInfo {
  code: string
  name: string
}

interface HistoricalDataPoint {
  date: string
  openPrice: number
  highPrice: number
  lowPrice: number
  closePrice: number
  changePercent: number
  changeAmount: number
  volume: number
  turnover: number
  amplitude: number
  turnoverRate: number
  risingStocks: number
  fallingStocks: number
}

interface HistoricalSummary {
  tradingDays: number
  totalReturn: number
  volatility: number
  maxPrice: number
  minPrice: number
  avgTurnover: number
}

interface TechnicalIndicators {
  ma5: number
  ma10: number
  ma20: number
  ma60: number
  rsi: number
  macd: number
  kdjK: number
  kdjD: number
  bollUpper: number
  bollLower: number
}

const loading = ref(false)
const dateRange = ref<[string, string]>(['2024-01-01', '2024-12-31'])
const selectedConcept = ref('')
const chartType = ref('candlestick')
const period = ref('1d')
const currentPage = ref(1)
const pageSize = ref(50)

const klineChart = ref<HTMLElement>()
const returnChart = ref<HTMLElement>()
const volumeChart = ref<HTMLElement>()
const klineChartInstance = ref<echarts.ECharts>()
const returnChartInstance = ref<echarts.ECharts>()
const volumeChartInstance = ref<echarts.ECharts>()

const conceptList = ref<ConceptOption[]>([])
const conceptInfo = ref<ConceptInfo>({ code: '', name: '' })
const historicalData = ref<HistoricalDataPoint[]>([])
const historicalSummary = ref<HistoricalSummary>({
  tradingDays: 0,
  totalReturn: 0,
  volatility: 0,
  maxPrice: 0,
  minPrice: 0,
  avgTurnover: 0
})
const technicalIndicators = ref<TechnicalIndicators>({
  ma5: 0,
  ma10: 0,
  ma20: 0,
  ma60: 0,
  rsi: 0,
  macd: 0,
  kdjK: 0,
  kdjD: 0,
  bollUpper: 0,
  bollLower: 0
})

const paginatedHistoricalData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return historicalData.value.slice(start, end)
})

const loadConceptList = async () => {
  try {
    const conceptNames = [
      '人工智能', '新能源汽车', '5G通信', '半导体', '生物医药',
      '新材料', '云计算', '物联网', '区块链', '虚拟现实',
      '工业互联网', '数字货币', '智能制造', '新基建', '碳中和'
    ]
    
    conceptList.value = conceptNames.map((name, index) => ({
      code: `BK${String(index + 1).padStart(4, '0')}`,
      name
    }))
    
    if (conceptList.value.length > 0) {
      selectedConcept.value = conceptList.value[0].code
    }
  } catch (error) {
    ElMessage.error('加载概念列表失败')
  }
}

const loadHistoricalData = async () => {
  if (!selectedConcept.value || !dateRange.value) return
  
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const concept = conceptList.value.find(c => c.code === selectedConcept.value)
    if (!concept) return
    
    conceptInfo.value = {
      code: concept.code,
      name: concept.name
    }
    
    // 生成历史数据
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    const mockData: HistoricalDataPoint[] = []
    
    let currentPrice = Math.random() * 50 + 50
    let currentDate = new Date(startDate)
    
    while (currentDate <= endDate) {
      // 跳过周末
      if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
        const openPrice = currentPrice + (Math.random() - 0.5) * 2
        const highPrice = openPrice + Math.random() * 5
        const lowPrice = openPrice - Math.random() * 5
        const closePrice = lowPrice + Math.random() * (highPrice - lowPrice)
        const changePercent = ((closePrice - openPrice) / openPrice) * 100
        const changeAmount = closePrice - openPrice
        
        mockData.push({
          date: currentDate.toISOString().split('T')[0],
          openPrice,
          highPrice,
          lowPrice,
          closePrice,
          changePercent,
          changeAmount,
          volume: Math.floor(Math.random() * 100000000 + 10000000),
          turnover: Math.random() * 100 + 10,
          amplitude: ((highPrice - lowPrice) / openPrice) * 100,
          turnoverRate: Math.random() * 5 + 1,
          risingStocks: Math.floor(Math.random() * 30) + 10,
          fallingStocks: Math.floor(Math.random() * 20) + 5
        })
        
        currentPrice = closePrice
      }
      
      currentDate.setDate(currentDate.getDate() + 1)
    }
    
    historicalData.value = mockData.reverse() // 最新日期在前
    
    // 计算历史汇总
    if (mockData.length > 0) {
      const firstPrice = mockData[mockData.length - 1].closePrice
      const lastPrice = mockData[0].closePrice
      const totalReturn = ((lastPrice - firstPrice) / firstPrice) * 100
      
      const prices = mockData.map(d => d.closePrice)
      const maxPrice = Math.max(...prices)
      const minPrice = Math.min(...prices)
      const avgTurnover = mockData.reduce((sum, d) => sum + d.turnover, 0) / mockData.length
      
      // 计算波动率
      const returns = mockData.slice(1).map((d, i) => 
        ((d.closePrice - mockData[mockData.length - 2 - i].closePrice) / mockData[mockData.length - 2 - i].closePrice) * 100
      )
      const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
      const volatility = Math.sqrt(variance) * Math.sqrt(252) // 年化波动率
      
      historicalSummary.value = {
        tradingDays: mockData.length,
        totalReturn,
        volatility,
        maxPrice,
        minPrice,
        avgTurnover
      }
    }
    
    // 计算技术指标
    calculateTechnicalIndicators()
    
    nextTick(() => {
      updateChart()
      renderReturnChart()
      renderVolumeChart()
    })
    
    ElMessage.success('历史数据加载成功')
  } catch (error) {
    ElMessage.error('加载历史数据失败')
  } finally {
    loading.value = false
  }
}

const calculateTechnicalIndicators = () => {
  if (historicalData.value.length === 0) return
  
  const prices = historicalData.value.map(d => d.closePrice).reverse() // 时间正序
  const length = prices.length
  
  // 计算移动平均线
  const ma5 = length >= 5 ? prices.slice(-5).reduce((sum, p) => sum + p, 0) / 5 : 0
  const ma10 = length >= 10 ? prices.slice(-10).reduce((sum, p) => sum + p, 0) / 10 : 0
  const ma20 = length >= 20 ? prices.slice(-20).reduce((sum, p) => sum + p, 0) / 20 : 0
  const ma60 = length >= 60 ? prices.slice(-60).reduce((sum, p) => sum + p, 0) / 60 : 0
  
  // 计算RSI
  let rsi = 50
  if (length >= 14) {
    const changes = prices.slice(-14).map((p, i, arr) => i > 0 ? p - arr[i-1] : 0).slice(1)
    const gains = changes.filter(c => c > 0)
    const losses = changes.filter(c => c < 0).map(c => Math.abs(c))
    const avgGain = gains.length > 0 ? gains.reduce((sum, g) => sum + g, 0) / gains.length : 0
    const avgLoss = losses.length > 0 ? losses.reduce((sum, l) => sum + l, 0) / losses.length : 0
    if (avgLoss > 0) {
      const rs = avgGain / avgLoss
      rsi = 100 - (100 / (1 + rs))
    }
  }
  
  // 简化的技术指标计算
  technicalIndicators.value = {
    ma5,
    ma10,
    ma20,
    ma60,
    rsi,
    macd: (Math.random() - 0.5) * 2, // 简化计算
    kdjK: Math.random() * 100,
    kdjD: Math.random() * 100,
    bollUpper: ma20 * 1.02,
    bollLower: ma20 * 0.98
  }
}

const queryData = () => {
  loadHistoricalData()
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const exportHistoricalData = () => {
  ElMessage.success('历史数据导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const updateChart = () => {
  if (chartType.value === 'candlestick') {
    renderKlineChart()
  } else {
    renderLineChart()
  }
}

const renderKlineChart = () => {
  if (!klineChart.value || historicalData.value.length === 0) return
  
  if (!klineChartInstance.value) {
    klineChartInstance.value = echarts.init(klineChart.value)
  }
  
  const data = historicalData.value.slice().reverse() // 时间正序
  const dates = data.map(d => d.date)
  const klineData = data.map(d => [d.openPrice, d.closePrice, d.lowPrice, d.highPrice])
  const volumes = data.map(d => d.volume)
  
  const option = {
    title: {
      text: `${conceptInfo.value.name} K线图`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '成交量'],
      top: 30
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        top: '15%',
        height: '60%'
      },
      {
        left: '10%',
        right: '10%',
        top: '80%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
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
        start: 50,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: function(params: any) {
            const dataIndex = params.dataIndex
            const kline = klineData[dataIndex]
            return kline[1] > kline[0] ? '#ef232a' : '#14b143'
          }
        }
      }
    ]
  }
  
  klineChartInstance.value.setOption(option)
}

const renderLineChart = () => {
  if (!klineChart.value || historicalData.value.length === 0) return
  
  if (!klineChartInstance.value) {
    klineChartInstance.value = echarts.init(klineChart.value)
  }
  
  const data = historicalData.value.slice().reverse()
  const dates = data.map(d => d.date)
  const prices = data.map(d => d.closePrice)
  
  const option = {
    title: {
      text: `${conceptInfo.value.name} 价格走势`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    dataZoom: [
      {
        type: 'inside',
        start: 50,
        end: 100
      },
      {
        show: true,
        type: 'slider',
        start: 50,
        end: 100
      }
    ],
    series: [{
      name: '收盘价',
      type: 'line',
      data: prices,
      smooth: true,
      lineStyle: {
        color: '#5470c6'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
          { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
        ])
      }
    }]
  }
  
  klineChartInstance.value.setOption(option)
}

const renderReturnChart = () => {
  if (!returnChart.value || historicalData.value.length === 0) return
  
  if (!returnChartInstance.value) {
    returnChartInstance.value = echarts.init(returnChart.value)
  }
  
  const data = historicalData.value.slice().reverse()
  const dates = data.map(d => d.date)
  const returns = data.map(d => d.changePercent)
  
  const option = {
    title: {
      text: '日收益率分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}%'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '20%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        formatter: function(value: string, index: number) {
          return index % 10 === 0 ? value.slice(5) : ''
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '收益率',
      type: 'bar',
      data: returns,
      itemStyle: {
        color: function(params: any) {
          return params.value > 0 ? '#f56c6c' : '#67c23a'
        }
      }
    }]
  }
  
  returnChartInstance.value.setOption(option)
}

const renderVolumeChart = () => {
  if (!volumeChart.value || historicalData.value.length === 0) return
  
  if (!volumeChartInstance.value) {
    volumeChartInstance.value = echarts.init(volumeChart.value)
  }
  
  const data = historicalData.value.slice().reverse()
  const dates = data.map(d => d.date)
  const volumes = data.map(d => d.volume)
  const turnovers = data.map(d => d.turnover)
  
  const option = {
    title: {
      text: '成交量/成交额趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['成交量', '成交额'],
      top: 30
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '25%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        formatter: function(value: string, index: number) {
          return index % 10 === 0 ? value.slice(5) : ''
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '成交量',
        position: 'left'
      },
      {
        type: 'value',
        name: '成交额(亿)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        yAxisIndex: 0,
        itemStyle: {
          color: '#91cc75'
        }
      },
      {
        name: '成交额',
        type: 'line',
        data: turnovers,
        yAxisIndex: 1,
        smooth: true,
        lineStyle: {
          color: '#fac858'
        }
      }
    ]
  }
  
  volumeChartInstance.value.setOption(option)
}

const formatDateRange = (): string => {
  if (!dateRange.value) return ''
  return `${dateRange.value[0]} 至 ${dateRange.value[1]}`
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
  loadConceptList()
})

onUnmounted(() => {
  if (klineChartInstance.value) {
    klineChartInstance.value.dispose()
  }
  if (returnChartInstance.value) {
    returnChartInstance.value.dispose()
  }
  if (volumeChartInstance.value) {
    volumeChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.concept-historical-data {
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

.concept-summary {
  margin-bottom: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.concept-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.concept-info h3 {
  margin: 0;
  color: #303133;
}

.concept-code {
  color: #909399;
  font-size: 14px;
}

.period-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.period-label {
  font-size: 14px;
  color: #606266;
}

.period-value {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.summary-metrics {
  margin-top: 20px;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  height: 80px;
}

.metric-icon {
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

.metric-icon.period {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-icon.return {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.metric-icon.volatility {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.metric-icon.max {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.metric-icon.min {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.metric-icon.turnover {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
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
  align-items: center;
}

.kline-chart {
  height: 500px;
}

.technical-indicators {
  padding: 20px;
}

.indicator-group {
  margin-bottom: 20px;
}

.indicator-group h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 14px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 8px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.indicator-item:last-child {
  border-bottom: none;
}

.indicator-name {
  font-size: 13px;
  color: #606266;
}

.indicator-value {
  font-size: 13px;
  font-weight: bold;
  color: #303133;
}

.analysis-section {
  margin-bottom: 20px;
}

.return-chart,
.volume-chart {
  height: 300px;
}

.data-table {
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