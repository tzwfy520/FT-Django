<template>
  <div class="concept-realtime-data">
    <div class="page-header">
      <h2>概念实时数据</h2>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <div class="market-overview">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon total">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.totalConcepts }}</div>
                <div class="overview-label">概念总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon rise">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value positive">{{ marketOverview.risingCount }}</div>
                <div class="overview-label">上涨</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon fall">
                <el-icon><CaretBottom /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value negative">{{ marketOverview.fallingCount }}</div>
                <div class="overview-label">下跌</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon neutral">
                <el-icon><Minus /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ marketOverview.flatCount }}</div>
                <div class="overview-label">平盘</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon turnover">
                <el-icon><Money /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ formatAmount(marketOverview.totalTurnover) }}</div>
                <div class="overview-label">总成交额(亿)</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon avg">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value" :class="getChangeClass(marketOverview.avgChange)">
                  {{ formatChange(marketOverview.avgChange) }}
                </div>
                <div class="overview-label">平均涨跌</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="data-filters">
      <el-card>
        <div class="filter-row">
          <div class="filter-group">
            <label>排序方式:</label>
            <el-select v-model="sortBy" @change="handleSort">
              <el-option label="涨跌幅" value="changePercent" />
              <el-option label="成交额" value="turnover" />
              <el-option label="总市值" value="marketCap" />
              <el-option label="概念名称" value="name" />
              <el-option label="成份股数" value="stockCount" />
            </el-select>
            <el-select v-model="sortOrder" @change="handleSort">
              <el-option label="降序" value="desc" />
              <el-option label="升序" value="asc" />
            </el-select>
          </div>
          
          <div class="filter-group">
            <label>涨跌幅筛选:</label>
            <el-select v-model="changeFilter" @change="applyFilters">
              <el-option label="全部" value="all" />
              <el-option label="涨幅>5%" value="rise5" />
              <el-option label="涨幅>3%" value="rise3" />
              <el-option label="涨幅>1%" value="rise1" />
              <el-option label="跌幅>1%" value="fall1" />
              <el-option label="跌幅>3%" value="fall3" />
              <el-option label="跌幅>5%" value="fall5" />
            </el-select>
          </div>
          
          <div class="filter-group">
            <label>成交额筛选:</label>
            <el-select v-model="turnoverFilter" @change="applyFilters">
              <el-option label="全部" value="all" />
              <el-option label=">100亿" value="100" />
              <el-option label=">50亿" value="50" />
              <el-option label=">20亿" value="20" />
              <el-option label=">10亿" value="10" />
              <el-option label=">5亿" value="5" />
            </el-select>
          </div>
          
          <div class="filter-group">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索概念名称"
              style="width: 200px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </el-card>
    </div>

    <div class="realtime-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>实时数据 ({{ filteredData.length }}个概念)</span>
            <div class="table-info">
              <span class="update-time">更新时间: {{ updateTime }}</span>
              <el-tag v-if="autoRefresh" type="success" size="small">自动刷新中</el-tag>
            </div>
          </div>
        </template>
        
        <el-table
          :data="paginatedData"
          stripe
          height="600"
          :default-sort="{ prop: 'changePercent', order: 'descending' }"
          @row-click="viewConceptDetail"
        >
          <el-table-column type="index" label="排名" width="60" />
          <el-table-column prop="name" label="概念名称" width="150" fixed="left">
            <template #default="{ row }">
              <div class="concept-name-cell">
                <span class="concept-name">{{ row.name }}</span>
                <span class="concept-code">{{ row.code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100" sortable>
            <template #default="{ row }">
              <span class="change-value" :class="getChangeClass(row.changePercent)">
                {{ formatChange(row.changePercent) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="avgPrice" label="平均价格" width="100">
            <template #default="{ row }">
              <span>{{ row.avgPrice.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stockCount" label="成份股数" width="100" sortable />
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
          <el-table-column prop="turnover" label="成交额" width="120" sortable>
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}亿</span>
            </template>
          </el-table-column>
          <el-table-column prop="marketCap" label="总市值" width="120" sortable>
            <template #default="{ row }">
              <span>{{ formatAmount(row.marketCap) }}亿</span>
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
          <el-table-column prop="peRatio" label="平均市盈率" width="120">
            <template #default="{ row }">
              <span>{{ row.peRatio.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="text" size="small" @click.stop="viewConceptDetail(row)">
                详情
              </el-button>
              <el-button type="text" size="small" @click.stop="addToWatchlist(row)">
                关注
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="filteredData.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 概念详情对话框 -->
    <el-dialog
      v-model="showConceptDetail"
      :title="selectedConcept?.name"
      width="90%"
      top="5vh"
    >
      <div v-if="selectedConcept" class="concept-detail">
        <div class="detail-header">
          <div class="detail-basic">
            <h3>{{ selectedConcept.name }}</h3>
            <span class="detail-code">{{ selectedConcept.code }}</span>
            <div class="detail-change" :class="getChangeClass(selectedConcept.changePercent)">
              {{ formatChange(selectedConcept.changePercent) }}
            </div>
          </div>
          <div class="detail-stats">
            <div class="detail-stat">
              <span class="stat-label">成份股数量</span>
              <span class="stat-value">{{ selectedConcept.stockCount }}只</span>
            </div>
            <div class="detail-stat">
              <span class="stat-label">总市值</span>
              <span class="stat-value">{{ formatAmount(selectedConcept.marketCap) }}亿</span>
            </div>
            <div class="detail-stat">
              <span class="stat-label">成交额</span>
              <span class="stat-value">{{ formatAmount(selectedConcept.turnover) }}亿</span>
            </div>
            <div class="detail-stat">
              <span class="stat-label">平均价格</span>
              <span class="stat-value">{{ selectedConcept.avgPrice.toFixed(2) }}</span>
            </div>
          </div>
        </div>
        
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card title="成份股实时数据">
              <el-table :data="selectedConcept.stocks" stripe max-height="400">
                <el-table-column type="index" label="#" width="50" />
                <el-table-column prop="code" label="代码" width="100" />
                <el-table-column prop="name" label="名称" width="120" />
                <el-table-column prop="price" label="现价" width="100">
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
                <el-table-column prop="turnover" label="成交额" width="120">
                  <template #default="{ row }">
                    <span>{{ formatAmount(row.turnover) }}亿</span>
                  </template>
                </el-table-column>
                <el-table-column prop="volume" label="成交量" width="120">
                  <template #default="{ row }">
                    <span>{{ formatVolume(row.volume) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="marketCap" label="市值" width="120">
                  <template #default="{ row }">
                    <span>{{ formatAmount(row.marketCap) }}亿</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card title="概念统计">
              <div ref="conceptStatsChart" class="concept-stats-chart"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, Refresh, Download, TrendCharts, CaretTop, CaretBottom, 
  Minus, Money, DataAnalysis 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface Stock {
  code: string
  name: string
  price: number
  changePercent: number
  turnover: number
  volume: number
  marketCap: number
}

interface ConceptData {
  code: string
  name: string
  changePercent: number
  avgPrice: number
  stockCount: number
  risingStocks: number
  fallingStocks: number
  turnover: number
  marketCap: number
  leadingStock: {
    name: string
    changePercent: number
  }
  amplitude: number
  turnoverRate: number
  peRatio: number
  stocks: Stock[]
}

const loading = ref(false)
const autoRefresh = ref(false)
const sortBy = ref('changePercent')
const sortOrder = ref('desc')
const changeFilter = ref('all')
const turnoverFilter = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const updateTime = ref('')
const showConceptDetail = ref(false)
const selectedConcept = ref<ConceptData | null>(null)

const conceptStatsChart = ref<HTMLElement>()
const conceptStatsChartInstance = ref<echarts.ECharts>()

let refreshTimer: NodeJS.Timeout | null = null

const marketOverview = ref({
  totalConcepts: 0,
  risingCount: 0,
  fallingCount: 0,
  flatCount: 0,
  totalTurnover: 0,
  avgChange: 0
})

const conceptsData = ref<ConceptData[]>([])

const filteredData = computed(() => {
  let filtered = [...conceptsData.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    filtered = filtered.filter(concept => 
      concept.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      concept.code.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  // 涨跌幅过滤
  if (changeFilter.value !== 'all') {
    switch (changeFilter.value) {
      case 'rise5':
        filtered = filtered.filter(c => c.changePercent > 5)
        break
      case 'rise3':
        filtered = filtered.filter(c => c.changePercent > 3)
        break
      case 'rise1':
        filtered = filtered.filter(c => c.changePercent > 1)
        break
      case 'fall1':
        filtered = filtered.filter(c => c.changePercent < -1)
        break
      case 'fall3':
        filtered = filtered.filter(c => c.changePercent < -3)
        break
      case 'fall5':
        filtered = filtered.filter(c => c.changePercent < -5)
        break
    }
  }
  
  // 成交额过滤
  if (turnoverFilter.value !== 'all') {
    const threshold = Number(turnoverFilter.value)
    filtered = filtered.filter(c => c.turnover > threshold)
  }
  
  // 排序
  filtered.sort((a, b) => {
    let aValue = a[sortBy.value as keyof ConceptData] as number
    let bValue = b[sortBy.value as keyof ConceptData] as number
    
    if (sortBy.value === 'name') {
      return sortOrder.value === 'desc' 
        ? b.name.localeCompare(a.name)
        : a.name.localeCompare(b.name)
    }
    
    return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
  })
  
  return filtered
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const loadRealtimeData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟概念实时数据
    const conceptNames = [
      '人工智能', '新能源汽车', '5G通信', '半导体', '生物医药',
      '新材料', '云计算', '物联网', '区块链', '虚拟现实',
      '工业互联网', '数字货币', '智能制造', '新基建', '碳中和',
      '氢能源', '储能', '光伏', '风电', '核电',
      '军工', '航空航天', '海洋工程', '高端装备', '机器人',
      '基因测序', '细胞治疗', '创新药', '医疗器械', '互联网医疗',
      '在线教育', '数字经济', '智慧城市', '智能交通', '智能家居',
      '网络安全', '数据中心', '边缘计算', '量子通信', '卫星互联网'
    ]
    
    const mockData: ConceptData[] = conceptNames.map((name, index) => {
      const changePercent = (Math.random() - 0.5) * 20 // -10% 到 +10%
      const stockCount = Math.floor(Math.random() * 50) + 10
      const risingStocks = Math.floor(stockCount * (0.3 + Math.random() * 0.4))
      const fallingStocks = stockCount - risingStocks - Math.floor(Math.random() * 5)
      const avgPrice = Math.random() * 100 + 10
      const turnover = Math.random() * 200 + 10
      const marketCap = Math.random() * 5000 + 500
      
      // 生成成份股数据
      const stocks: Stock[] = []
      for (let i = 0; i < Math.min(stockCount, 20); i++) {
        stocks.push({
          code: `${String(Math.floor(Math.random() * 900000) + 100000)}`,
          name: `股票${i + 1}`,
          price: Math.random() * 100 + 10,
          changePercent: (Math.random() - 0.5) * 20,
          turnover: Math.random() * 50 + 1,
          volume: Math.floor(Math.random() * 100000000 + 10000000),
          marketCap: Math.random() * 500 + 50
        })
      }
      
      // 获取领涨股
      const leadingStock = stocks.reduce((prev, current) => 
        prev.changePercent > current.changePercent ? prev : current
      )
      
      return {
        code: `BK${String(index + 1).padStart(4, '0')}`,
        name,
        changePercent: Number(changePercent.toFixed(2)),
        avgPrice: Number(avgPrice.toFixed(2)),
        stockCount,
        risingStocks,
        fallingStocks,
        turnover: Number(turnover.toFixed(2)),
        marketCap: Number(marketCap.toFixed(2)),
        leadingStock: {
          name: leadingStock.name,
          changePercent: leadingStock.changePercent
        },
        amplitude: Number((Math.random() * 10 + 1).toFixed(2)),
        turnoverRate: Number((Math.random() * 5 + 1).toFixed(2)),
        peRatio: Number((Math.random() * 50 + 10).toFixed(2)),
        stocks
      }
    })
    
    conceptsData.value = mockData
    
    // 计算市场概览
    marketOverview.value = {
      totalConcepts: mockData.length,
      risingCount: mockData.filter(c => c.changePercent > 0).length,
      fallingCount: mockData.filter(c => c.changePercent < 0).length,
      flatCount: mockData.filter(c => c.changePercent === 0).length,
      totalTurnover: mockData.reduce((sum, c) => sum + c.turnover, 0),
      avgChange: mockData.reduce((sum, c) => sum + c.changePercent, 0) / mockData.length
    }
    
    updateTime.value = new Date().toLocaleTimeString()
    
    if (!autoRefresh.value) {
      ElMessage.success('实时数据刷新成功')
    }
  } catch (error) {
    ElMessage.error('加载实时数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadRealtimeData()
}

const toggleAutoRefresh = (enabled: boolean) => {
  if (enabled) {
    refreshTimer = setInterval(() => {
      loadRealtimeData()
    }, 30000) // 30秒刷新一次
    ElMessage.success('已开启自动刷新，每30秒更新一次')
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const handleSort = () => {
  currentPage.value = 1
}

const applyFilters = () => {
  currentPage.value = 1
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const viewConceptDetail = (concept: ConceptData) => {
  selectedConcept.value = concept
  showConceptDetail.value = true
  
  nextTick(() => {
    renderConceptStatsChart()
  })
}

const addToWatchlist = (concept: ConceptData) => {
  ElMessage.success(`已添加 ${concept.name} 到关注列表`)
}

const renderConceptStatsChart = () => {
  if (!conceptStatsChart.value || !selectedConcept.value) return
  
  if (!conceptStatsChartInstance.value) {
    conceptStatsChartInstance.value = echarts.init(conceptStatsChart.value)
  }
  
  const concept = selectedConcept.value
  const data = [
    { name: '上涨', value: concept.risingStocks, itemStyle: { color: '#f56c6c' } },
    { name: '下跌', value: concept.fallingStocks, itemStyle: { color: '#67c23a' } },
    { name: '平盘', value: concept.stockCount - concept.risingStocks - concept.fallingStocks, itemStyle: { color: '#909399' } }
  ]
  
  const option = {
    title: {
      text: '成份股涨跌分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '股票数量',
      type: 'pie',
      radius: ['40%', '70%'],
      data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        show: true,
        formatter: '{b}: {c}只'
      }
    }]
  }
  
  conceptStatsChartInstance.value.setOption(option)
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

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadRealtimeData()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (conceptStatsChartInstance.value) {
    conceptStatsChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.concept-realtime-data {
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

.market-overview {
  margin-bottom: 20px;
}

.overview-card {
  height: 100px;
}

.overview-item {
  display: flex;
  align-items: center;
  height: 100%;
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

.overview-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.rise {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-icon.fall {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.overview-icon.neutral {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.overview-icon.turnover {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.overview-icon.avg {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
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

.data-filters {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-group label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.realtime-table {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

.concept-name-cell {
  display: flex;
  flex-direction: column;
}

.concept-name {
  font-weight: bold;
  color: #303133;
}

.concept-code {
  font-size: 12px;
  color: #909399;
}

.change-value {
  font-weight: bold;
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

.concept-detail {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.detail-basic {
  display: flex;
  align-items: center;
  gap: 15px;
}

.detail-basic h3 {
  margin: 0;
  color: #303133;
}

.detail-code {
  color: #909399;
  font-size: 14px;
}

.detail-change {
  font-size: 18px;
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 4px;
  color: white;
}

.detail-stats {
  display: flex;
  gap: 30px;
}

.detail-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.concept-stats-chart {
  height: 300px;
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

.positive.detail-change {
  background-color: #f56c6c;
}

.negative.detail-change {
  background-color: #67c23a;
}

.neutral.detail-change {
  background-color: #909399;
}
</style>