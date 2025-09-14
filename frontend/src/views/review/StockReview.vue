<template>
  <div class="stock-review">
    <div class="page-header">
      <h2>自选股票复盘</h2>
      <div class="header-actions">
        <div class="review-status">
          <el-tag :type="reviewStatus.type" size="large">
            <el-icon><Clock /></el-icon>
            {{ reviewStatus.text }}
          </el-tag>
        </div>
        <el-button @click="startReview" :loading="reviewing" type="primary">
          <el-icon><Refresh /></el-icon>
          开始复盘
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 复盘概览 -->
    <div class="review-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon positive">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overviewData.totalStocks }}</div>
                <div class="overview-label">自选股票数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon" :class="overviewData.riseCount > overviewData.fallCount ? 'positive' : 'negative'">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overviewData.riseCount }}/{{ overviewData.fallCount }}</div>
                <div class="overview-label">涨跌家数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon" :class="overviewData.avgReturn >= 0 ? 'positive' : 'negative'">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatPercent(overviewData.avgReturn) }}</div>
                <div class="overview-label">平均收益率</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon warning">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overviewData.alertCount }}</div>
                <div class="overview-label">预警股票</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和排序 -->
    <div class="filter-section">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="4">
            <el-select v-model="filterType" placeholder="筛选类型" @change="applyFilter">
              <el-option label="全部" value="all" />
              <el-option label="上涨" value="rise" />
              <el-option label="下跌" value="fall" />
              <el-option label="涨停" value="limit_up" />
              <el-option label="跌停" value="limit_down" />
              <el-option label="异动" value="abnormal" />
              <el-option label="预警" value="alert" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="sortBy" placeholder="排序方式" @change="applySorting">
              <el-option label="涨跌幅" value="change_percent" />
              <el-option label="成交量" value="volume" />
              <el-option label="成交额" value="turnover" />
              <el-option label="换手率" value="turnover_rate" />
              <el-option label="振幅" value="amplitude" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="sortOrder" placeholder="排序顺序" @change="applySorting">
              <el-option label="降序" value="desc" />
              <el-option label="升序" value="asc" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索股票"
              @input="applyFilter"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button @click="showAnalysisDialog = true">
              <el-icon><DataAnalysis /></el-icon>
              综合分析
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <el-card>
        <template #header>
          <div class="list-header">
            <span>自选股票复盘 ({{ filteredStocks.length }})</span>
            <div class="list-actions">
              <el-button size="small" @click="selectAll">
                全选
              </el-button>
              <el-button size="small" @click="batchAnalysis" :disabled="selectedStocks.length === 0">
                批量分析
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedStocks" 
          stripe 
          @selection-change="handleSelectionChange"
          @row-click="showStockDetail"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120">
            <template #default="{ row }">
              <div class="stock-name">
                <span>{{ row.name }}</span>
                <el-tag v-if="row.isLimitUp" type="danger" size="small">涨停</el-tag>
                <el-tag v-else-if="row.isLimitDown" type="success" size="small">跌停</el-tag>
                <el-tag v-if="row.hasAlert" type="warning" size="small">预警</el-tag>
              </div>
            </template>
          </el-table-column>
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
                {{ formatPercent(row.changePercent) }}
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
          <el-table-column prop="turnoverRate" label="换手率" width="100">
            <template #default="{ row }">
              <span>{{ row.turnoverRate.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="100">
            <template #default="{ row }">
              <span>{{ row.amplitude.toFixed(2) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="reviewScore" label="复盘评分" width="120">
            <template #default="{ row }">
              <div class="review-score">
                <el-rate
                  v-model="row.reviewScore"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}"
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click.stop="showStockDetail(row)">
                详情
              </el-button>
              <el-button size="small" @click.stop="showAnalysis(row)">
                分析
              </el-button>
              <el-button size="small" type="danger" @click.stop="removeFromWatchlist(row)">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredStocks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 股票详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`${selectedStock?.name} (${selectedStock?.code}) 复盘详情`"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedStock" class="stock-detail">
        <!-- 基本信息 -->
        <el-row :gutter="20" class="detail-info">
          <el-col :span="8">
            <div class="detail-card">
              <h4>基本信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">现价:</span>
                  <span class="info-value" :class="getPriceClass(selectedStock.changePercent)">
                    {{ selectedStock.currentPrice.toFixed(2) }}
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">涨跌幅:</span>
                  <span class="info-value" :class="getChangeClass(selectedStock.changePercent)">
                    {{ formatPercent(selectedStock.changePercent) }}
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">成交量:</span>
                  <span class="info-value">{{ formatVolume(selectedStock.volume) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">换手率:</span>
                  <span class="info-value">{{ selectedStock.turnoverRate.toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-card">
              <h4>技术指标</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">RSI:</span>
                  <span class="info-value">{{ selectedStock.rsi.toFixed(2) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">MACD:</span>
                  <span class="info-value" :class="getChangeClass(selectedStock.macd)">
                    {{ selectedStock.macd.toFixed(4) }}
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">KDJ-K:</span>
                  <span class="info-value">{{ selectedStock.kdj.k.toFixed(2) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">KDJ-D:</span>
                  <span class="info-value">{{ selectedStock.kdj.d.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-card">
              <h4>复盘评价</h4>
              <div class="review-evaluation">
                <div class="score-item">
                  <span>综合评分:</span>
                  <el-rate v-model="selectedStock.reviewScore" disabled show-score />
                </div>
                <div class="recommendation">
                  <span>操作建议:</span>
                  <el-tag :type="getRecommendationType(selectedStock.recommendation)">
                    {{ selectedStock.recommendation }}
                  </el-tag>
                </div>
                <div class="risk-level">
                  <span>风险等级:</span>
                  <el-tag :type="getRiskType(selectedStock.riskLevel)">
                    {{ selectedStock.riskLevel }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 图表分析 -->
        <div class="chart-analysis">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="K线图" name="kline">
              <div ref="klineChart" class="chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="成交量" name="volume">
              <div ref="volumeChart" class="chart-container"></div>
            </el-tab-pane>
            <el-tab-pane label="技术指标" name="indicators">
              <div ref="indicatorChart" class="chart-container"></div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 复盘分析 -->
        <div class="review-analysis">
          <h4>复盘分析</h4>
          <el-card>
            <div class="analysis-content">
              <div class="analysis-section">
                <h5>今日表现</h5>
                <p>{{ selectedStock.todayAnalysis }}</p>
              </div>
              <div class="analysis-section">
                <h5>技术分析</h5>
                <p>{{ selectedStock.technicalAnalysis }}</p>
              </div>
              <div class="analysis-section">
                <h5>资金分析</h5>
                <p>{{ selectedStock.fundAnalysis }}</p>
              </div>
              <div class="analysis-section">
                <h5>后市展望</h5>
                <p>{{ selectedStock.outlook }}</p>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>

    <!-- 综合分析对话框 -->
    <el-dialog
      v-model="showAnalysisDialog"
      title="综合分析报告"
      width="70%"
      top="5vh"
    >
      <div class="comprehensive-analysis">
        <!-- 市场概况 -->
        <div class="market-summary">
          <h4>市场概况</h4>
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="marketChart" class="chart-container-small"></div>
            </el-col>
            <el-col :span="12">
              <div class="market-stats">
                <div class="stat-item">
                  <span class="stat-label">上涨股票:</span>
                  <span class="stat-value positive">{{ overviewData.riseCount }}只</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">下跌股票:</span>
                  <span class="stat-value negative">{{ overviewData.fallCount }}只</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均收益:</span>
                  <span class="stat-value" :class="getChangeClass(overviewData.avgReturn)">
                    {{ formatPercent(overviewData.avgReturn) }}
                  </span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">最佳表现:</span>
                  <span class="stat-value positive">{{ overviewData.bestStock }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">最差表现:</span>
                  <span class="stat-value negative">{{ overviewData.worstStock }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 行业分布 -->
        <div class="industry-analysis">
          <h4>行业分布</h4>
          <div ref="industryChart" class="chart-container-small"></div>
        </div>
        
        <!-- 操作建议 -->
        <div class="recommendations">
          <h4>操作建议</h4>
          <el-table :data="recommendationData" stripe>
            <el-table-column prop="type" label="建议类型" width="120" />
            <el-table-column prop="stocks" label="股票列表" />
            <el-table-column prop="reason" label="理由" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Clock, Refresh, Download, TrendCharts, CaretTop, 
  DataAnalysis, Warning, Search 
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
  amplitude: number
  pe: number
  pb: number
  isLimitUp: boolean
  isLimitDown: boolean
  hasAlert: boolean
  reviewScore: number
  recommendation: string
  riskLevel: string
  rsi: number
  macd: number
  kdj: {
    k: number
    d: number
    j: number
  }
  todayAnalysis: string
  technicalAnalysis: string
  fundAnalysis: string
  outlook: string
  industry: string
}

interface OverviewData {
  totalStocks: number
  riseCount: number
  fallCount: number
  avgReturn: number
  alertCount: number
  bestStock: string
  worstStock: string
}

interface RecommendationItem {
  type: string
  stocks: string
  reason: string
}

const reviewing = ref(false)
const showDetailDialog = ref(false)
const showAnalysisDialog = ref(false)
const selectedStock = ref<Stock | null>(null)
const selectedStocks = ref<Stock[]>([])
const activeTab = ref('kline')

const filterType = ref('all')
const sortBy = ref('change_percent')
const sortOrder = ref('desc')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const klineChart = ref<HTMLElement>()
const volumeChart = ref<HTMLElement>()
const indicatorChart = ref<HTMLElement>()
const marketChart = ref<HTMLElement>()
const industryChart = ref<HTMLElement>()

const reviewStatus = ref({
  type: 'success' as const,
  text: '复盘完成 16:30'
})

const overviewData = ref<OverviewData>({
  totalStocks: 0,
  riseCount: 0,
  fallCount: 0,
  avgReturn: 0,
  alertCount: 0,
  bestStock: '',
  worstStock: ''
})

const stockList = ref<Stock[]>([])

const recommendationData = ref<RecommendationItem[]>([
  { type: '买入', stocks: '平安银行、招商银行', reason: '技术指标向好，资金流入明显' },
  { type: '持有', stocks: '五粮液、贵州茅台', reason: '基本面稳定，短期调整后有望反弹' },
  { type: '减仓', stocks: '万科A', reason: '成交量萎缩，技术面走弱' },
  { type: '观望', stocks: '中国平安', reason: '震荡整理中，等待明确方向' }
])

// 计算属性
const filteredStocks = computed(() => {
  let result = [...stockList.value]
  
  // 筛选
  if (filterType.value !== 'all') {
    result = result.filter(stock => {
      switch (filterType.value) {
        case 'rise':
          return stock.changePercent > 0
        case 'fall':
          return stock.changePercent < 0
        case 'limit_up':
          return stock.isLimitUp
        case 'limit_down':
          return stock.isLimitDown
        case 'abnormal':
          return stock.amplitude > 5
        case 'alert':
          return stock.hasAlert
        default:
          return true
      }
    })
  }
  
  // 搜索
  if (searchKeyword.value) {
    result = result.filter(stock => 
      stock.code.includes(searchKeyword.value) || 
      stock.name.includes(searchKeyword.value)
    )
  }
  
  // 排序
  result.sort((a, b) => {
    let aValue = a[sortBy.value as keyof Stock] as number
    let bValue = b[sortBy.value as keyof Stock] as number
    
    if (sortOrder.value === 'desc') {
      return bValue - aValue
    } else {
      return aValue - bValue
    }
  })
  
  return result
})

const paginatedStocks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStocks.value.slice(start, end)
})

// 生成模拟数据
const generateMockData = () => {
  const stockCodes = [
    { code: '000001', name: '平安银行', industry: '银行' },
    { code: '000002', name: '万科A', industry: '房地产' },
    { code: '000858', name: '五粮液', industry: '食品饮料' },
    { code: '600036', name: '招商银行', industry: '银行' },
    { code: '600519', name: '贵州茅台', industry: '食品饮料' },
    { code: '000063', name: '中兴通讯', industry: '通信' },
    { code: '002415', name: '海康威视', industry: '电子' },
    { code: '300059', name: '东方财富', industry: '非银金融' },
    { code: '600887', name: '伊利股份', industry: '食品饮料' },
    { code: '000725', name: '京东方A', industry: '电子' }
  ]
  
  const recommendations = ['买入', '持有', '减仓', '观望']
  const riskLevels = ['低风险', '中风险', '高风险']
  
  const stocks: Stock[] = stockCodes.map(item => {
    const basePrice = Math.random() * 100 + 10
    const changePercent = (Math.random() - 0.5) * 10
    const changeAmount = (basePrice * changePercent) / 100
    const currentPrice = basePrice + changeAmount
    
    return {
      code: item.code,
      name: item.name,
      industry: item.industry,
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
      amplitude: Math.random() * 10,
      pe: Math.random() * 50 + 5,
      pb: Math.random() * 5 + 0.5,
      isLimitUp: Math.random() < 0.05,
      isLimitDown: Math.random() < 0.05,
      hasAlert: Math.random() < 0.2,
      reviewScore: Math.floor(Math.random() * 5) + 1,
      recommendation: recommendations[Math.floor(Math.random() * recommendations.length)],
      riskLevel: riskLevels[Math.floor(Math.random() * riskLevels.length)],
      rsi: Math.random() * 100,
      macd: (Math.random() - 0.5) * 2,
      kdj: {
        k: Math.random() * 100,
        d: Math.random() * 100,
        j: Math.random() * 100
      },
      todayAnalysis: `${item.name}今日${changePercent >= 0 ? '上涨' : '下跌'}${Math.abs(changePercent).toFixed(2)}%，成交量${Math.random() > 0.5 ? '放大' : '缩小'}，资金${Math.random() > 0.5 ? '净流入' : '净流出'}。`,
      technicalAnalysis: `技术面上，RSI指标为${Math.random() * 100}，MACD${Math.random() > 0.5 ? '金叉' : '死叉'}，KDJ指标${Math.random() > 0.5 ? '向上' : '向下'}发散。`,
      fundAnalysis: `资金面上，主力资金${Math.random() > 0.5 ? '净流入' : '净流出'}${Math.floor(Math.random() * 10000)}万元，散户资金${Math.random() > 0.5 ? '跟进' : '观望'}。`,
      outlook: `后市展望：基于当前技术面和资金面分析，建议${recommendations[Math.floor(Math.random() * recommendations.length)]}操作。`
    }
  })
  
  stockList.value = stocks
  
  // 更新概览数据
  const riseCount = stocks.filter(s => s.changePercent > 0).length
  const fallCount = stocks.filter(s => s.changePercent < 0).length
  const avgReturn = stocks.reduce((sum, s) => sum + s.changePercent, 0) / stocks.length
  const alertCount = stocks.filter(s => s.hasAlert).length
  
  const bestStock = stocks.reduce((best, current) => 
    current.changePercent > best.changePercent ? current : best
  )
  const worstStock = stocks.reduce((worst, current) => 
    current.changePercent < worst.changePercent ? current : worst
  )
  
  overviewData.value = {
    totalStocks: stocks.length,
    riseCount,
    fallCount,
    avgReturn,
    alertCount,
    bestStock: `${bestStock.name}(+${bestStock.changePercent.toFixed(2)}%)`,
    worstStock: `${worstStock.name}(${worstStock.changePercent.toFixed(2)}%)`
  }
}

const startReview = async () => {
  reviewing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    generateMockData()
    ElMessage.success('复盘完成')
    reviewStatus.value = {
      type: 'success',
      text: `复盘完成 ${new Date().toLocaleTimeString()}`
    }
  } catch (error) {
    ElMessage.error('复盘失败')
  } finally {
    reviewing.value = false
  }
}

const refreshData = () => {
  generateMockData()
  ElMessage.success('数据已刷新')
}

const applyFilter = () => {
  currentPage.value = 1
}

const applySorting = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection: Stock[]) => {
  selectedStocks.value = selection
}

const selectAll = () => {
  // 这里应该调用表格的全选方法
  ElMessage.info('全选功能需要表格组件支持')
}

const batchAnalysis = () => {
  ElMessage.success(`已选择${selectedStocks.value.length}只股票进行批量分析`)
}

const showStockDetail = (stock: Stock) => {
  selectedStock.value = stock
  showDetailDialog.value = true
  
  nextTick(() => {
    initDetailCharts()
  })
}

const showAnalysis = (stock: Stock) => {
  ElMessage.info(`显示${stock.name}的详细分析`)
}

const removeFromWatchlist = async (stock: Stock) => {
  try {
    await ElMessageBox.confirm(
      `确定要从自选中移除 ${stock.name} 吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = stockList.value.findIndex(s => s.code === stock.code)
    if (index >= 0) {
      stockList.value.splice(index, 1)
      ElMessage.success('已移除')
    }
  } catch {
    // 用户取消
  }
}

const exportReport = () => {
  ElMessage.success('复盘报告导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const initDetailCharts = () => {
  if (!selectedStock.value) return
  
  // K线图
  if (klineChart.value) {
    const chart = echarts.init(klineChart.value)
    // 这里应该实现K线图的配置
    chart.setOption({
      title: { text: 'K线图' },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'candlestick', data: [] }]
    })
  }
  
  // 成交量图
  if (volumeChart.value) {
    const chart = echarts.init(volumeChart.value)
    chart.setOption({
      title: { text: '成交量' },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [] }]
    })
  }
  
  // 技术指标图
  if (indicatorChart.value) {
    const chart = echarts.init(indicatorChart.value)
    chart.setOption({
      title: { text: '技术指标' },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: [
        { name: 'RSI', type: 'line', data: [] },
        { name: 'MACD', type: 'line', data: [] }
      ]
    })
  }
}

const initAnalysisCharts = () => {
  // 市场分布图
  if (marketChart.value) {
    const chart = echarts.init(marketChart.value)
    chart.setOption({
      title: { text: '涨跌分布' },
      series: [{
        type: 'pie',
        data: [
          { name: '上涨', value: overviewData.value.riseCount },
          { name: '下跌', value: overviewData.value.fallCount }
        ]
      }]
    })
  }
  
  // 行业分布图
  if (industryChart.value) {
    const chart = echarts.init(industryChart.value)
    const industryData = stockList.value.reduce((acc, stock) => {
      acc[stock.industry] = (acc[stock.industry] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    chart.setOption({
      title: { text: '行业分布' },
      series: [{
        type: 'pie',
        data: Object.entries(industryData).map(([name, value]) => ({ name, value }))
      }]
    })
  }
}

const formatPercent = (value: number): string => {
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(2) + '%'
}

const formatChangeAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2)
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatAmount = (amount: number): string => {
  return Math.abs(amount).toFixed(2)
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getPriceClass = (change: number): string => {
  return change > 0 ? 'price-up' : change < 0 ? 'price-down' : 'price-flat'
}

const getRecommendationType = (recommendation: string): string => {
  const typeMap: Record<string, string> = {
    '买入': 'success',
    '持有': 'info',
    '减仓': 'warning',
    '观望': 'info'
  }
  return typeMap[recommendation] || 'info'
}

const getRiskType = (riskLevel: string): string => {
  const typeMap: Record<string, string> = {
    '低风险': 'success',
    '中风险': 'warning',
    '高风险': 'danger'
  }
  return typeMap[riskLevel] || 'info'
}

onMounted(() => {
  generateMockData()
  
  // 检查复盘状态
  const now = new Date()
  const hour = now.getHours()
  
  if (hour >= 16) {
    reviewStatus.value = {
      type: 'success',
      text: '可以开始复盘'
    }
  } else {
    reviewStatus.value = {
      type: 'warning',
      text: `等待收盘 (${16 - hour}小时后)`
    }
  }
})
</script>

<style scoped>
.stock-review {
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

.review-overview {
  margin-bottom: 20px;
}

.overview-card {
  height: 100px;
}

.overview-item {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.overview-icon {
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

.overview-icon.positive {
  background: linear-gradient(135deg, #f56c6c, #ff8a80);
}

.overview-icon.negative {
  background: linear-gradient(135deg, #67c23a, #81c784);
}

.overview-icon.warning {
  background: linear-gradient(135deg, #e6a23c, #ffb74d);
}

.overview-content {
  flex: 1;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: #909399;
}

.filter-section {
  margin-bottom: 20px;
}

.stock-list {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-actions {
  display: flex;
  gap: 10px;
}

.stock-name {
  display: flex;
  align-items: center;
  gap: 5px;
}

.review-score {
  display: flex;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.stock-detail {
  padding: 20px 0;
}

.detail-info {
  margin-bottom: 30px;
}

.detail-card {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  height: 100%;
}

.detail-card h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-label {
  font-size: 14px;
  color: #606266;
}

.info-value {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.review-evaluation {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.score-item,
.recommendation,
.risk-level {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-analysis {
  margin-bottom: 30px;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.chart-container-small {
  height: 300px;
  width: 100%;
}

.review-analysis h4 {
  margin-bottom: 15px;
  color: #303133;
}

.analysis-content {
  padding: 20px;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h5 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 14px;
}

.analysis-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.comprehensive-analysis {
  padding: 20px 0;
}

.market-summary,
.industry-analysis,
.recommendations {
  margin-bottom: 30px;
}

.market-summary h4,
.industry-analysis h4,
.recommendations h4 {
  margin-bottom: 15px;
  color: #303133;
}

.market-stats {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 14px;
  font-weight: bold;
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