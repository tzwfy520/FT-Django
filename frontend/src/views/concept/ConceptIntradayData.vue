<template>
  <div class="concept-intraday-data">
    <div class="page-header">
      <h2>概念分时数据</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadIntradayData"
        />
        <el-select v-model="selectedConcept" placeholder="选择概念" @change="loadIntradayData">
          <el-option
            v-for="concept in conceptList"
            :key="concept.code"
            :label="concept.name"
            :value="concept.code"
          />
        </el-select>
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div v-if="selectedConcept" class="concept-info">
      <el-card>
        <div class="concept-basic">
          <div class="concept-title">
            <h3>{{ conceptInfo.name }}</h3>
            <span class="concept-code">{{ conceptInfo.code }}</span>
          </div>
          <div class="concept-metrics">
            <div class="metric-item">
              <span class="metric-label">当前价格</span>
              <span class="metric-value">{{ conceptInfo.currentPrice.toFixed(2) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">涨跌幅</span>
              <span class="metric-value" :class="getChangeClass(conceptInfo.changePercent)">
                {{ formatChange(conceptInfo.changePercent) }}
              </span>
            </div>
            <div class="metric-item">
              <span class="metric-label">涨跌额</span>
              <span class="metric-value" :class="getChangeClass(conceptInfo.changeAmount)">
                {{ formatChangeAmount(conceptInfo.changeAmount) }}
              </span>
            </div>
            <div class="metric-item">
              <span class="metric-label">成交额</span>
              <span class="metric-value">{{ formatAmount(conceptInfo.turnover) }}亿</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">成份股数</span>
              <span class="metric-value">{{ conceptInfo.stockCount }}只</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">上涨股数</span>
              <span class="metric-value positive">{{ conceptInfo.risingStocks }}只</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div v-if="selectedConcept" class="chart-section">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card title="分时走势图">
            <div ref="intradayChart" class="intraday-chart"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card title="实时指标">
            <div class="realtime-indicators">
              <div class="indicator-item">
                <span class="indicator-label">振幅</span>
                <span class="indicator-value">{{ conceptInfo.amplitude.toFixed(2) }}%</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">换手率</span>
                <span class="indicator-value">{{ conceptInfo.turnoverRate.toFixed(2) }}%</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">量比</span>
                <span class="indicator-value">{{ conceptInfo.volumeRatio.toFixed(2) }}</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">市净率</span>
                <span class="indicator-value">{{ conceptInfo.pbRatio.toFixed(2) }}</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">市盈率</span>
                <span class="indicator-value">{{ conceptInfo.peRatio.toFixed(2) }}</span>
              </div>
              <div class="indicator-item">
                <span class="indicator-label">总市值</span>
                <span class="indicator-value">{{ formatAmount(conceptInfo.marketCap) }}亿</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-if="selectedConcept" class="analysis-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card title="资金流向分析">
            <div ref="capitalFlowChart" class="capital-flow-chart"></div>
            <div class="capital-flow-summary">
              <div class="flow-item">
                <span class="flow-label">主力净流入</span>
                <span class="flow-value" :class="getChangeClass(capitalFlow.mainNetInflow)">
                  {{ formatAmount(Math.abs(capitalFlow.mainNetInflow)) }}亿
                </span>
              </div>
              <div class="flow-item">
                <span class="flow-label">超大单净流入</span>
                <span class="flow-value" :class="getChangeClass(capitalFlow.superLargeNetInflow)">
                  {{ formatAmount(Math.abs(capitalFlow.superLargeNetInflow)) }}亿
                </span>
              </div>
              <div class="flow-item">
                <span class="flow-label">大单净流入</span>
                <span class="flow-value" :class="getChangeClass(capitalFlow.largeNetInflow)">
                  {{ formatAmount(Math.abs(capitalFlow.largeNetInflow)) }}亿
                </span>
              </div>
              <div class="flow-item">
                <span class="flow-label">中单净流入</span>
                <span class="flow-value" :class="getChangeClass(capitalFlow.mediumNetInflow)">
                  {{ formatAmount(Math.abs(capitalFlow.mediumNetInflow)) }}亿
                </span>
              </div>
              <div class="flow-item">
                <span class="flow-label">小单净流入</span>
                <span class="flow-value" :class="getChangeClass(capitalFlow.smallNetInflow)">
                  {{ formatAmount(Math.abs(capitalFlow.smallNetInflow)) }}亿
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card title="成份股表现">
            <el-table :data="topStocks" stripe max-height="400">
              <el-table-column type="index" label="#" width="50" />
              <el-table-column prop="name" label="股票名称" width="120" />
              <el-table-column prop="code" label="代码" width="100" />
              <el-table-column prop="price" label="现价" width="80">
                <template #default="{ row }">
                  <span>{{ row.price.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="changePercent" label="涨跌幅" width="100">
                <template #default="{ row }">
                  <span :class="getChangeClass(row.changePercent)">
                    {{ formatChange(row.changePercent) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="turnover" label="成交额" width="100">
                <template #default="{ row }">
                  <span>{{ formatAmount(row.turnover) }}亿</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-if="selectedConcept" class="data-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>分时数据明细</span>
            <div class="table-actions">
              <el-button size="small" @click="exportIntradayData">
                <el-icon><Download /></el-icon>
                导出明细
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table :data="paginatedIntradayData" stripe height="400">
          <el-table-column prop="time" label="时间" width="100" />
          <el-table-column prop="price" label="价格" width="100">
            <template #default="{ row }">
              <span>{{ row.price.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
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
          <el-table-column prop="avgPrice" label="均价" width="100">
            <template #default="{ row }">
              <span>{{ row.avgPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="netInflow" label="净流入" width="120">
            <template #default="{ row }">
              <span :class="getChangeClass(row.netInflow)">
                {{ formatAmount(Math.abs(row.netInflow)) }}万
              </span>
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
          <el-table-column prop="leadingStock" label="领涨股" width="150">
            <template #default="{ row }">
              <div class="leading-stock">
                <span class="stock-name">{{ row.leadingStock.name }}</span>
                <span class="stock-change" :class="getChangeClass(row.leadingStock.changePercent)">
                  {{ formatChange(row.leadingStock.changePercent) }}
                </span>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="intradayData.length"
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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface ConceptOption {
  code: string
  name: string
}

interface ConceptInfo {
  code: string
  name: string
  currentPrice: number
  changePercent: number
  changeAmount: number
  turnover: number
  stockCount: number
  risingStocks: number
  amplitude: number
  turnoverRate: number
  volumeRatio: number
  pbRatio: number
  peRatio: number
  marketCap: number
}

interface IntradayDataPoint {
  time: string
  price: number
  changePercent: number
  volume: number
  turnover: number
  avgPrice: number
  netInflow: number
  risingStocks: number
  fallingStocks: number
  leadingStock: {
    name: string
    changePercent: number
  }
}

interface Stock {
  code: string
  name: string
  price: number
  changePercent: number
  turnover: number
}

interface CapitalFlow {
  mainNetInflow: number
  superLargeNetInflow: number
  largeNetInflow: number
  mediumNetInflow: number
  smallNetInflow: number
}

const loading = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedConcept = ref('')
const currentPage = ref(1)
const pageSize = ref(50)

const intradayChart = ref<HTMLElement>()
const capitalFlowChart = ref<HTMLElement>()
const intradayChartInstance = ref<echarts.ECharts>()
const capitalFlowChartInstance = ref<echarts.ECharts>()

const conceptList = ref<ConceptOption[]>([])
const conceptInfo = ref<ConceptInfo>({
  code: '',
  name: '',
  currentPrice: 0,
  changePercent: 0,
  changeAmount: 0,
  turnover: 0,
  stockCount: 0,
  risingStocks: 0,
  amplitude: 0,
  turnoverRate: 0,
  volumeRatio: 0,
  pbRatio: 0,
  peRatio: 0,
  marketCap: 0
})

const intradayData = ref<IntradayDataPoint[]>([])
const topStocks = ref<Stock[]>([])
const capitalFlow = ref<CapitalFlow>({
  mainNetInflow: 0,
  superLargeNetInflow: 0,
  largeNetInflow: 0,
  mediumNetInflow: 0,
  smallNetInflow: 0
})

const paginatedIntradayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return intradayData.value.slice(start, end)
})

const loadConceptList = async () => {
  try {
    // 模拟API调用
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

const loadIntradayData = async () => {
  if (!selectedConcept.value) return
  
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const concept = conceptList.value.find(c => c.code === selectedConcept.value)
    if (!concept) return
    
    // 生成概念基本信息
    const currentPrice = Math.random() * 100 + 50
    const changePercent = (Math.random() - 0.5) * 10
    const changeAmount = currentPrice * changePercent / 100
    
    conceptInfo.value = {
      code: concept.code,
      name: concept.name,
      currentPrice,
      changePercent,
      changeAmount,
      turnover: Math.random() * 200 + 50,
      stockCount: Math.floor(Math.random() * 50) + 20,
      risingStocks: Math.floor(Math.random() * 30) + 10,
      amplitude: Math.random() * 8 + 2,
      turnoverRate: Math.random() * 5 + 1,
      volumeRatio: Math.random() * 3 + 0.5,
      pbRatio: Math.random() * 5 + 1,
      peRatio: Math.random() * 50 + 10,
      marketCap: Math.random() * 5000 + 1000
    }
    
    // 生成分时数据
    const mockIntradayData: IntradayDataPoint[] = []
    const startTime = new Date()
    startTime.setHours(9, 30, 0, 0)
    
    for (let i = 0; i < 240; i++) { // 4小时 * 60分钟
      const time = new Date(startTime.getTime() + i * 60000)
      const timeStr = time.toTimeString().slice(0, 5)
      
      // 跳过中午休市时间
      if (time.getHours() === 11 && time.getMinutes() >= 30) {
        continue
      }
      if (time.getHours() === 12) {
        continue
      }
      if (time.getHours() === 13 && time.getMinutes() < 0) {
        continue
      }
      
      const price = currentPrice + (Math.random() - 0.5) * 10
      const changePercentPoint = ((price - currentPrice) / currentPrice) * 100
      
      mockIntradayData.push({
        time: timeStr,
        price,
        changePercent: changePercentPoint,
        volume: Math.floor(Math.random() * 1000000 + 100000),
        turnover: Math.random() * 10000 + 1000,
        avgPrice: price + (Math.random() - 0.5) * 2,
        netInflow: (Math.random() - 0.5) * 5000,
        risingStocks: Math.floor(Math.random() * 20) + 5,
        fallingStocks: Math.floor(Math.random() * 15) + 3,
        leadingStock: {
          name: `领涨股${i % 5 + 1}`,
          changePercent: Math.random() * 10 + 1
        }
      })
    }
    
    intradayData.value = mockIntradayData
    
    // 生成成份股数据
    topStocks.value = Array.from({ length: 10 }, (_, i) => ({
      code: `${String(Math.floor(Math.random() * 900000) + 100000)}`,
      name: `成份股${i + 1}`,
      price: Math.random() * 100 + 10,
      changePercent: (Math.random() - 0.5) * 15,
      turnover: Math.random() * 50 + 5
    }))
    
    // 生成资金流向数据
    capitalFlow.value = {
      mainNetInflow: (Math.random() - 0.5) * 100,
      superLargeNetInflow: (Math.random() - 0.5) * 50,
      largeNetInflow: (Math.random() - 0.5) * 30,
      mediumNetInflow: (Math.random() - 0.5) * 20,
      smallNetInflow: (Math.random() - 0.5) * 10
    }
    
    nextTick(() => {
      renderIntradayChart()
      renderCapitalFlowChart()
    })
    
    ElMessage.success('分时数据加载成功')
  } catch (error) {
    ElMessage.error('加载分时数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadIntradayData()
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const exportIntradayData = () => {
  ElMessage.success('分时数据导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const renderIntradayChart = () => {
  if (!intradayChart.value || intradayData.value.length === 0) return
  
  if (!intradayChartInstance.value) {
    intradayChartInstance.value = echarts.init(intradayChart.value)
  }
  
  const times = intradayData.value.map(item => item.time)
  const prices = intradayData.value.map(item => item.price)
  const volumes = intradayData.value.map(item => item.volume)
  const avgPrices = intradayData.value.map(item => item.avgPrice)
  
  const option = {
    title: {
      text: `${conceptInfo.value.name} 分时走势`,
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params: any) {
        const time = params[0].axisValue
        let result = `时间: ${time}<br/>`
        params.forEach((param: any) => {
          result += `${param.seriesName}: ${param.value.toFixed(2)}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['价格', '均价', '成交量'],
      top: 30
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        top: '15%',
        height: '50%'
      },
      {
        left: '10%',
        right: '10%',
        top: '70%',
        height: '20%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: times,
        gridIndex: 0,
        axisLabel: {
          formatter: function(value: string, index: number) {
            return index % 30 === 0 ? value : ''
          }
        }
      },
      {
        type: 'category',
        data: times,
        gridIndex: 1,
        axisLabel: {
          formatter: function(value: string, index: number) {
            return index % 30 === 0 ? value : ''
          }
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        gridIndex: 0,
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        type: 'value',
        gridIndex: 1,
        scale: true,
        splitArea: {
          show: true
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        xAxisIndex: 0,
        yAxisIndex: 0,
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
      },
      {
        name: '均价',
        type: 'line',
        data: avgPrices,
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: true,
        lineStyle: {
          color: '#fc8452',
          type: 'dashed'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: {
          color: '#91cc75'
        }
      }
    ]
  }
  
  intradayChartInstance.value.setOption(option)
}

const renderCapitalFlowChart = () => {
  if (!capitalFlowChart.value) return
  
  if (!capitalFlowChartInstance.value) {
    capitalFlowChartInstance.value = echarts.init(capitalFlowChart.value)
  }
  
  const data = [
    { name: '超大单', value: capitalFlow.value.superLargeNetInflow },
    { name: '大单', value: capitalFlow.value.largeNetInflow },
    { name: '中单', value: capitalFlow.value.mediumNetInflow },
    { name: '小单', value: capitalFlow.value.smallNetInflow }
  ]
  
  const option = {
    title: {
      text: '资金流向分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}亿 ({d}%)'
    },
    series: [{
      name: '资金流向',
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map(item => ({
        ...item,
        itemStyle: {
          color: item.value > 0 ? '#f56c6c' : '#67c23a'
        }
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        show: true,
        formatter: '{b}: {c}亿'
      }
    }]
  }
  
  capitalFlowChartInstance.value.setOption(option)
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

watch(selectedConcept, () => {
  if (selectedConcept.value) {
    loadIntradayData()
  }
})

onMounted(() => {
  loadConceptList()
})

onUnmounted(() => {
  if (intradayChartInstance.value) {
    intradayChartInstance.value.dispose()
  }
  if (capitalFlowChartInstance.value) {
    capitalFlowChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.concept-intraday-data {
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

.concept-info {
  margin-bottom: 20px;
}

.concept-basic {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.concept-title {
  display: flex;
  align-items: center;
  gap: 15px;
}

.concept-title h3 {
  margin: 0;
  color: #303133;
}

.concept-code {
  color: #909399;
  font-size: 14px;
}

.concept-metrics {
  display: flex;
  gap: 30px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.chart-section {
  margin-bottom: 20px;
}

.intraday-chart {
  height: 500px;
}

.realtime-indicators {
  padding: 20px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
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
  color: #303133;
}

.analysis-section {
  margin-bottom: 20px;
}

.capital-flow-chart {
  height: 300px;
}

.capital-flow-summary {
  padding: 15px;
  border-top: 1px solid #f0f0f0;
}

.flow-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.flow-label {
  font-size: 14px;
  color: #606266;
}

.flow-value {
  font-size: 14px;
  font-weight: bold;
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

.leading-stock {
  display: flex;
  flex-direction: column;
}

.stock-name {
  font-size: 12px;
  color: #303133;
}

.stock-change {
  font-size: 11px;
  font-weight: bold;
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