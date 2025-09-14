<template>
  <div class="market-capital-flow">
    <div class="page-header">
      <h2>实时资金流向</h2>
      <div class="header-actions">
        <el-button type="primary" @click="loadCapitalFlow" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
      </div>
    </div>

    <div class="flow-summary">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="flow-card">
            <div class="flow-item">
              <div class="flow-title">主力净流入</div>
              <div class="flow-value positive">+{{ formatAmount(flowData.mainNetInflow) }}</div>
              <div class="flow-ratio positive">占比: {{ flowData.mainRatio }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="flow-card">
            <div class="flow-item">
              <div class="flow-title">超大单净流入</div>
              <div class="flow-value" :class="getFlowClass(flowData.superLargeNetInflow)">{{ formatFlowAmount(flowData.superLargeNetInflow) }}</div>
              <div class="flow-ratio" :class="getFlowClass(flowData.superLargeNetInflow)">占比: {{ flowData.superLargeRatio }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="flow-card">
            <div class="flow-item">
              <div class="flow-title">大单净流入</div>
              <div class="flow-value" :class="getFlowClass(flowData.largeNetInflow)">{{ formatFlowAmount(flowData.largeNetInflow) }}</div>
              <div class="flow-ratio" :class="getFlowClass(flowData.largeNetInflow)">占比: {{ flowData.largeRatio }}%</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="flow-chart">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>资金流向趋势</span>
            <div class="chart-controls">
              <el-radio-group v-model="timeRange" @change="updateChart">
                <el-radio-button label="1d">日内</el-radio-button>
                <el-radio-button label="5d">5日</el-radio-button>
                <el-radio-button label="30d">30日</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="chartContainer" class="chart" style="height: 400px;"></div>
      </el-card>
    </div>

    <div class="flow-details">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>资金流入排行</span>
            </template>
            <el-table :data="inflowRanking" stripe style="width: 100%">
              <el-table-column prop="rank" label="排名" width="60" />
              <el-table-column prop="sector" label="板块" />
              <el-table-column prop="inflow" label="净流入" width="120">
                <template #default="{ row }">
                  <span class="positive">+{{ formatAmount(row.inflow) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="ratio" label="占比" width="80">
                <template #default="{ row }">
                  <span class="positive">{{ row.ratio }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>资金流出排行</span>
            </template>
            <el-table :data="outflowRanking" stripe style="width: 100%">
              <el-table-column prop="rank" label="排名" width="60" />
              <el-table-column prop="sector" label="板块" />
              <el-table-column prop="outflow" label="净流出" width="120">
                <template #default="{ row }">
                  <span class="negative">{{ formatFlowAmount(row.outflow) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="ratio" label="占比" width="80">
                <template #default="{ row }">
                  <span class="negative">{{ row.ratio }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="flow-analysis">
      <el-card>
        <template #header>
          <span>资金流向分析</span>
        </template>
        <div class="analysis-content">
          <div class="analysis-item">
            <h4>市场情绪</h4>
            <el-tag :type="sentimentType" size="large">{{ sentiment }}</el-tag>
            <p>{{ sentimentDescription }}</p>
          </div>
          <div class="analysis-item">
            <h4>主力动向</h4>
            <p>{{ mainForceAnalysis }}</p>
          </div>
          <div class="analysis-item">
            <h4>热点板块</h4>
            <div class="hot-sectors">
              <el-tag v-for="sector in hotSectors" :key="sector" type="success" class="sector-tag">
                {{ sector }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface FlowData {
  mainNetInflow: number
  mainRatio: number
  superLargeNetInflow: number
  superLargeRatio: number
  largeNetInflow: number
  largeRatio: number
}

interface RankingItem {
  rank: number
  sector: string
  inflow?: number
  outflow?: number
  ratio: number
}

const loading = ref(false)
const autoRefresh = ref(false)
const timeRange = ref('1d')
const chartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()
const refreshTimer = ref<NodeJS.Timeout>()

const flowData = ref<FlowData>({
  mainNetInflow: 125.68,
  mainRatio: 8.5,
  superLargeNetInflow: -45.32,
  superLargeRatio: -3.2,
  largeNetInflow: 78.94,
  largeRatio: 5.6
})

const inflowRanking = ref<RankingItem[]>([
  { rank: 1, sector: '新能源汽车', inflow: 45.68, ratio: 12.5 },
  { rank: 2, sector: '人工智能', inflow: 38.92, ratio: 10.8 },
  { rank: 3, sector: '半导体', inflow: 32.15, ratio: 8.9 },
  { rank: 4, sector: '医药生物', inflow: 28.76, ratio: 7.9 },
  { rank: 5, sector: '5G通信', inflow: 24.33, ratio: 6.7 }
])

const outflowRanking = ref<RankingItem[]>([
  { rank: 1, sector: '房地产', outflow: -52.34, ratio: -14.5 },
  { rank: 2, sector: '银行', outflow: -41.28, ratio: -11.4 },
  { rank: 3, sector: '煤炭', outflow: -35.67, ratio: -9.9 },
  { rank: 4, sector: '钢铁', outflow: -29.45, ratio: -8.1 },
  { rank: 5, sector: '有色金属', outflow: -23.89, ratio: -6.6 }
])

const sentiment = ref('偏乐观')
const sentimentType = ref<'success' | 'warning' | 'danger'>('success')
const sentimentDescription = ref('主力资金净流入，市场情绪相对乐观，成长股受到青睐。')
const mainForceAnalysis = ref('主力资金今日净流入125.68亿元，主要集中在科技成长板块，显示机构对新兴产业的看好。超大单资金有所流出，可能存在获利了结行为。')
const hotSectors = ref(['新能源汽车', '人工智能', '半导体', '医药生物'])

const loadCapitalFlow = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 更新数据
    flowData.value = {
      mainNetInflow: Math.random() * 200 - 50,
      mainRatio: Math.random() * 20 - 5,
      superLargeNetInflow: Math.random() * 100 - 50,
      superLargeRatio: Math.random() * 10 - 5,
      largeNetInflow: Math.random() * 150 - 25,
      largeRatio: Math.random() * 15 - 2
    }
    
    await nextTick()
    updateChart()
    
    ElMessage.success('资金流向数据更新成功')
  } catch (error) {
    ElMessage.error('加载资金流向数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartContainer.value) return
  
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  // 生成模拟时间序列数据
  const times: string[] = []
  const mainFlowData: number[] = []
  const superLargeFlowData: number[] = []
  const largeFlowData: number[] = []
  
  const dataPoints = timeRange.value === '1d' ? 24 : timeRange.value === '5d' ? 5 : 30
  
  for (let i = 0; i < dataPoints; i++) {
    if (timeRange.value === '1d') {
      times.push(`${String(9 + Math.floor(i * 7 / 24)).padStart(2, '0')}:${String((i * 15) % 60).padStart(2, '0')}`)
    } else {
      const date = new Date()
      date.setDate(date.getDate() - (dataPoints - 1 - i))
      times.push(date.toISOString().split('T')[0])
    }
    
    mainFlowData.push(Math.random() * 200 - 100)
    superLargeFlowData.push(Math.random() * 100 - 50)
    largeFlowData.push(Math.random() * 150 - 75)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['主力净流入', '超大单净流入', '大单净流入']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: times
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}亿'
      }
    },
    series: [
      {
        name: '主力净流入',
        type: 'line',
        data: mainFlowData,
        smooth: true,
        lineStyle: { color: '#5470c6' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '超大单净流入',
        type: 'line',
        data: superLargeFlowData,
        smooth: true,
        lineStyle: { color: '#91cc75' }
      },
      {
        name: '大单净流入',
        type: 'line',
        data: largeFlowData,
        smooth: true,
        lineStyle: { color: '#fac858' }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
}

const toggleAutoRefresh = (enabled: boolean) => {
  if (enabled) {
    refreshTimer.value = setInterval(() => {
      loadCapitalFlow()
    }, 30000) // 30秒刷新一次
    ElMessage.info('已开启自动刷新，每30秒更新一次')
  } else {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = undefined
    }
    ElMessage.info('已关闭自动刷新')
  }
}

const formatAmount = (amount: number): string => {
  return Math.abs(amount).toFixed(2) + '亿'
}

const formatFlowAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2) + '亿'
}

const getFlowClass = (amount: number): string => {
  return amount > 0 ? 'positive' : amount < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadCapitalFlow()
})

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
})
</script>

<style scoped>
.market-capital-flow {
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

.flow-summary {
  margin-bottom: 20px;
}

.flow-card {
  text-align: center;
}

.flow-item {
  padding: 10px;
}

.flow-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.flow-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.flow-ratio {
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

.flow-chart {
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

.flow-details {
  margin-bottom: 20px;
}

.flow-analysis {
  margin-bottom: 20px;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analysis-item h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.analysis-item p {
  margin: 10px 0;
  color: #606266;
  line-height: 1.6;
}

.hot-sectors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sector-tag {
  margin: 0;
}
</style>