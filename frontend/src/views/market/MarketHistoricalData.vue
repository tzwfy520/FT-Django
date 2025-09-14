<template>
  <div class="market-historical-data">
    <div class="page-header">
      <h2>大盘历史数据</h2>
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
        <el-button type="primary" @click="loadHistoricalData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <div class="data-cards">
      <el-row :gutter="20">
        <el-col :span="6" v-for="(item, index) in summaryData" :key="index">
          <el-card class="summary-card">
            <div class="card-content">
              <div class="card-title">{{ item.title }}</div>
              <div class="card-value" :class="item.changeClass">{{ item.value }}</div>
              <div class="card-change" :class="item.changeClass">{{ item.change }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>历史走势图</span>
            <div class="chart-controls">
              <el-radio-group v-model="chartType" @change="updateChart">
                <el-radio-button label="kline">K线图</el-radio-button>
                <el-radio-button label="line">折线图</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="chartContainer" class="chart" style="height: 400px;"></div>
      </el-card>
    </div>

    <div class="data-table">
      <el-card>
        <template #header>
          <span>历史数据详情</span>
        </template>
        <el-table
          :data="historicalData"
          v-loading="loading"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="open" label="开盘价" width="100" />
          <el-table-column prop="high" label="最高价" width="100" />
          <el-table-column prop="low" label="最低价" width="100" />
          <el-table-column prop="close" label="收盘价" width="100" />
          <el-table-column prop="volume" label="成交量" width="120">
            <template #default="{ row }">
              {{ formatVolume(row.volume) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="成交额" width="120">
            <template #default="{ row }">
              {{ formatAmount(row.amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="change" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.change)">{{ row.change }}%</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface HistoricalDataItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  change: number
}

interface SummaryItem {
  title: string
  value: string
  change: string
  changeClass: string
}

const loading = ref(false)
const dateRange = ref<[string, string]>(['2024-01-01', '2024-12-31'])
const chartType = ref('kline')
const chartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()

const historicalData = ref<HistoricalDataItem[]>([])
const summaryData = ref<SummaryItem[]>([
  { title: '期间最高', value: '3,500.25', change: '+5.2%', changeClass: 'positive' },
  { title: '期间最低', value: '2,850.60', change: '-8.1%', changeClass: 'negative' },
  { title: '期间涨幅', value: '12.5%', change: '+2.3%', changeClass: 'positive' },
  { title: '平均成交量', value: '2.5亿手', change: '+15.6%', changeClass: 'positive' }
])

const loadHistoricalData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟数据
    const mockData: HistoricalDataItem[] = []
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    let currentPrice = 3200
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      if (d.getDay() !== 0 && d.getDay() !== 6) { // 排除周末
        const change = (Math.random() - 0.5) * 6
        const open = currentPrice
        const close = currentPrice + change
        const high = Math.max(open, close) + Math.random() * 20
        const low = Math.min(open, close) - Math.random() * 20
        
        mockData.push({
          date: d.toISOString().split('T')[0],
          open: Number(open.toFixed(2)),
          high: Number(high.toFixed(2)),
          low: Number(low.toFixed(2)),
          close: Number(close.toFixed(2)),
          volume: Math.floor(Math.random() * 500000000),
          amount: Math.floor(Math.random() * 800000000000),
          change: Number(((close - open) / open * 100).toFixed(2))
        })
        
        currentPrice = close
      }
    }
    
    historicalData.value = mockData.reverse()
    await nextTick()
    updateChart()
    
    ElMessage.success('历史数据加载成功')
  } catch (error) {
    ElMessage.error('加载历史数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartContainer.value || !historicalData.value.length) return
  
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  const dates = historicalData.value.map(item => item.date)
  const data = historicalData.value.map(item => [item.open, item.close, item.low, item.high])
  const volumes = historicalData.value.map(item => item.volume)
  
  const option = {
    grid: [{
      left: '10%',
      right: '8%',
      height: '50%'
    }, {
      left: '10%',
      right: '8%',
      top: '70%',
      height: '16%'
    }],
    xAxis: [{
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      min: 'dataMin',
      max: 'dataMax'
    }, {
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
    }],
    yAxis: [{
      scale: true,
      splitArea: { show: true }
    }, {
      scale: true,
      gridIndex: 1,
      splitNumber: 2,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false }
    }],
    series: chartType.value === 'kline' ? [
      {
        name: '大盘指数',
        type: 'candlestick',
        data: data,
        itemStyle: {
          color: '#ec0000',
          color0: '#00da3c',
          borderColor: '#8A0000',
          borderColor0: '#008F28'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes
      }
    ] : [
      {
        name: '收盘价',
        type: 'line',
        data: historicalData.value.map(item => item.close),
        smooth: true,
        lineStyle: { color: '#5470c6' }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿手'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万手'
  }
  return volume.toString() + '手'
}

const formatAmount = (amount: number): string => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿元'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万元'
  }
  return amount.toString() + '元'
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadHistoricalData()
})
</script>

<style scoped>
.market-historical-data {
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

.data-cards {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
}

.card-content {
  padding: 10px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.card-change {
  font-size: 12px;
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

.chart-container {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.data-table {
  margin-bottom: 20px;
}
</style>