<template>
  <div class="margin-trading-data">
    <div class="page-header">
      <h2>两融数据</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadMarginData"
        />
        <el-select v-model="dataType" placeholder="数据类型" @change="loadMarginData">
          <el-option label="融资融券汇总" value="summary" />
          <el-option label="融资明细" value="financing" />
          <el-option label="融券明细" value="securities_lending" />
          <el-option label="标的股票" value="underlying" />
        </el-select>
        <el-button type="primary" @click="loadMarginData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <div class="summary-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-content">
              <div class="card-title">融资余额</div>
              <div class="card-value">{{ summaryData.financingBalance }}亿</div>
              <div class="card-change" :class="getChangeClass(summaryData.financingChange)">{{ formatChange(summaryData.financingChange) }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-content">
              <div class="card-title">融券余额</div>
              <div class="card-value">{{ summaryData.securitiesBalance }}亿</div>
              <div class="card-change" :class="getChangeClass(summaryData.securitiesChange)">{{ formatChange(summaryData.securitiesChange) }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-content">
              <div class="card-title">融资买入额</div>
              <div class="card-value">{{ summaryData.financingBuyAmount }}亿</div>
              <div class="card-change" :class="getChangeClass(summaryData.buyAmountChange)">{{ formatChange(summaryData.buyAmountChange) }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-content">
              <div class="card-title">融券卖出量</div>
              <div class="card-value">{{ summaryData.securitiesSellVolume }}万股</div>
              <div class="card-change" :class="getChangeClass(summaryData.sellVolumeChange)">{{ formatChange(summaryData.sellVolumeChange) }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="trend-chart">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>两融余额趋势</span>
            <div class="chart-controls">
              <el-radio-group v-model="timeRange" @change="updateChart">
                <el-radio-button label="7d">7天</el-radio-button>
                <el-radio-button label="30d">30天</el-radio-button>
                <el-radio-button label="90d">90天</el-radio-button>
                <el-radio-button label="1y">1年</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="chartContainer" class="chart" style="height: 400px;"></div>
      </el-card>
    </div>

    <div class="data-tables">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="table-header">
                <span>融资余额前十</span>
                <el-button size="small" @click="exportFinancingData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </template>
            <el-table :data="financingTop10" stripe size="small">
              <el-table-column prop="rank" label="排名" width="60" />
              <el-table-column prop="stockCode" label="代码" width="80" />
              <el-table-column prop="stockName" label="名称" width="100">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="viewStockDetail(row.stockCode)">{{ row.stockName }}</el-button>
                </template>
              </el-table-column>
              <el-table-column prop="balance" label="余额(万)" width="100" />
              <el-table-column prop="change" label="变动" width="80">
                <template #default="{ row }">
                  <span :class="getChangeClass(row.change)">{{ formatChange(row.change) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="table-header">
                <span>融券余量前十</span>
                <el-button size="small" @click="exportSecuritiesData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </template>
            <el-table :data="securitiesTop10" stripe size="small">
              <el-table-column prop="rank" label="排名" width="60" />
              <el-table-column prop="stockCode" label="代码" width="80" />
              <el-table-column prop="stockName" label="名称" width="100">
                <template #default="{ row }">
                  <el-button type="text" size="small" @click="viewStockDetail(row.stockCode)">{{ row.stockName }}</el-button>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="余量(万股)" width="100" />
              <el-table-column prop="change" label="变动" width="80">
                <template #default="{ row }">
                  <span :class="getChangeClass(row.change)">{{ formatChange(row.change) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="detailed-data">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>两融明细数据</span>
            <div class="table-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索股票代码或名称"
                style="width: 200px;"
                clearable
                @input="filterDetailedData"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button @click="exportAllData">
                <el-icon><Download /></el-icon>
                导出全部
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table
          :data="filteredDetailedData"
          v-loading="loading"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'financingBalance', order: 'descending' }"
        >
          <el-table-column prop="stockCode" label="股票代码" width="100" fixed="left" />
          <el-table-column prop="stockName" label="股票名称" width="120" fixed="left">
            <template #default="{ row }">
              <el-button type="text" @click="viewStockDetail(row.stockCode)">{{ row.stockName }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="closePrice" label="收盘价" width="80" />
          <el-table-column prop="changePercent" label="涨跌幅" width="80">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">{{ row.changePercent }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="financingBalance" label="融资余额(万)" width="120" sortable />
          <el-table-column prop="financingBuyAmount" label="融资买入(万)" width="120" />
          <el-table-column prop="financingRepayAmount" label="融资偿还(万)" width="120" />
          <el-table-column prop="financingNetAmount" label="融资净额(万)" width="120">
            <template #default="{ row }">
              <span :class="getChangeClass(row.financingNetAmount)">{{ formatAmount(row.financingNetAmount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="securitiesBalance" label="融券余量(万股)" width="130" sortable />
          <el-table-column prop="securitiesSellVolume" label="融券卖出(万股)" width="130" />
          <el-table-column prop="securitiesRepayVolume" label="融券偿还(万股)" width="130" />
          <el-table-column prop="securitiesNetVolume" label="融券净量(万股)" width="130">
            <template #default="{ row }">
              <span :class="getChangeClass(row.securitiesNetVolume)">{{ formatAmount(row.securitiesNetVolume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="marginRatio" label="融资融券比" width="100">
            <template #default="{ row }">
              {{ row.marginRatio }}%
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

    <div class="analysis-section">
      <el-card>
        <template #header>
          <span>两融数据分析</span>
        </template>
        <div class="analysis-content">
          <div class="analysis-item">
            <h4>市场情况</h4>
            <p>{{ marketAnalysis }}</p>
          </div>
          <div class="analysis-item">
            <h4>资金流向</h4>
            <p>{{ fundFlowAnalysis }}</p>
          </div>
          <div class="analysis-item">
            <h4>风险提示</h4>
            <p>{{ riskWarning }}</p>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface MarginDetailItem {
  stockCode: string
  stockName: string
  closePrice: number
  changePercent: number
  financingBalance: number
  financingBuyAmount: number
  financingRepayAmount: number
  financingNetAmount: number
  securitiesBalance: number
  securitiesSellVolume: number
  securitiesRepayVolume: number
  securitiesNetVolume: number
  marginRatio: number
}

interface TopItem {
  rank: number
  stockCode: string
  stockName: string
  balance?: number
  volume?: number
  change: number
}

const loading = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const dataType = ref('summary')
const timeRange = ref('30d')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

const chartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()

const summaryData = ref({
  financingBalance: 8956.78,
  financingChange: 2.35,
  securitiesBalance: 156.89,
  securitiesChange: -1.24,
  financingBuyAmount: 234.56,
  buyAmountChange: 5.67,
  securitiesSellVolume: 1234.56,
  sellVolumeChange: -3.45
})

const financingTop10 = ref<TopItem[]>([
  { rank: 1, stockCode: '000001', stockName: '平安银行', balance: 125680, change: 2.35 },
  { rank: 2, stockCode: '000002', stockName: '万科A', balance: 98750, change: -1.24 },
  { rank: 3, stockCode: '000858', stockName: '五粮液', balance: 87650, change: 3.45 },
  { rank: 4, stockCode: '002415', stockName: '海康威视', balance: 76540, change: 1.89 },
  { rank: 5, stockCode: '600036', stockName: '招商银行', balance: 65430, change: -0.67 }
])

const securitiesTop10 = ref<TopItem[]>([
  { rank: 1, stockCode: '000001', stockName: '平安银行', volume: 12568, change: 5.67 },
  { rank: 2, stockCode: '000002', stockName: '万科A', volume: 9875, change: -2.34 },
  { rank: 3, stockCode: '000858', stockName: '五粮液', volume: 8765, change: 7.89 },
  { rank: 4, stockCode: '002415', stockName: '海康威视', volume: 7654, change: -1.23 },
  { rank: 5, stockCode: '600036', stockName: '招商银行', volume: 6543, change: 3.45 }
])

const detailedData = ref<MarginDetailItem[]>([])
const filteredDetailedData = ref<MarginDetailItem[]>([])

const marketAnalysis = ref('当前两融余额总体保持稳定增长态势，融资余额较前一交易日增加2.35%，显示投资者对市场信心有所提升。融券余额小幅下降1.24%，表明做空情绪有所缓解。')
const fundFlowAnalysis = ref('融资资金主要流入科技、金融等板块，其中平安银行、万科A等权重股获得较多融资买入。融券方面，部分高估值股票出现融券增加，投资者对估值过高的股票保持谨慎态度。')
const riskWarning = ref('请注意两融交易的杠杆风险，合理控制仓位。当前市场波动较大，建议投资者根据自身风险承受能力进行操作，避免过度杠杆。')

const loadMarginData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟详细数据
    const mockData: MarginDetailItem[] = []
    for (let i = 0; i < 200; i++) {
      const changePercent = (Math.random() - 0.5) * 20
      const financingBalance = Math.random() * 100000 + 10000
      const securitiesBalance = Math.random() * 10000 + 1000
      
      mockData.push({
        stockCode: `${String(i + 1).padStart(6, '0')}`,
        stockName: `股票${i + 1}`,
        closePrice: Number((Math.random() * 100 + 10).toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        financingBalance: Number(financingBalance.toFixed(2)),
        financingBuyAmount: Number((Math.random() * 5000 + 500).toFixed(2)),
        financingRepayAmount: Number((Math.random() * 4000 + 400).toFixed(2)),
        financingNetAmount: Number(((Math.random() - 0.5) * 2000).toFixed(2)),
        securitiesBalance: Number(securitiesBalance.toFixed(2)),
        securitiesSellVolume: Number((Math.random() * 1000 + 100).toFixed(2)),
        securitiesRepayVolume: Number((Math.random() * 800 + 80).toFixed(2)),
        securitiesNetVolume: Number(((Math.random() - 0.5) * 400).toFixed(2)),
        marginRatio: Number((Math.random() * 50 + 10).toFixed(2))
      })
    }
    
    detailedData.value = mockData
    filteredDetailedData.value = mockData
    totalRecords.value = mockData.length
    
    await nextTick()
    updateChart()
    
    ElMessage.success('两融数据加载成功')
  } catch (error) {
    ElMessage.error('加载两融数据失败')
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
  const dates: string[] = []
  const financingData: number[] = []
  const securitiesData: number[] = []
  
  const days = timeRange.value === '7d' ? 7 : timeRange.value === '30d' ? 30 : timeRange.value === '90d' ? 90 : 365
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
    
    financingData.push(8900 + Math.random() * 200 - 100)
    securitiesData.push(150 + Math.random() * 20 - 10)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['融资余额', '融券余额']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '融资余额(亿)',
        position: 'left',
        axisLabel: {
          formatter: '{value}亿'
        }
      },
      {
        type: 'value',
        name: '融券余额(亿)',
        position: 'right',
        axisLabel: {
          formatter: '{value}亿'
        }
      }
    ],
    series: [
      {
        name: '融资余额',
        type: 'line',
        yAxisIndex: 0,
        data: financingData,
        smooth: true,
        lineStyle: { color: '#5470c6' },
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '融券余额',
        type: 'line',
        yAxisIndex: 1,
        data: securitiesData,
        smooth: true,
        lineStyle: { color: '#91cc75' }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
}

const filterDetailedData = () => {
  if (!searchKeyword.value) {
    filteredDetailedData.value = detailedData.value
  } else {
    filteredDetailedData.value = detailedData.value.filter(item => 
      item.stockCode.includes(searchKeyword.value) || 
      item.stockName.includes(searchKeyword.value)
    )
  }
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadMarginData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadMarginData()
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
}

const exportFinancingData = () => {
  ElMessage.success('融资数据导出功能开发中...')
}

const exportSecuritiesData = () => {
  ElMessage.success('融券数据导出功能开发中...')
}

const exportAllData = () => {
  ElMessage.success('全部数据导出功能开发中...')
}

const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : ''
  return sign + change.toFixed(2) + '%'
}

const formatAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2)
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadMarginData()
})
</script>

<style scoped>
.margin-trading-data {
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

.summary-overview {
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
  color: #303133;
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

.trend-chart {
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

.data-tables {
  margin-bottom: 20px;
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

.detailed-data {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.analysis-section {
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
  margin: 0;
  color: #606266;
  line-height: 1.6;
}
</style>