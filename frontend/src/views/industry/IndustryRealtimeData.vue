<template>
  <div class="industry-realtime-data">
    <div class="page-header">
      <h2>行业实时数据</h2>
      <div class="header-actions">
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          inactive-text="手动刷新"
          @change="toggleAutoRefresh"
        />
        <el-select v-model="refreshInterval" placeholder="刷新间隔" style="width: 120px;">
          <el-option label="3秒" :value="3" />
          <el-option label="5秒" :value="5" />
          <el-option label="10秒" :value="10" />
          <el-option label="30秒" :value="30" />
        </el-select>
        <el-button type="primary" @click="loadRealtimeData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <div class="market-summary">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-title">上涨行业</div>
              <div class="summary-value positive">{{ marketSummary.risingCount }}</div>
              <div class="summary-subtitle">{{ ((marketSummary.risingCount / marketSummary.totalCount) * 100).toFixed(1) }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-title">下跌行业</div>
              <div class="summary-value negative">{{ marketSummary.fallingCount }}</div>
              <div class="summary-subtitle">{{ ((marketSummary.fallingCount / marketSummary.totalCount) * 100).toFixed(1) }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-title">平盘行业</div>
              <div class="summary-value neutral">{{ marketSummary.flatCount }}</div>
              <div class="summary-subtitle">{{ ((marketSummary.flatCount / marketSummary.totalCount) * 100).toFixed(1) }}%</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-title">总成交额</div>
              <div class="summary-value">{{ formatAmount(marketSummary.totalTurnover) }}</div>
              <div class="summary-subtitle">亿元</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <div class="time-info">
            <div class="current-time">{{ currentTime }}</div>
            <div class="market-status" :class="marketStatus.class">{{ marketStatus.text }}</div>
            <div class="last-update">更新时间: {{ lastUpdateTime }}</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="data-filters">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="sortBy" placeholder="排序字段" @change="sortData">
            <el-option label="涨跌幅" value="changePercent" />
            <el-option label="涨跌额" value="changeAmount" />
            <el-option label="现价" value="currentPrice" />
            <el-option label="成交额" value="turnover" />
            <el-option label="成交量" value="volume" />
            <el-option label="换手率" value="turnoverRate" />
            <el-option label="市值" value="marketCap" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="sortOrder" placeholder="排序方式" @change="sortData">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterType" placeholder="筛选条件" @change="filterData">
            <el-option label="全部" value="all" />
            <el-option label="上涨" value="rising" />
            <el-option label="下跌" value="falling" />
            <el-option label="平盘" value="flat" />
            <el-option label="涨幅>5%" value="strong_rising" />
            <el-option label="跌幅>5%" value="strong_falling" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索行业名称"
            clearable
            @input="filterData"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <div class="realtime-table">
      <el-table
        :data="filteredData"
        stripe
        :height="tableHeight"
        @row-click="viewIndustryDetail"
        row-class-name="clickable-row"
      >
        <el-table-column prop="rank" label="排名" width="60" fixed="left" />
        <el-table-column prop="name" label="行业名称" width="150" fixed="left">
          <template #default="{ row }">
            <div class="industry-name">
              <span class="name-text">{{ row.name }}</span>
              <div class="name-tags">
                <el-tag v-for="tag in row.tags" :key="tag" size="small" :type="getTagType(tag)">
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="currentPrice" label="现价" width="100">
          <template #default="{ row }">
            <span class="price-value">{{ row.currentPrice.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="changeAmount" label="涨跌额" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.changeAmount)">{{ formatChange(row.changeAmount, false) }}</span>
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
            <span>{{ formatAmount(row.turnover) }}亿</span>
          </template>
        </el-table-column>
        <el-table-column prop="turnoverRate" label="换手率" width="100">
          <template #default="{ row }">
            <span>{{ row.turnoverRate.toFixed(2) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="marketCap" label="总市值" width="120">
          <template #default="{ row }">
            <span>{{ formatAmount(row.marketCap) }}亿</span>
          </template>
        </el-table-column>
        <el-table-column prop="pe" label="市盈率" width="80">
          <template #default="{ row }">
            <span>{{ row.pe > 0 ? row.pe.toFixed(2) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pb" label="市净率" width="80">
          <template #default="{ row }">
            <span>{{ row.pb > 0 ? row.pb.toFixed(2) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="leadingStock" label="领涨股" width="150">
          <template #default="{ row }">
            <div class="leading-stock">
              <el-button type="text" size="small" @click.stop="viewStockDetail(row.leadingStock.code)">
                {{ row.leadingStock.name }}
              </el-button>
              <span :class="getChangeClass(row.leadingStock.changePercent)">
                {{ formatChange(row.leadingStock.changePercent) }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="capitalFlow" label="资金流向" width="120">
          <template #default="{ row }">
            <div class="capital-flow">
              <span :class="getChangeClass(row.capitalFlow)">{{ formatAmount(row.capitalFlow) }}亿</span>
              <div class="flow-indicator" :class="getFlowIndicatorClass(row.capitalFlow)"></div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="分时走势" width="120">
          <template #default="{ row }">
            <div class="mini-chart" :ref="el => setChartRef(el, row.code)"></div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="addToWatchlist(row.code)">关注</el-button>
            <el-button size="small" type="primary" @click.stop="viewIndustryDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

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

    <!-- 行业详情对话框 -->
    <el-dialog v-model="detailVisible" :title="selectedIndustry?.name + ' - 实时详情'" width="90%" top="5vh">
      <div v-if="selectedIndustry" class="industry-detail">
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="detail-chart">
              <div ref="detailChartContainer" class="chart" style="height: 400px;"></div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="detail-info">
              <div class="info-section">
                <h4>基本信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">行业代码:</span>
                    <span class="info-value">{{ selectedIndustry.code }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">现价:</span>
                    <span class="info-value">{{ selectedIndustry.currentPrice.toFixed(2) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">涨跌额:</span>
                    <span class="info-value" :class="getChangeClass(selectedIndustry.changeAmount)">
                      {{ formatChange(selectedIndustry.changeAmount, false) }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">涨跌幅:</span>
                    <span class="info-value" :class="getChangeClass(selectedIndustry.changePercent)">
                      {{ formatChange(selectedIndustry.changePercent) }}
                    </span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">成交量:</span>
                    <span class="info-value">{{ formatVolume(selectedIndustry.volume) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">成交额:</span>
                    <span class="info-value">{{ formatAmount(selectedIndustry.turnover) }}亿</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">换手率:</span>
                    <span class="info-value">{{ selectedIndustry.turnoverRate.toFixed(2) }}%</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">总市值:</span>
                    <span class="info-value">{{ formatAmount(selectedIndustry.marketCap) }}亿</span>
                  </div>
                </div>
              </div>
              
              <div class="info-section">
                <h4>资金流向</h4>
                <div class="capital-info">
                  <div class="capital-item">
                    <span class="capital-label">主力净流入:</span>
                    <span class="capital-value" :class="getChangeClass(selectedIndustry.mainCapitalFlow)">
                      {{ formatAmount(selectedIndustry.mainCapitalFlow) }}亿
                    </span>
                  </div>
                  <div class="capital-item">
                    <span class="capital-label">超大单:</span>
                    <span class="capital-value" :class="getChangeClass(selectedIndustry.superLargeFlow)">
                      {{ formatAmount(selectedIndustry.superLargeFlow) }}亿
                    </span>
                  </div>
                  <div class="capital-item">
                    <span class="capital-label">大单:</span>
                    <span class="capital-value" :class="getChangeClass(selectedIndustry.largeFlow)">
                      {{ formatAmount(selectedIndustry.largeFlow) }}亿
                    </span>
                  </div>
                  <div class="capital-item">
                    <span class="capital-label">中小单:</span>
                    <span class="capital-value" :class="getChangeClass(selectedIndustry.smallFlow)">
                      {{ formatAmount(selectedIndustry.smallFlow) }}亿
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="info-section">
                <h4>成份股表现</h4>
                <div class="stock-performance">
                  <div class="performance-item">
                    <span class="performance-label">上涨股票:</span>
                    <span class="performance-value positive">{{ selectedIndustry.risingStocks }}只</span>
                  </div>
                  <div class="performance-item">
                    <span class="performance-label">下跌股票:</span>
                    <span class="performance-value negative">{{ selectedIndustry.fallingStocks }}只</span>
                  </div>
                  <div class="performance-item">
                    <span class="performance-label">平盘股票:</span>
                    <span class="performance-value neutral">{{ selectedIndustry.flatStocks }}只</span>
                  </div>
                  <div class="performance-item">
                    <span class="performance-label">领涨股:</span>
                    <span class="performance-value">
                      <el-button type="text" size="small" @click="viewStockDetail(selectedIndustry.leadingStock.code)">
                        {{ selectedIndustry.leadingStock.name }}
                      </el-button>
                      <span :class="getChangeClass(selectedIndustry.leadingStock.changePercent)">
                        {{ formatChange(selectedIndustry.leadingStock.changePercent) }}
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="addToWatchlist(selectedIndustry?.code)">加入关注</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface IndustryRealtimeData {
  rank: number
  code: string
  name: string
  currentPrice: number
  changeAmount: number
  changePercent: number
  volume: number
  turnover: number
  turnoverRate: number
  marketCap: number
  pe: number
  pb: number
  leadingStock: {
    code: string
    name: string
    changePercent: number
  }
  capitalFlow: number
  mainCapitalFlow: number
  superLargeFlow: number
  largeFlow: number
  smallFlow: number
  risingStocks: number
  fallingStocks: number
  flatStocks: number
  tags: string[]
  trendData: number[]
}

const loading = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(5)
const sortBy = ref('changePercent')
const sortOrder = ref('desc')
const filterType = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)
const tableHeight = ref(600)
const detailVisible = ref(false)
const selectedIndustry = ref<IndustryRealtimeData | null>(null)

const currentTime = ref('')
const lastUpdateTime = ref('')
const marketStatus = ref({ text: '交易中', class: 'trading' })

const detailChartContainer = ref<HTMLElement>()
const detailChartInstance = ref<echarts.ECharts>()
const miniChartRefs = ref<Map<string, HTMLElement>>(new Map())
const miniChartInstances = ref<Map<string, echarts.ECharts>>(new Map())

let refreshTimer: NodeJS.Timeout | null = null

const marketSummary = ref({
  totalCount: 104,
  risingCount: 67,
  fallingCount: 32,
  flatCount: 5,
  totalTurnover: 12580.5
})

const allData = ref<IndustryRealtimeData[]>([])
const filteredData = ref<IndustryRealtimeData[]>([])

const loadRealtimeData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟实时数据
    const mockData: IndustryRealtimeData[] = []
    const industryNames = [
      '银行', '证券', '保险', '房地产', '建筑材料', '钢铁', '有色金属', '煤炭',
      '石油石化', '电力', '公用事业', '交通运输', '汽车', '家电', '食品饮料',
      '纺织服装', '轻工制造', '医药生物', '化工', '电子', '计算机', '通信',
      '传媒', '军工', '机械设备', '电气设备', '建筑装饰', '商业贸易',
      '休闲服务', '农林牧渔', '综合', '非银金融'
    ]
    
    for (let i = 0; i < industryNames.length; i++) {
      const currentPrice = Number((Math.random() * 1000 + 100).toFixed(2))
      const changePercent = Number(((Math.random() - 0.5) * 20).toFixed(2))
      const changeAmount = Number((currentPrice * changePercent / 100).toFixed(2))
      const volume = Math.floor(Math.random() * 1000000000 + 100000000)
      const turnover = Number((Math.random() * 500 + 50).toFixed(2))
      const marketCap = Number((Math.random() * 5000 + 1000).toFixed(2))
      
      const trendData = Array.from({ length: 240 }, (_, index) => {
        const basePrice = currentPrice - changeAmount
        const volatility = Math.sin(index / 20) * 5 + (Math.random() - 0.5) * 10
        return basePrice + volatility
      })
      
      const tags = ['热门', '活跃', '机构重仓', '高分红', '新能源', '科技'].filter(() => Math.random() > 0.7)
      
      mockData.push({
        rank: i + 1,
        code: `BK${String(i + 1).padStart(4, '0')}`,
        name: industryNames[i],
        currentPrice,
        changeAmount,
        changePercent,
        volume,
        turnover,
        turnoverRate: Number((Math.random() * 10 + 1).toFixed(2)),
        marketCap,
        pe: Number((Math.random() * 30 + 10).toFixed(2)),
        pb: Number((Math.random() * 5 + 1).toFixed(2)),
        leadingStock: {
          code: `${String(Math.floor(Math.random() * 999999)).padStart(6, '0')}`,
          name: `${industryNames[i]}龙头`,
          changePercent: Number(((Math.random() - 0.3) * 25).toFixed(2))
        },
        capitalFlow: Number(((Math.random() - 0.5) * 100).toFixed(2)),
        mainCapitalFlow: Number(((Math.random() - 0.5) * 80).toFixed(2)),
        superLargeFlow: Number(((Math.random() - 0.5) * 50).toFixed(2)),
        largeFlow: Number(((Math.random() - 0.5) * 30).toFixed(2)),
        smallFlow: Number(((Math.random() - 0.5) * 20).toFixed(2)),
        risingStocks: Math.floor(Math.random() * 30 + 10),
        fallingStocks: Math.floor(Math.random() * 20 + 5),
        flatStocks: Math.floor(Math.random() * 5 + 1),
        tags,
        trendData
      })
    }
    
    allData.value = mockData
    totalCount.value = mockData.length
    
    // 更新市场概况
    marketSummary.value = {
      totalCount: mockData.length,
      risingCount: mockData.filter(d => d.changePercent > 0).length,
      fallingCount: mockData.filter(d => d.changePercent < 0).length,
      flatCount: mockData.filter(d => d.changePercent === 0).length,
      totalTurnover: mockData.reduce((sum, d) => sum + d.turnover, 0)
    }
    
    sortData()
    updateTime()
    
    await nextTick()
    renderMiniCharts()
    
    ElMessage.success('实时数据更新成功')
  } catch (error) {
    ElMessage.error('加载实时数据失败')
  } finally {
    loading.value = false
  }
}

const sortData = () => {
  const sorted = [...allData.value].sort((a, b) => {
    let aValue = a[sortBy.value as keyof IndustryRealtimeData] as number
    let bValue = b[sortBy.value as keyof IndustryRealtimeData] as number
    
    return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
  })
  
  // 重新分配排名
  sorted.forEach((item, index) => {
    item.rank = index + 1
  })
  
  filterData(sorted)
}

const filterData = (data = allData.value) => {
  let filtered = [...data]
  
  // 按类型筛选
  if (filterType.value !== 'all') {
    switch (filterType.value) {
      case 'rising':
        filtered = filtered.filter(d => d.changePercent > 0)
        break
      case 'falling':
        filtered = filtered.filter(d => d.changePercent < 0)
        break
      case 'flat':
        filtered = filtered.filter(d => d.changePercent === 0)
        break
      case 'strong_rising':
        filtered = filtered.filter(d => d.changePercent > 5)
        break
      case 'strong_falling':
        filtered = filtered.filter(d => d.changePercent < -5)
        break
    }
  }
  
  // 按关键词筛选
  if (searchKeyword.value) {
    filtered = filtered.filter(d => 
      d.name.includes(searchKeyword.value) || 
      d.code.includes(searchKeyword.value)
    )
  }
  
  filteredData.value = filtered
}

const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    loadRealtimeData()
  }, refreshInterval.value * 1000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
  lastUpdateTime.value = now.toLocaleTimeString('zh-CN')
  
  // 判断市场状态
  const hour = now.getHours()
  const minute = now.getMinutes()
  const timeNum = hour * 100 + minute
  
  if ((timeNum >= 930 && timeNum <= 1130) || (timeNum >= 1300 && timeNum <= 1500)) {
    marketStatus.value = { text: '交易中', class: 'trading' }
  } else if (timeNum >= 915 && timeNum < 930) {
    marketStatus.value = { text: '集合竞价', class: 'auction' }
  } else {
    marketStatus.value = { text: '休市', class: 'closed' }
  }
}

const setChartRef = (el: HTMLElement | null, code: string) => {
  if (el) {
    miniChartRefs.value.set(code, el)
  }
}

const renderMiniCharts = () => {
  filteredData.value.forEach(industry => {
    const container = miniChartRefs.value.get(industry.code)
    if (!container) return
    
    let chartInstance = miniChartInstances.value.get(industry.code)
    if (!chartInstance) {
      chartInstance = echarts.init(container)
      miniChartInstances.value.set(industry.code, chartInstance)
    }
    
    const option = {
      grid: {
        left: 0,
        right: 0,
        top: 0,
        bottom: 0
      },
      xAxis: {
        type: 'category',
        show: false,
        data: industry.trendData.map((_, index) => index)
      },
      yAxis: {
        type: 'value',
        show: false,
        scale: true
      },
      series: [{
        type: 'line',
        data: industry.trendData,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: industry.changePercent >= 0 ? '#f56c6c' : '#67c23a'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: industry.changePercent >= 0 ? 'rgba(245, 108, 108, 0.3)' : 'rgba(103, 194, 58, 0.3)'
            }, {
              offset: 1,
              color: industry.changePercent >= 0 ? 'rgba(245, 108, 108, 0.1)' : 'rgba(103, 194, 58, 0.1)'
            }]
          }
        }
      }]
    }
    
    chartInstance.setOption(option)
  })
}

const viewIndustryDetail = (industry: IndustryRealtimeData) => {
  selectedIndustry.value = industry
  detailVisible.value = true
  
  nextTick(() => {
    renderDetailChart()
  })
}

const renderDetailChart = () => {
  if (!detailChartContainer.value || !selectedIndustry.value) return
  
  if (!detailChartInstance.value) {
    detailChartInstance.value = echarts.init(detailChartContainer.value)
  }
  
  const industry = selectedIndustry.value
  const timeData = industry.trendData.map((_, index) => {
    const hour = Math.floor(index / 60) + 9
    const minute = index % 60
    return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`
  })
  
  const option = {
    title: {
      text: `${industry.name} 分时走势`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        return `时间: ${data.name}<br/>价格: ${data.value.toFixed(2)}`
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
      scale: true,
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [{
      type: 'line',
      data: industry.trendData,
      smooth: true,
      symbol: 'none',
      lineStyle: {
        width: 2,
        color: industry.changePercent >= 0 ? '#f56c6c' : '#67c23a'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: industry.changePercent >= 0 ? 'rgba(245, 108, 108, 0.3)' : 'rgba(103, 194, 58, 0.3)'
          }, {
            offset: 1,
            color: industry.changePercent >= 0 ? 'rgba(245, 108, 108, 0.1)' : 'rgba(103, 194, 58, 0.1)'
          }]
        }
      }
    }]
  }
  
  detailChartInstance.value.setOption(option)
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
}

const addToWatchlist = (code: string) => {
  ElMessage.success(`${code} 已加入关注列表`)
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadRealtimeData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadRealtimeData()
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

const getFlowIndicatorClass = (flow: number): string => {
  return flow > 0 ? 'flow-in' : flow < 0 ? 'flow-out' : 'flow-neutral'
}

const getTagType = (tag: string): string => {
  const types: Record<string, string> = {
    '热门': 'danger',
    '活跃': 'warning',
    '机构重仓': 'success',
    '高分红': 'primary',
    '新能源': 'success',
    '科技': 'info'
  }
  return types[tag] || 'info'
}

onMounted(() => {
  loadRealtimeData()
  
  // 启动时间更新
  setInterval(updateTime, 1000)
  
  // 启动自动刷新
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  
  // 清理图表实例
  miniChartInstances.value.forEach(chart => {
    chart.dispose()
  })
  
  if (detailChartInstance.value) {
    detailChartInstance.value.dispose()
  }
})
</script>

<style scoped>
.industry-realtime-data {
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

.market-summary {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
}

.summary-content {
  padding: 15px;
}

.summary-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.summary-subtitle {
  font-size: 12px;
  color: #909399;
}

.time-info {
  text-align: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.current-time {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.market-status {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.market-status.trading {
  color: #f56c6c;
}

.market-status.auction {
  color: #e6a23c;
}

.market-status.closed {
  color: #909399;
}

.last-update {
  font-size: 12px;
  color: #909399;
}

.data-filters {
  margin-bottom: 20px;
}

.realtime-table {
  margin-bottom: 20px;
}

:deep(.clickable-row) {
  cursor: pointer;
}

:deep(.clickable-row:hover) {
  background-color: #f5f7fa;
}

.industry-name {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.name-text {
  font-weight: bold;
  color: #303133;
}

.name-tags {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.price-value {
  font-weight: bold;
  color: #303133;
}

.leading-stock {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.capital-flow {
  display: flex;
  align-items: center;
  gap: 5px;
}

.flow-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.flow-in {
  background-color: #f56c6c;
}

.flow-out {
  background-color: #67c23a;
}

.flow-neutral {
  background-color: #909399;
}

.mini-chart {
  width: 100px;
  height: 40px;
}

.pagination-container {
  text-align: right;
  margin-bottom: 20px;
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

.industry-detail {
  padding: 10px 0;
}

.detail-info {
  padding: 0 10px;
}

.info-section {
  margin-bottom: 20px;
}

.info-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 5px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.info-label {
  color: #606266;
}

.info-value {
  font-weight: bold;
  color: #303133;
}

.capital-info {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.capital-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.capital-label {
  color: #606266;
}

.capital-value {
  font-weight: bold;
}

.stock-performance {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.performance-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.performance-label {
  color: #606266;
}

.performance-value {
  font-weight: bold;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}
</style>