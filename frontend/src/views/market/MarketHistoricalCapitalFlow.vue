<template>
  <div class="market-historical-capital-flow">
    <div class="page-header">
      <h2>历史资金流向</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadHistoricalFlow"
        />
        <el-select v-model="flowType" placeholder="资金类型" @change="loadHistoricalFlow">
          <el-option label="全部资金" value="all" />
          <el-option label="主力资金" value="main" />
          <el-option label="超大单" value="super_large" />
          <el-option label="大单" value="large" />
          <el-option label="中单" value="medium" />
          <el-option label="小单" value="small" />
        </el-select>
        <el-button type="primary" @click="loadHistoricalFlow" :loading="loading">
          <el-icon><Refresh /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <div class="summary-cards">
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

    <div class="flow-trend-chart">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>历史资金流向趋势</span>
            <div class="chart-controls">
              <el-radio-group v-model="chartType" @change="updateChart">
                <el-radio-button label="line">折线图</el-radio-button>
                <el-radio-button label="bar">柱状图</el-radio-button>
                <el-radio-button label="area">面积图</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="chartContainer" class="chart" style="height: 400px;"></div>
      </el-card>
    </div>

    <div class="flow-distribution">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>资金流向分布</span>
            </template>
            <div ref="pieChartContainer" class="chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>净流入统计</span>
            </template>
            <div class="flow-stats">
              <div class="stat-item" v-for="stat in flowStats" :key="stat.type">
                <div class="stat-label">{{ stat.label }}</div>
                <div class="stat-value" :class="getFlowClass(stat.value)">{{ formatFlowAmount(stat.value) }}</div>
                <div class="stat-days">{{ stat.days }}天</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="historical-data-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>历史数据详情</span>
            <el-button size="small" @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </template>
        <el-table
          :data="historicalFlowData"
          v-loading="loading"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'date', order: 'descending' }"
        >
          <el-table-column prop="date" label="日期" width="120" sortable />
          <el-table-column prop="mainFlow" label="主力净流入(亿)" width="130" sortable>
            <template #default="{ row }">
              <span :class="getFlowClass(row.mainFlow)">{{ formatFlowAmount(row.mainFlow) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="superLargeFlow" label="超大单(亿)" width="120" sortable>
            <template #default="{ row }">
              <span :class="getFlowClass(row.superLargeFlow)">{{ formatFlowAmount(row.superLargeFlow) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="largeFlow" label="大单(亿)" width="100" sortable>
            <template #default="{ row }">
              <span :class="getFlowClass(row.largeFlow)">{{ formatFlowAmount(row.largeFlow) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="mediumFlow" label="中单(亿)" width="100" sortable>
            <template #default="{ row }">
              <span :class="getFlowClass(row.mediumFlow)">{{ formatFlowAmount(row.mediumFlow) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="smallFlow" label="小单(亿)" width="100" sortable>
            <template #default="{ row }">
              <span :class="getFlowClass(row.smallFlow)">{{ formatFlowAmount(row.smallFlow) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="totalVolume" label="总成交量(亿手)" width="140">
            <template #default="{ row }">
              {{ (row.totalVolume / 100000000).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="indexChange" label="指数涨跌幅" width="120">
            <template #default="{ row }">
              <span :class="getChangeClass(row.indexChange)">{{ row.indexChange }}%</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="totalRecords"
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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface HistoricalFlowItem {
  date: string
  mainFlow: number
  superLargeFlow: number
  largeFlow: number
  mediumFlow: number
  smallFlow: number
  totalVolume: number
  indexChange: number
}

interface SummaryItem {
  title: string
  value: string
  change: string
  changeClass: string
}

interface FlowStat {
  type: string
  label: string
  value: number
  days: number
}

const loading = ref(false)
const dateRange = ref<[string, string]>(['2024-01-01', '2024-12-31'])
const flowType = ref('all')
const chartType = ref('line')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

const chartContainer = ref<HTMLElement>()
const pieChartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()
const pieChartInstance = ref<echarts.ECharts>()

const historicalFlowData = ref<HistoricalFlowItem[]>([])
const summaryData = ref<SummaryItem[]>([
  { title: '期间净流入', value: '1,256.8亿', change: '+15.2%', changeClass: 'positive' },
  { title: '流入天数', value: '156天', change: '占比65%', changeClass: 'positive' },
  { title: '最大单日流入', value: '89.5亿', change: '2024-03-15', changeClass: 'positive' },
  { title: '最大单日流出', value: '-76.3亿', change: '2024-08-22', changeClass: 'negative' }
])

const flowStats = ref<FlowStat[]>([
  { type: 'main', label: '主力资金', value: 1256.8, days: 156 },
  { type: 'super_large', label: '超大单', value: -234.5, days: 89 },
  { type: 'large', label: '大单', value: 567.3, days: 134 },
  { type: 'medium', label: '中单', value: -345.6, days: 98 },
  { type: 'small', label: '小单', value: -123.4, days: 76 }
])

const loadHistoricalFlow = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    // 生成模拟历史数据
    const mockData: HistoricalFlowItem[] = []
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      if (d.getDay() !== 0 && d.getDay() !== 6) { // 排除周末
        mockData.push({
          date: d.toISOString().split('T')[0],
          mainFlow: (Math.random() - 0.5) * 200,
          superLargeFlow: (Math.random() - 0.5) * 100,
          largeFlow: (Math.random() - 0.5) * 150,
          mediumFlow: (Math.random() - 0.5) * 80,
          smallFlow: (Math.random() - 0.5) * 60,
          totalVolume: Math.random() * 500000000 + 200000000,
          indexChange: (Math.random() - 0.5) * 8
        })
      }
    }
    
    historicalFlowData.value = mockData.reverse()
    totalRecords.value = mockData.length
    
    await nextTick()
    updateChart()
    updatePieChart()
    
    ElMessage.success('历史资金流向数据加载成功')
  } catch (error) {
    ElMessage.error('加载历史资金流向数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartContainer.value || !historicalFlowData.value.length) return
  
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  const dates = historicalFlowData.value.map(item => item.date)
  const mainFlowData = historicalFlowData.value.map(item => item.mainFlow)
  const superLargeFlowData = historicalFlowData.value.map(item => item.superLargeFlow)
  const largeFlowData = historicalFlowData.value.map(item => item.largeFlow)
  
  const series = [
    {
      name: '主力资金',
      type: chartType.value === 'area' ? 'line' : chartType.value,
      data: mainFlowData,
      smooth: true,
      lineStyle: { color: '#5470c6' },
      areaStyle: chartType.value === 'area' ? { opacity: 0.3 } : undefined
    },
    {
      name: '超大单',
      type: chartType.value === 'area' ? 'line' : chartType.value,
      data: superLargeFlowData,
      smooth: true,
      lineStyle: { color: '#91cc75' },
      areaStyle: chartType.value === 'area' ? { opacity: 0.3 } : undefined
    },
    {
      name: '大单',
      type: chartType.value === 'area' ? 'line' : chartType.value,
      data: largeFlowData,
      smooth: true,
      lineStyle: { color: '#fac858' },
      areaStyle: chartType.value === 'area' ? { opacity: 0.3 } : undefined
    }
  ]
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['主力资金', '超大单', '大单']
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
      boundaryGap: chartType.value === 'bar'
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}亿'
      }
    },
    series: series
  }
  
  chartInstance.value.setOption(option)
}

const updatePieChart = () => {
  if (!pieChartContainer.value) return
  
  if (!pieChartInstance.value) {
    pieChartInstance.value = echarts.init(pieChartContainer.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}亿 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '资金流向',
        type: 'pie',
        radius: '50%',
        data: [
          { value: Math.abs(flowStats.value[0].value), name: '主力资金' },
          { value: Math.abs(flowStats.value[1].value), name: '超大单' },
          { value: Math.abs(flowStats.value[2].value), name: '大单' },
          { value: Math.abs(flowStats.value[3].value), name: '中单' },
          { value: Math.abs(flowStats.value[4].value), name: '小单' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  pieChartInstance.value.setOption(option)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadHistoricalFlow()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadHistoricalFlow()
}

const exportData = () => {
  // 模拟导出功能
  ElMessage.success('数据导出功能开发中...')
}

const formatFlowAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2)
}

const getFlowClass = (amount: number): string => {
  return amount > 0 ? 'positive' : amount < 0 ? 'negative' : 'neutral'
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadHistoricalFlow()
})
</script>

<style scoped>
.market-historical-capital-flow {
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

.summary-cards {
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

.flow-trend-chart {
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

.flow-distribution {
  margin-bottom: 20px;
}

.flow-stats {
  padding: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
}

.stat-days {
  font-size: 12px;
  color: #909399;
}

.historical-data-table {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>