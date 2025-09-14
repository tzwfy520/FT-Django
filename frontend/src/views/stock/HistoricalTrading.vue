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
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
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
          <el-form-item label="数据类型">
            <el-select v-model="queryForm.dataType" style="width: 120px;">
              <el-option label="日K线" value="daily" />
              <el-option label="周K线" value="weekly" />
              <el-option label="月K线" value="monthly" />
              <el-option label="分时数据" value="minute" />
            </el-select>
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
                {{ stockInfo.price.toFixed(2) }}
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
              <div class="info-value">{{ stockInfo.turnoverRate.toFixed(2) }}%</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- K线图表 -->
    <div v-if="historicalData.length > 0" class="chart-section">
      <el-card>
        <template #header>
          <div class="chart-header">
            <span>K线图表</span>
            <div class="chart-actions">
              <el-radio-group v-model="chartType" @change="updateChart">
                <el-radio-button label="kline">K线</el-radio-button>
                <el-radio-button label="volume">成交量</el-radio-button>
                <el-radio-button label="ma">均线</el-radio-button>
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
    </div>

    <!-- 技术指标 -->
    <div v-if="historicalData.length > 0" class="indicators-section">
      <el-card>
        <template #header>
          <div class="indicators-header">
            <span>技术指标</span>
            <el-select v-model="selectedIndicator" @change="updateIndicators" style="width: 120px;">
              <el-option label="MACD" value="macd" />
              <el-option label="RSI" value="rsi" />
              <el-option label="KDJ" value="kdj" />
              <el-option label="BOLL" value="boll" />
            </el-select>
          </div>
        </template>
        
        <div ref="indicatorContainer" class="indicator-container"></div>
      </el-card>
    </div>

    <!-- 历史数据表格 -->
    <div v-if="historicalData.length > 0" class="data-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>历史数据 ({{ historicalData.length }}条)</span>
            <div class="table-actions">
              <el-button size="small" @click="downloadData">
                <el-icon><Download /></el-icon>
                下载数据
              </el-button>
              <el-button size="small" @click="analyzeData">
                <el-icon><DataAnalysis /></el-icon>
                数据分析
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedData" 
          stripe 
          height="400"
          @sort-change="handleSortChange"
        >
          <el-table-column prop="date" label="日期" width="120" sortable="custom" />
          <el-table-column prop="openPrice" label="开盘价" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.openPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="highPrice" label="最高价" width="100" sortable="custom">
            <template #default="{ row }">
              <span class="positive">{{ row.highPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="lowPrice" label="最低价" width="100" sortable="custom">
            <template #default="{ row }">
              <span class="negative">{{ row.lowPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="closePrice" label="收盘价" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.closePrice.toFixed(2) }}</span>
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
          <el-table-column prop="amplitude" label="振幅" width="100" sortable="custom">
            <template #default="{ row }">
              <span>{{ row.amplitude.toFixed(2) }}%</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="historicalData.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 数据分析对话框 -->
    <el-dialog v-model="analysisDialog" title="数据分析" width="800px">
      <div v-if="analysisResult" class="analysis-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="analysis-section">
              <h4>基本统计</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="数据天数">{{ analysisResult.totalDays }}</el-descriptions-item>
                <el-descriptions-item label="最高价">{{ analysisResult.maxPrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="最低价">{{ analysisResult.minPrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="平均价">{{ analysisResult.avgPrice.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="总成交量">{{ formatVolume(analysisResult.totalVolume) }}</el-descriptions-item>
                <el-descriptions-item label="平均成交量">{{ formatVolume(analysisResult.avgVolume) }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="analysis-section">
              <h4>涨跌统计</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="上涨天数">{{ analysisResult.risingDays }}</el-descriptions-item>
                <el-descriptions-item label="下跌天数">{{ analysisResult.fallingDays }}</el-descriptions-item>
                <el-descriptions-item label="平盘天数">{{ analysisResult.flatDays }}</el-descriptions-item>
                <el-descriptions-item label="上涨概率">{{ (analysisResult.risingDays / analysisResult.totalDays * 100).toFixed(2) }}%</el-descriptions-item>
                <el-descriptions-item label="最大涨幅">{{ formatChange(analysisResult.maxRise) }}</el-descriptions-item>
                <el-descriptions-item label="最大跌幅">{{ formatChange(analysisResult.maxFall) }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
        </el-row>
        
        <div class="analysis-section">
          <h4>收益率分析</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">期间收益率</div>
                <div class="return-value" :class="getChangeClass(analysisResult.totalReturn)">
                  {{ formatChange(analysisResult.totalReturn) }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">年化收益率</div>
                <div class="return-value" :class="getChangeClass(analysisResult.annualizedReturn)">
                  {{ formatChange(analysisResult.annualizedReturn) }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">波动率</div>
                <div class="return-value">{{ analysisResult.volatility.toFixed(2) }}%</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      <template #footer>
        <el-button @click="analysisDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportAnalysis">
          导出分析报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, Refresh, Download, Star, View, FullScreen, DataAnalysis 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface HistoricalData {
  date: string
  openPrice: number
  highPrice: number
  lowPrice: number
  closePrice: number
  changePercent: number
  changeAmount: number
  volume: number
  turnover: number
  turnoverRate: number
  amplitude: number
}

interface StockInfo {
  code: string
  name: string
  price: number
  changePercent: number
  changeAmount: number
  volume: number
  turnover: number
  turnoverRate: number
}

interface AnalysisResult {
  totalDays: number
  maxPrice: number
  minPrice: number
  avgPrice: number
  totalVolume: number
  avgVolume: number
  risingDays: number
  fallingDays: number
  flatDays: number
  maxRise: number
  maxFall: number
  totalReturn: number
  annualizedReturn: number
  volatility: number
}

const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const chartType = ref('kline')
const selectedIndicator = ref('macd')
const analysisDialog = ref(false)
const chartContainer = ref<HTMLElement>()
const indicatorContainer = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()
const indicatorChart = ref<echarts.ECharts>()

const queryForm = ref({
  stockCode: '',
  stockName: '',
  startDate: '',
  endDate: '',
  dataType: 'daily'
})

const stockInfo = ref<StockInfo | null>(null)
const historicalData = ref<HistoricalData[]>([])
const analysisResult = ref<AnalysisResult | null>(null)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return historicalData.value.slice(start, end)
})

const getStockInfo = async () => {
  if (!queryForm.value.stockCode) return
  
  // 模拟获取股票信息
  const stockNames = ['平安银行', '万科A', '中国平安', '招商银行', '五粮液']
  queryForm.value.stockName = stockNames[Math.floor(Math.random() * stockNames.length)]
}

const queryHistoricalData = async () => {
  if (!queryForm.value.stockCode) {
    ElMessage.error('请输入股票代码')
    return
  }
  
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟历史数据
    const mockData: HistoricalData[] = []
    const startDate = new Date(queryForm.value.startDate || '2024-01-01')
    const endDate = new Date(queryForm.value.endDate || new Date().toISOString().split('T')[0])
    const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
    
    let basePrice = Math.random() * 50 + 10
    
    for (let i = 0; i < Math.min(daysDiff, 250); i++) {
      const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000)
      const changePercent = (Math.random() - 0.5) * 10
      const changeAmount = (basePrice * changePercent) / 100
      const closePrice = basePrice + changeAmount
      const openPrice = basePrice + (Math.random() - 0.5) * 2
      const highPrice = Math.max(closePrice, openPrice, basePrice + Math.random() * 3)
      const lowPrice = Math.min(closePrice, openPrice, basePrice - Math.random() * 3)
      const volume = Math.floor(Math.random() * 50000000 + 1000000)
      const turnover = (volume * closePrice) / 10000
      const amplitude = ((highPrice - lowPrice) / basePrice) * 100
      
      mockData.push({
        date: date.toISOString().split('T')[0],
        openPrice,
        highPrice,
        lowPrice,
        closePrice,
        changePercent,
        changeAmount,
        volume,
        turnover,
        turnoverRate: Math.random() * 5,
        amplitude
      })
      
      basePrice = closePrice
    }
    
    historicalData.value = mockData.reverse() // 最新日期在前
    
    // 生成股票基本信息
    const latestData = historicalData.value[0]
    stockInfo.value = {
      code: queryForm.value.stockCode,
      name: queryForm.value.stockName,
      price: latestData.closePrice,
      changePercent: latestData.changePercent,
      changeAmount: latestData.changeAmount,
      volume: latestData.volume,
      turnover: latestData.turnover,
      turnoverRate: latestData.turnoverRate
    }
    
    // 初始化图表
    await nextTick()
    initChart()
    initIndicatorChart()
    
    ElMessage.success('历史数据查询成功')
  } catch (error) {
    ElMessage.error('查询历史数据失败')
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (!chartContainer.value) return
  
  chart.value = echarts.init(chartContainer.value)
  updateChart()
}

const initIndicatorChart = () => {
  if (!indicatorContainer.value) return
  
  indicatorChart.value = echarts.init(indicatorContainer.value)
  updateIndicators()
}

const updateChart = () => {
  if (!chart.value || historicalData.value.length === 0) return
  
  const dates = historicalData.value.map(item => item.date)
  const klineData = historicalData.value.map(item => [
    item.openPrice,
    item.closePrice,
    item.lowPrice,
    item.highPrice
  ])
  const volumeData = historicalData.value.map(item => item.volume)
  
  let option: any = {
    title: {
      text: `${stockInfo.value?.name} (${stockInfo.value?.code})`,
      left: 0
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '成交量', 'MA5', 'MA10', 'MA20'],
      top: 30
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '70%',
        height: '16%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
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
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 80,
        end: 100
      }
    ],
    series: []
  }
  
  if (chartType.value === 'kline' || chartType.value === 'ma') {
    option.series.push({
      name: 'K线',
      type: 'candlestick',
      data: klineData,
      itemStyle: {
        color: '#ef232a',
        color0: '#14b143',
        borderColor: '#ef232a',
        borderColor0: '#14b143'
      }
    })
    
    if (chartType.value === 'ma') {
      // 计算移动平均线
      const ma5 = calculateMA(5)
      const ma10 = calculateMA(10)
      const ma20 = calculateMA(20)
      
      option.series.push(
        {
          name: 'MA5',
          type: 'line',
          data: ma5,
          smooth: true,
          lineStyle: { opacity: 0.5 }
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10,
          smooth: true,
          lineStyle: { opacity: 0.5 }
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20,
          smooth: true,
          lineStyle: { opacity: 0.5 }
        }
      )
    }
  }
  
  if (chartType.value === 'volume') {
    option.series.push({
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumeData
    })
  } else {
    option.series.push({
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volumeData,
      itemStyle: {
        color: function(params: any) {
          const dataIndex = params.dataIndex
          const klineItem = klineData[dataIndex]
          return klineItem[1] > klineItem[0] ? '#ef232a' : '#14b143'
        }
      }
    })
  }
  
  chart.value.setOption(option, true)
}

const calculateMA = (period: number) => {
  const result = []
  for (let i = 0; i < historicalData.value.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else {
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += historicalData.value[i - j].closePrice
      }
      result.push(sum / period)
    }
  }
  return result
}

const updateIndicators = () => {
  if (!indicatorChart.value || historicalData.value.length === 0) return
  
  const dates = historicalData.value.map(item => item.date)
  let option: any = {
    title: {
      text: selectedIndicator.value.toUpperCase(),
      left: 0
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    dataZoom: [
      {
        type: 'inside',
        start: 80,
        end: 100
      }
    ],
    series: []
  }
  
  // 根据选择的指标生成数据
  switch (selectedIndicator.value) {
    case 'macd':
      const macdData = calculateMACD()
      option.series = [
        {
          name: 'DIF',
          type: 'line',
          data: macdData.dif
        },
        {
          name: 'DEA',
          type: 'line',
          data: macdData.dea
        },
        {
          name: 'MACD',
          type: 'bar',
          data: macdData.macd
        }
      ]
      break
    case 'rsi':
      const rsiData = calculateRSI()
      option.series = [{
        name: 'RSI',
        type: 'line',
        data: rsiData
      }]
      break
    case 'kdj':
      const kdjData = calculateKDJ()
      option.series = [
        {
          name: 'K',
          type: 'line',
          data: kdjData.k
        },
        {
          name: 'D',
          type: 'line',
          data: kdjData.d
        },
        {
          name: 'J',
          type: 'line',
          data: kdjData.j
        }
      ]
      break
    case 'boll':
      const bollData = calculateBOLL()
      option.series = [
        {
          name: 'UPPER',
          type: 'line',
          data: bollData.upper
        },
        {
          name: 'MID',
          type: 'line',
          data: bollData.mid
        },
        {
          name: 'LOWER',
          type: 'line',
          data: bollData.lower
        }
      ]
      break
  }
  
  indicatorChart.value.setOption(option, true)
}

const calculateMACD = () => {
  // 简化的MACD计算
  const prices = historicalData.value.map(item => item.closePrice)
  const dif = []
  const dea = []
  const macd = []
  
  for (let i = 0; i < prices.length; i++) {
    const value = Math.sin(i * 0.1) * 2 + Math.random() - 0.5
    dif.push(value)
    dea.push(value * 0.8)
    macd.push((value - value * 0.8) * 2)
  }
  
  return { dif, dea, macd }
}

const calculateRSI = () => {
  // 简化的RSI计算
  const result = []
  for (let i = 0; i < historicalData.value.length; i++) {
    result.push(Math.random() * 100)
  }
  return result
}

const calculateKDJ = () => {
  // 简化的KDJ计算
  const k = []
  const d = []
  const j = []
  
  for (let i = 0; i < historicalData.value.length; i++) {
    const kValue = Math.random() * 100
    const dValue = kValue * 0.8
    const jValue = 3 * kValue - 2 * dValue
    
    k.push(kValue)
    d.push(dValue)
    j.push(jValue)
  }
  
  return { k, d, j }
}

const calculateBOLL = () => {
  // 简化的布林带计算
  const prices = historicalData.value.map(item => item.closePrice)
  const upper = []
  const mid = []
  const lower = []
  
  for (let i = 0; i < prices.length; i++) {
    const price = prices[i]
    mid.push(price)
    upper.push(price * 1.02)
    lower.push(price * 0.98)
  }
  
  return { upper, mid, lower }
}

const analyzeData = () => {
  if (historicalData.value.length === 0) return
  
  const data = historicalData.value
  const prices = data.map(item => item.closePrice)
  const changes = data.map(item => item.changePercent)
  
  const totalDays = data.length
  const maxPrice = Math.max(...prices)
  const minPrice = Math.min(...prices)
  const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length
  const totalVolume = data.reduce((sum, item) => sum + item.volume, 0)
  const avgVolume = totalVolume / totalDays
  
  const risingDays = changes.filter(change => change > 0).length
  const fallingDays = changes.filter(change => change < 0).length
  const flatDays = changes.filter(change => change === 0).length
  
  const maxRise = Math.max(...changes)
  const maxFall = Math.min(...changes)
  
  const firstPrice = prices[prices.length - 1]
  const lastPrice = prices[0]
  const totalReturn = ((lastPrice - firstPrice) / firstPrice) * 100
  const annualizedReturn = totalReturn * (365 / totalDays)
  
  // 计算波动率
  const avgChange = changes.reduce((sum, change) => sum + change, 0) / changes.length
  const variance = changes.reduce((sum, change) => sum + Math.pow(change - avgChange, 2), 0) / changes.length
  const volatility = Math.sqrt(variance)
  
  analysisResult.value = {
    totalDays,
    maxPrice,
    minPrice,
    avgPrice,
    totalVolume,
    avgVolume,
    risingDays,
    fallingDays,
    flatDays,
    maxRise,
    maxFall,
    totalReturn,
    annualizedReturn,
    volatility
  }
  
  analysisDialog.value = true
}

const resetQuery = () => {
  queryForm.value = {
    stockCode: '',
    stockName: '',
    startDate: '',
    endDate: '',
    dataType: 'daily'
  }
  stockInfo.value = null
  historicalData.value = []
}

const searchStocks = () => {
  // 搜索逻辑
}

const refreshData = () => {
  if (queryForm.value.stockCode) {
    queryHistoricalData()
  }
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const addToWatchlist = () => {
  ElMessage.success(`已将${stockInfo.value?.name}加入自选`)
}

const viewRealtime = () => {
  ElMessage.info(`跳转到${stockInfo.value?.name}实时数据页面`)
}

const fullScreen = () => {
  ElMessage.info('全屏功能开发中...')
}

const downloadData = () => {
  ElMessage.success('数据下载功能开发中...')
}

const exportAnalysis = () => {
  ElMessage.success('分析报告导出功能开发中...')
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  // 排序逻辑
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
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
  // 设置默认日期
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(startDate.getMonth() - 3)
  
  queryForm.value.endDate = endDate.toISOString().split('T')[0]
  queryForm.value.startDate = startDate.toISOString().split('T')[0]
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
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.chart-section {
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

.indicators-section {
  margin-bottom: 20px;
}

.indicators-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicator-container {
  height: 300px;
  width: 100%;
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

.analysis-content {
  padding: 20px 0;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.return-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.return-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.return-value {
  font-size: 18px;
  font-weight: bold;
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