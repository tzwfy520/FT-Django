<template>
  <div class="industry-intraday-data">
    <div class="page-header">
      <h2>行业分时数据</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadIntradayData"
        />
        <el-select v-model="selectedIndustry" placeholder="选择行业" @change="loadIntradayData">
          <el-option
            v-for="industry in industryList"
            :key="industry.code"
            :label="industry.name"
            :value="industry.code"
          />
        </el-select>
        <el-button type="primary" @click="loadIntradayData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div class="industry-info" v-if="currentIndustry">
      <el-card>
        <div class="info-header">
          <div class="industry-title">
            <h3>{{ currentIndustry.name }}</h3>
            <span class="industry-code">{{ currentIndustry.code }}</span>
          </div>
          <div class="industry-stats">
            <div class="stat-item">
              <span class="stat-label">现价</span>
              <span class="stat-value">{{ currentIndustry.currentPrice.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">涨跌额</span>
              <span class="stat-value" :class="getChangeClass(currentIndustry.changeAmount)">
                {{ formatChange(currentIndustry.changeAmount, false) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">涨跌幅</span>
              <span class="stat-value" :class="getChangeClass(currentIndustry.changePercent)">
                {{ formatChange(currentIndustry.changePercent) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成交额</span>
              <span class="stat-value">{{ formatAmount(currentIndustry.turnover) }}亿</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">换手率</span>
              <span class="stat-value">{{ currentIndustry.turnoverRate.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="chart-container">
      <el-row :gutter="20">
        <el-col :span="18">
          <el-card title="分时走势图">
            <div class="chart-header">
              <div class="chart-controls">
                <el-radio-group v-model="chartType" @change="updateChart">
                  <el-radio-button label="price">价格走势</el-radio-button>
                  <el-radio-button label="volume">成交量</el-radio-button>
                  <el-radio-button label="turnover">成交额</el-radio-button>
                  <el-radio-button label="capital">资金流向</el-radio-button>
                </el-radio-group>
              </div>
              <div class="chart-info">
                <span class="update-time">更新时间: {{ lastUpdateTime }}</span>
              </div>
            </div>
            <div ref="mainChartContainer" class="main-chart"></div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card title="实时指标">
            <div class="indicators">
              <div class="indicator-item">
                <div class="indicator-label">开盘价</div>
                <div class="indicator-value">{{ currentIndustry?.openPrice?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">最高价</div>
                <div class="indicator-value high">{{ currentIndustry?.highPrice?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">最低价</div>
                <div class="indicator-value low">{{ currentIndustry?.lowPrice?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">昨收价</div>
                <div class="indicator-value">{{ currentIndustry?.prevClose?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">振幅</div>
                <div class="indicator-value">{{ currentIndustry?.amplitude?.toFixed(2) || '-' }}%</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">量比</div>
                <div class="indicator-value">{{ currentIndustry?.volumeRatio?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">委比</div>
                <div class="indicator-value" :class="getChangeClass(currentIndustry?.bidRatio || 0)">
                  {{ currentIndustry?.bidRatio?.toFixed(2) || '-' }}%
                </div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">市盈率</div>
                <div class="indicator-value">{{ currentIndustry?.pe?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">市净率</div>
                <div class="indicator-value">{{ currentIndustry?.pb?.toFixed(2) || '-' }}</div>
              </div>
              <div class="indicator-item">
                <div class="indicator-label">总市值</div>
                <div class="indicator-value">{{ formatAmount(currentIndustry?.marketCap || 0) }}亿</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="data-analysis">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card title="资金流向分析">
            <div ref="capitalFlowChart" class="analysis-chart"></div>
            <div class="capital-summary">
              <div class="capital-item">
                <span class="capital-label">主力净流入:</span>
                <span class="capital-value" :class="getChangeClass(capitalFlowData.mainFlow)">
                  {{ formatAmount(capitalFlowData.mainFlow) }}亿
                </span>
              </div>
              <div class="capital-item">
                <span class="capital-label">超大单:</span>
                <span class="capital-value" :class="getChangeClass(capitalFlowData.superLargeFlow)">
                  {{ formatAmount(capitalFlowData.superLargeFlow) }}亿
                </span>
              </div>
              <div class="capital-item">
                <span class="capital-label">大单:</span>
                <span class="capital-value" :class="getChangeClass(capitalFlowData.largeFlow)">
                  {{ formatAmount(capitalFlowData.largeFlow) }}亿
                </span>
              </div>
              <div class="capital-item">
                <span class="capital-label">中小单:</span>
                <span class="capital-value" :class="getChangeClass(capitalFlowData.smallFlow)">
                  {{ formatAmount(capitalFlowData.smallFlow) }}亿
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card title="成份股表现">
            <div class="stock-performance">
              <div class="performance-summary">
                <div class="summary-item">
                  <span class="summary-label">上涨股票:</span>
                  <span class="summary-value positive">{{ stockPerformance.risingCount }}只</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">下跌股票:</span>
                  <span class="summary-value negative">{{ stockPerformance.fallingCount }}只</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">平盘股票:</span>
                  <span class="summary-value neutral">{{ stockPerformance.flatCount }}只</span>
                </div>
              </div>
              <div class="top-stocks">
                <h5>领涨股</h5>
                <div class="stock-list">
                  <div v-for="stock in stockPerformance.topGainers" :key="stock.code" class="stock-item">
                    <el-button type="text" size="small" @click="viewStockDetail(stock.code)">
                      {{ stock.name }}
                    </el-button>
                    <span :class="getChangeClass(stock.changePercent)">
                      {{ formatChange(stock.changePercent) }}
                    </span>
                  </div>
                </div>
                <h5>领跌股</h5>
                <div class="stock-list">
                  <div v-for="stock in stockPerformance.topLosers" :key="stock.code" class="stock-item">
                    <el-button type="text" size="small" @click="viewStockDetail(stock.code)">
                      {{ stock.name }}
                    </el-button>
                    <span :class="getChangeClass(stock.changePercent)">
                      {{ formatChange(stock.changePercent) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="data-table">
      <el-card title="分时数据明细">
        <div class="table-controls">
          <el-select v-model="timeInterval" placeholder="时间间隔" @change="loadIntradayData">
            <el-option label="1分钟" value="1m" />
            <el-option label="5分钟" value="5m" />
            <el-option label="15分钟" value="15m" />
            <el-option label="30分钟" value="30m" />
            <el-option label="60分钟" value="60m" />
          </el-select>
          <el-input
            v-model="searchTime"
            placeholder="搜索时间 (HH:MM)"
            style="width: 150px;"
            clearable
          />
        </div>
        <el-table
          :data="filteredTableData"
          stripe
          height="400"
          :default-sort="{ prop: 'time', order: 'descending' }"
        >
          <el-table-column prop="time" label="时间" width="100" sortable />
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              <span>{{ row.price.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="change" label="涨跌" width="100">
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
              <span>{{ formatAmount(row.turnover) }}万</span>
            </template>
          </el-table-column>
          <el-table-column prop="avgPrice" label="均价" width="100">
            <template #default="{ row }">
              <span>{{ row.avgPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="capitalFlow" label="资金流向" width="120">
            <template #default="{ row }">
              <span :class="getChangeClass(row.capitalFlow)">{{ formatAmount(row.capitalFlow) }}万</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
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

interface IndustryInfo {
  code: string
  name: string
  currentPrice: number
  changeAmount: number
  changePercent: number
  turnover: number
  turnoverRate: number
  openPrice: number
  highPrice: number
  lowPrice: number
  prevClose: number
  amplitude: number
  volumeRatio: number
  bidRatio: number
  pe: number
  pb: number
  marketCap: number
}

interface IntradayDataPoint {
  time: string
  price: number
  change: number
  changePercent: number
  volume: number
  turnover: number
  avgPrice: number
  capitalFlow: number
}

interface StockInfo {
  code: string
  name: string
  changePercent: number
}

const loading = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedIndustry = ref('BK0001')
const chartType = ref('price')
const timeInterval = ref('1m')
const searchTime = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)
const lastUpdateTime = ref('')

const mainChartContainer = ref<HTMLElement>()
const capitalFlowChart = ref<HTMLElement>()
const mainChartInstance = ref<echarts.ECharts>()
const capitalFlowChartInstance = ref<echarts.ECharts>()

const industryList = ref([
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
const intradayData = ref<IntradayDataPoint[]>([])

const capitalFlowData = ref({
  mainFlow: 0,
  superLargeFlow: 0,
  largeFlow: 0,
  smallFlow: 0
})

const stockPerformance = ref({
  risingCount: 0,
  fallingCount: 0,
  flatCount: 0,
  topGainers: [] as StockInfo[],
  topLosers: [] as StockInfo[]
})

const filteredTableData = computed(() => {
  let filtered = [...intradayData.value]
  
  if (searchTime.value) {
    filtered = filtered.filter(item => item.time.includes(searchTime.value))
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  
  return filtered.slice(start, end)
})

const loadIntradayData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟行业信息
    const industryInfo = industryList.value.find(i => i.code === selectedIndustry.value)
    if (!industryInfo) return
    
    const basePrice = Number((Math.random() * 100 + 50).toFixed(2))
    const changePercent = Number(((Math.random() - 0.5) * 10).toFixed(2))
    const changeAmount = Number((basePrice * changePercent / 100).toFixed(2))
    const currentPrice = basePrice + changeAmount
    
    currentIndustry.value = {
      code: industryInfo.code,
      name: industryInfo.name,
      currentPrice,
      changeAmount,
      changePercent,
      turnover: Number((Math.random() * 500 + 100).toFixed(2)),
      turnoverRate: Number((Math.random() * 5 + 1).toFixed(2)),
      openPrice: Number((basePrice + (Math.random() - 0.5) * 5).toFixed(2)),
      highPrice: Number((currentPrice + Math.random() * 10).toFixed(2)),
      lowPrice: Number((currentPrice - Math.random() * 10).toFixed(2)),
      prevClose: basePrice,
      amplitude: Number((Math.random() * 15 + 5).toFixed(2)),
      volumeRatio: Number((Math.random() * 3 + 0.5).toFixed(2)),
      bidRatio: Number(((Math.random() - 0.5) * 50).toFixed(2)),
      pe: Number((Math.random() * 30 + 10).toFixed(2)),
      pb: Number((Math.random() * 5 + 1).toFixed(2)),
      marketCap: Number((Math.random() * 5000 + 1000).toFixed(2))
    }
    
    // 生成分时数据
    const mockIntradayData: IntradayDataPoint[] = []
    const startTime = new Date(`${selectedDate.value} 09:30:00`)
    
    for (let i = 0; i < 240; i++) { // 4小时交易时间，每分钟一个数据点
      const time = new Date(startTime.getTime() + i * 60000)
      const timeStr = time.toTimeString().slice(0, 5)
      
      const price = basePrice + Math.sin(i / 30) * 5 + (Math.random() - 0.5) * 3
      const change = price - basePrice
      const changePercent = (change / basePrice) * 100
      const volume = Math.floor(Math.random() * 1000000 + 100000)
      const turnover = Number((price * volume / 10000).toFixed(2))
      const avgPrice = Number((basePrice + change / 2).toFixed(2))
      const capitalFlow = Number(((Math.random() - 0.5) * 1000).toFixed(2))
      
      mockIntradayData.push({
        time: timeStr,
        price: Number(price.toFixed(2)),
        change: Number(change.toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        volume,
        turnover,
        avgPrice,
        capitalFlow
      })
    }
    
    intradayData.value = mockIntradayData
    totalCount.value = mockIntradayData.length
    
    // 生成资金流向数据
    capitalFlowData.value = {
      mainFlow: Number(((Math.random() - 0.5) * 100).toFixed(2)),
      superLargeFlow: Number(((Math.random() - 0.5) * 60).toFixed(2)),
      largeFlow: Number(((Math.random() - 0.5) * 40).toFixed(2)),
      smallFlow: Number(((Math.random() - 0.5) * 30).toFixed(2))
    }
    
    // 生成成份股表现数据
    const topGainers: StockInfo[] = []
    const topLosers: StockInfo[] = []
    
    for (let i = 0; i < 5; i++) {
      topGainers.push({
        code: `${String(Math.floor(Math.random() * 999999)).padStart(6, '0')}`,
        name: `${industryInfo.name}股${i + 1}`,
        changePercent: Number((Math.random() * 10 + 5).toFixed(2))
      })
      
      topLosers.push({
        code: `${String(Math.floor(Math.random() * 999999)).padStart(6, '0')}`,
        name: `${industryInfo.name}股${i + 6}`,
        changePercent: Number((-Math.random() * 10 - 5).toFixed(2))
      })
    }
    
    stockPerformance.value = {
      risingCount: Math.floor(Math.random() * 30 + 20),
      fallingCount: Math.floor(Math.random() * 20 + 10),
      flatCount: Math.floor(Math.random() * 5 + 2),
      topGainers,
      topLosers
    }
    
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
    
    await nextTick()
    updateChart()
    renderCapitalFlowChart()
    
    ElMessage.success('分时数据加载成功')
  } catch (error) {
    ElMessage.error('加载分时数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!mainChartContainer.value || !intradayData.value.length) return
  
  if (!mainChartInstance.value) {
    mainChartInstance.value = echarts.init(mainChartContainer.value)
  }
  
  const timeData = intradayData.value.map(item => item.time)
  let seriesData: number[] = []
  let yAxisName = ''
  let color = '#409eff'
  
  switch (chartType.value) {
    case 'price':
      seriesData = intradayData.value.map(item => item.price)
      yAxisName = '价格'
      color = currentIndustry.value?.changePercent >= 0 ? '#f56c6c' : '#67c23a'
      break
    case 'volume':
      seriesData = intradayData.value.map(item => item.volume)
      yAxisName = '成交量'
      color = '#e6a23c'
      break
    case 'turnover':
      seriesData = intradayData.value.map(item => item.turnover)
      yAxisName = '成交额(万)'
      color = '#909399'
      break
    case 'capital':
      seriesData = intradayData.value.map(item => item.capitalFlow)
      yAxisName = '资金流向(万)'
      color = '#67c23a'
      break
  }
  
  const option = {
    title: {
      text: `${currentIndustry.value?.name} - ${getChartTitle()}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        const index = data.dataIndex
        const item = intradayData.value[index]
        return `
          时间: ${item.time}<br/>
          价格: ${item.price.toFixed(2)}<br/>
          涨跌: ${formatChange(item.change, false)}<br/>
          涨跌幅: ${formatChange(item.changePercent)}<br/>
          成交量: ${formatVolume(item.volume)}<br/>
          成交额: ${formatAmount(item.turnover)}万<br/>
          资金流向: ${formatAmount(item.capitalFlow)}万
        `
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
      data: timeData,
      axisLabel: {
        interval: 30
      }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      scale: true
    },
    series: [{
      type: chartType.value === 'volume' ? 'bar' : 'line',
      data: seriesData,
      smooth: chartType.value !== 'volume',
      symbol: 'none',
      lineStyle: {
        width: 2,
        color
      },
      itemStyle: {
        color
      },
      areaStyle: chartType.value !== 'volume' ? {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: color + '40'
          }, {
            offset: 1,
            color: color + '10'
          }]
        }
      } : undefined
    }]
  }
  
  mainChartInstance.value.setOption(option)
}

const renderCapitalFlowChart = () => {
  if (!capitalFlowChart.value) return
  
  if (!capitalFlowChartInstance.value) {
    capitalFlowChartInstance.value = echarts.init(capitalFlowChart.value)
  }
  
  const data = [
    { name: '超大单', value: Math.abs(capitalFlowData.value.superLargeFlow), flow: capitalFlowData.value.superLargeFlow },
    { name: '大单', value: Math.abs(capitalFlowData.value.largeFlow), flow: capitalFlowData.value.largeFlow },
    { name: '中小单', value: Math.abs(capitalFlowData.value.smallFlow), flow: capitalFlowData.value.smallFlow }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const item = data[params.dataIndex]
        const flowText = item.flow >= 0 ? '流入' : '流出'
        return `${params.name}: ${formatAmount(item.flow)}亿 (${flowText})`
      }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map(item => ({
        name: item.name,
        value: item.value,
        itemStyle: {
          color: item.flow >= 0 ? '#f56c6c' : '#67c23a'
        }
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  capitalFlowChartInstance.value.setOption(option)
}

const getChartTitle = (): string => {
  const titles: Record<string, string> = {
    price: '价格走势',
    volume: '成交量',
    turnover: '成交额',
    capital: '资金流向'
  }
  return titles[chartType.value] || '分时走势'
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
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

onMounted(() => {
  loadIntradayData()
})

onUnmounted(() => {
  if (mainChartInstance.value) {
    mainChartInstance.value.dispose()
  }
  if (capitalFlowChartInstance.value) {
    capitalFlowChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.industry-intraday-data {
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

.industry-info {
  margin-bottom: 20px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.industry-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.industry-title h3 {
  margin: 0;
  color: #303133;
}

.industry-code {
  color: #909399;
  font-size: 14px;
}

.industry-stats {
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
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.chart-container {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-info {
  font-size: 12px;
  color: #909399;
}

.main-chart {
  height: 400px;
}

.indicators {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.indicator-label {
  font-size: 14px;
  color: #606266;
}

.indicator-value {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.indicator-value.high {
  color: #f56c6c;
}

.indicator-value.low {
  color: #67c23a;
}

.data-analysis {
  margin-bottom: 20px;
}

.analysis-chart {
  height: 250px;
  margin-bottom: 15px;
}

.capital-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.capital-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.capital-label {
  font-size: 14px;
  color: #606266;
}

.capital-value {
  font-size: 14px;
  font-weight: bold;
}

.stock-performance {
  padding: 10px 0;
}

.performance-summary {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.summary-label {
  font-size: 14px;
  color: #606266;
}

.summary-value {
  font-size: 14px;
  font-weight: bold;
}

.top-stocks h5 {
  margin: 15px 0 10px 0;
  color: #303133;
  font-size: 14px;
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 15px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
}

.table-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
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