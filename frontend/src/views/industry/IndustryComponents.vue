<template>
  <div class="industry-components">
    <div class="page-header">
      <h2>行业板块成份</h2>
      <div class="header-actions">
        <el-select v-model="sortBy" placeholder="排序方式" @change="sortIndustries">
          <el-option label="涨跌幅" value="changePercent" />
          <el-option label="成交额" value="turnover" />
          <el-option label="市值" value="marketCap" />
          <el-option label="名称" value="name" />
        </el-select>
        <el-select v-model="sortOrder" placeholder="排序顺序" @change="sortIndustries">
          <el-option label="降序" value="desc" />
          <el-option label="升序" value="asc" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索行业板块"
          style="width: 200px;"
          clearable
          @input="filterIndustries"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="loadIndustryData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="market-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">行业总数</div>
              <div class="card-value">{{ overviewData.totalIndustries }}</div>
              <div class="card-subtitle">个行业板块</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">上涨行业</div>
              <div class="card-value positive">{{ overviewData.risingIndustries }}</div>
              <div class="card-subtitle">个行业上涨</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">下跌行业</div>
              <div class="card-value negative">{{ overviewData.fallingIndustries }}</div>
              <div class="card-subtitle">个行业下跌</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">平盘行业</div>
              <div class="card-value neutral">{{ overviewData.flatIndustries }}</div>
              <div class="card-subtitle">个行业平盘</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="performance-chart">
      <el-card>
        <template #header>
          <div class="chart-header">
            <span>行业表现分布</span>
            <div class="chart-controls">
              <el-radio-group v-model="chartType" @change="updateChart">
                <el-radio-button label="scatter">散点图</el-radio-button>
                <el-radio-button label="bar">柱状图</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="chartContainer" class="chart" style="height: 400px;"></div>
      </el-card>
    </div>

    <div class="industry-grid">
      <el-row :gutter="20">
        <el-col 
          v-for="industry in filteredIndustries" 
          :key="industry.code"
          :span="8"
          style="margin-bottom: 20px;"
        >
          <el-card 
            class="industry-card" 
            :class="getIndustryCardClass(industry.changePercent)"
            @click="viewIndustryDetail(industry)"
          >
            <div class="industry-header">
              <div class="industry-info">
                <h3 class="industry-name">{{ industry.name }}</h3>
                <span class="industry-code">{{ industry.code }}</span>
              </div>
              <div class="industry-performance">
                <div class="price-change" :class="getChangeClass(industry.changePercent)">
                  {{ formatChange(industry.changePercent) }}
                </div>
                <div class="price-value">{{ industry.currentPrice }}</div>
              </div>
            </div>
            
            <div class="industry-metrics">
              <div class="metric-row">
                <span class="metric-label">成交额:</span>
                <span class="metric-value">{{ formatAmount(industry.turnover) }}亿</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">市值:</span>
                <span class="metric-value">{{ formatAmount(industry.marketCap) }}亿</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">成份股:</span>
                <span class="metric-value">{{ industry.stockCount }}只</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">领涨股:</span>
                <span class="metric-value leader-stock" @click.stop="viewStockDetail(industry.leadingStock.code)">
                  {{ industry.leadingStock.name }}
                  <span :class="getChangeClass(industry.leadingStock.changePercent)">
                    ({{ formatChange(industry.leadingStock.changePercent) }})
                  </span>
                </span>
              </div>
            </div>
            
            <div class="industry-trend">
              <div class="trend-label">近期走势:</div>
              <div class="trend-chart">
                <div 
                  v-for="(point, index) in industry.trendData" 
                  :key="index"
                  class="trend-point"
                  :class="getTrendPointClass(point)"
                  :style="{ height: Math.abs(point) * 2 + 'px' }"
                ></div>
              </div>
            </div>
            
            <div class="industry-tags">
              <el-tag 
                v-for="tag in industry.tags" 
                :key="tag"
                size="small"
                :type="getTagType(tag)"
              >
                {{ tag }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48]"
        :total="totalIndustries"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <div class="hot-industries">
      <el-card>
        <template #header>
          <div class="section-header">
            <span>热门行业</span>
            <el-button size="small" @click="exportHotIndustries">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </template>
        
        <el-table :data="hotIndustries" stripe>
          <el-table-column prop="rank" label="排名" width="60" />
          <el-table-column prop="name" label="行业名称" width="150">
            <template #default="{ row }">
              <el-button type="text" @click="viewIndustryDetail(row)">{{ row.name }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="100">
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">{{ formatChange(row.changePercent) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额(亿)" width="120" />
          <el-table-column prop="stockCount" label="成份股数" width="100" />
          <el-table-column prop="leadingStock" label="领涨股" width="150">
            <template #default="{ row }">
              <el-button type="text" size="small" @click="viewStockDetail(row.leadingStock.code)">
                {{ row.leadingStock.name }}
                <span :class="getChangeClass(row.leadingStock.changePercent)">
                  ({{ formatChange(row.leadingStock.changePercent) }})
                </span>
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="heatScore" label="热度" width="100">
            <template #default="{ row }">
              <el-progress :percentage="row.heatScore" :show-text="false" :stroke-width="8" />
              <span style="margin-left: 8px;">{{ row.heatScore }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 行业详情对话框 -->
    <el-dialog v-model="industryDetailVisible" :title="selectedIndustry?.name" width="80%" top="5vh">
      <div v-if="selectedIndustry" class="industry-detail">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <div class="basic-info">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="info-section">
                    <h4>行业概况</h4>
                    <div class="info-grid">
                      <div class="info-item">
                        <span class="info-label">行业代码:</span>
                        <span class="info-value">{{ selectedIndustry.code }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">成份股数:</span>
                        <span class="info-value">{{ selectedIndustry.stockCount }}只</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">总市值:</span>
                        <span class="info-value">{{ formatAmount(selectedIndustry.marketCap) }}亿</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">流通市值:</span>
                        <span class="info-value">{{ formatAmount(selectedIndustry.floatMarketCap) }}亿</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">平均市盈率:</span>
                        <span class="info-value">{{ selectedIndustry.avgPE }}</span>
                      </div>
                      <div class="info-item">
                        <span class="info-label">平均市净率:</span>
                        <span class="info-value">{{ selectedIndustry.avgPB }}</span>
                      </div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-section">
                    <h4>今日表现</h4>
                    <div class="performance-metrics">
                      <div class="performance-item">
                        <span class="performance-label">涨跌幅:</span>
                        <span class="performance-value" :class="getChangeClass(selectedIndustry.changePercent)">
                          {{ formatChange(selectedIndustry.changePercent) }}
                        </span>
                      </div>
                      <div class="performance-item">
                        <span class="performance-label">成交额:</span>
                        <span class="performance-value">{{ formatAmount(selectedIndustry.turnover) }}亿</span>
                      </div>
                      <div class="performance-item">
                        <span class="performance-label">换手率:</span>
                        <span class="performance-value">{{ selectedIndustry.turnoverRate }}%</span>
                      </div>
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
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="成份股" name="stocks">
            <div class="stocks-section">
              <div class="stocks-header">
                <el-input
                  v-model="stockSearchKeyword"
                  placeholder="搜索成份股"
                  style="width: 200px;"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button @click="exportStocks">
                  <el-icon><Download /></el-icon>
                  导出成份股
                </el-button>
              </div>
              
              <el-table :data="filteredStocks" stripe max-height="400">
                <el-table-column prop="rank" label="排名" width="60" />
                <el-table-column prop="code" label="代码" width="80" />
                <el-table-column prop="name" label="名称" width="120">
                  <template #default="{ row }">
                    <el-button type="text" @click="viewStockDetail(row.code)">{{ row.name }}</el-button>
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="现价" width="80" />
                <el-table-column prop="changePercent" label="涨跌幅" width="100">
                  <template #default="{ row }">
                    <span :class="getChangeClass(row.changePercent)">{{ formatChange(row.changePercent) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="turnover" label="成交额(万)" width="120" />
                <el-table-column prop="marketCap" label="市值(亿)" width="100" />
                <el-table-column prop="pe" label="市盈率" width="80" />
                <el-table-column prop="pb" label="市净率" width="80" />
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button size="small" @click="addToWatchlist(row.code)">加自选</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="资金流向" name="capital">
            <div class="capital-flow">
              <div ref="capitalChartContainer" class="chart" style="height: 300px;"></div>
              <div class="capital-summary">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="capital-item">
                      <div class="capital-label">主力净流入</div>
                      <div class="capital-value" :class="getChangeClass(selectedIndustry.mainCapitalFlow)">
                        {{ formatAmount(selectedIndustry.mainCapitalFlow) }}亿
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="capital-item">
                      <div class="capital-label">超大单净流入</div>
                      <div class="capital-value" :class="getChangeClass(selectedIndustry.superLargeFlow)">
                        {{ formatAmount(selectedIndustry.superLargeFlow) }}亿
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="capital-item">
                      <div class="capital-label">大单净流入</div>
                      <div class="capital-value" :class="getChangeClass(selectedIndustry.largeFlow)">
                        {{ formatAmount(selectedIndustry.largeFlow) }}亿
                      </div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="capital-item">
                      <div class="capital-label">中小单净流入</div>
                      <div class="capital-value" :class="getChangeClass(selectedIndustry.smallFlow)">
                        {{ formatAmount(selectedIndustry.smallFlow) }}亿
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="industryDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="addIndustryToWatchlist">加入关注</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface StockInfo {
  rank: number
  code: string
  name: string
  price: number
  changePercent: number
  turnover: number
  marketCap: number
  pe: number
  pb: number
}

interface IndustryInfo {
  code: string
  name: string
  currentPrice: number
  changePercent: number
  turnover: number
  marketCap: number
  floatMarketCap: number
  stockCount: number
  avgPE: number
  avgPB: number
  turnoverRate: number
  risingStocks: number
  fallingStocks: number
  flatStocks: number
  leadingStock: {
    code: string
    name: string
    changePercent: number
  }
  trendData: number[]
  tags: string[]
  mainCapitalFlow: number
  superLargeFlow: number
  largeFlow: number
  smallFlow: number
  stocks: StockInfo[]
}

const loading = ref(false)
const sortBy = ref('changePercent')
const sortOrder = ref('desc')
const searchKeyword = ref('')
const stockSearchKeyword = ref('')
const chartType = ref('scatter')
const currentPage = ref(1)
const pageSize = ref(12)
const totalIndustries = ref(0)
const industryDetailVisible = ref(false)
const selectedIndustry = ref<IndustryInfo | null>(null)
const activeTab = ref('basic')

const chartContainer = ref<HTMLElement>()
const capitalChartContainer = ref<HTMLElement>()
const chartInstance = ref<echarts.ECharts>()
const capitalChartInstance = ref<echarts.ECharts>()

const overviewData = ref({
  totalIndustries: 104,
  risingIndustries: 67,
  fallingIndustries: 32,
  flatIndustries: 5
})

const allIndustries = ref<IndustryInfo[]>([])
const filteredIndustries = ref<IndustryInfo[]>([])
const hotIndustries = ref<IndustryInfo[]>([])

const filteredStocks = computed(() => {
  if (!selectedIndustry.value || !stockSearchKeyword.value) {
    return selectedIndustry.value?.stocks || []
  }
  return selectedIndustry.value.stocks.filter(stock => 
    stock.code.includes(stockSearchKeyword.value) || 
    stock.name.includes(stockSearchKeyword.value)
  )
})

const loadIndustryData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟行业数据
    const mockIndustries: IndustryInfo[] = []
    const industryNames = [
      '银行', '证券', '保险', '房地产', '建筑材料', '钢铁', '有色金属', '煤炭',
      '石油石化', '电力', '公用事业', '交通运输', '汽车', '家电', '食品饮料',
      '纺织服装', '轻工制造', '医药生物', '化工', '电子', '计算机', '通信',
      '传媒', '军工', '机械设备', '电气设备', '建筑装饰', '商业贸易',
      '休闲服务', '农林牧渔', '综合', '非银金融'
    ]
    
    for (let i = 0; i < industryNames.length; i++) {
      const changePercent = (Math.random() - 0.5) * 20
      const turnover = Math.random() * 500 + 50
      const marketCap = Math.random() * 5000 + 1000
      
      // 生成成份股数据
      const stocks: StockInfo[] = []
      const stockCount = Math.floor(Math.random() * 50) + 10
      for (let j = 0; j < stockCount; j++) {
        stocks.push({
          rank: j + 1,
          code: `${String(Math.floor(Math.random() * 999999)).padStart(6, '0')}`,
          name: `${industryNames[i]}股票${j + 1}`,
          price: Number((Math.random() * 100 + 10).toFixed(2)),
          changePercent: Number(((Math.random() - 0.5) * 20).toFixed(2)),
          turnover: Number((Math.random() * 10000 + 1000).toFixed(0)),
          marketCap: Number((Math.random() * 500 + 50).toFixed(2)),
          pe: Number((Math.random() * 50 + 5).toFixed(2)),
          pb: Number((Math.random() * 10 + 0.5).toFixed(2))
        })
      }
      
      // 找出领涨股
      const leadingStock = stocks.reduce((prev, current) => 
        prev.changePercent > current.changePercent ? prev : current
      )
      
      const trendData = Array.from({ length: 20 }, () => (Math.random() - 0.5) * 10)
      const tags = ['热门', '活跃', '机构重仓', '高分红'].filter(() => Math.random() > 0.7)
      
      mockIndustries.push({
        code: `BK${String(i + 1).padStart(4, '0')}`,
        name: industryNames[i],
        currentPrice: Number((Math.random() * 1000 + 100).toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        turnover: Number(turnover.toFixed(2)),
        marketCap: Number(marketCap.toFixed(2)),
        floatMarketCap: Number((marketCap * 0.8).toFixed(2)),
        stockCount,
        avgPE: Number((Math.random() * 30 + 10).toFixed(2)),
        avgPB: Number((Math.random() * 5 + 1).toFixed(2)),
        turnoverRate: Number((Math.random() * 10 + 1).toFixed(2)),
        risingStocks: stocks.filter(s => s.changePercent > 0).length,
        fallingStocks: stocks.filter(s => s.changePercent < 0).length,
        flatStocks: stocks.filter(s => s.changePercent === 0).length,
        leadingStock: {
          code: leadingStock.code,
          name: leadingStock.name,
          changePercent: leadingStock.changePercent
        },
        trendData,
        tags,
        mainCapitalFlow: Number(((Math.random() - 0.5) * 100).toFixed(2)),
        superLargeFlow: Number(((Math.random() - 0.5) * 50).toFixed(2)),
        largeFlow: Number(((Math.random() - 0.5) * 30).toFixed(2)),
        smallFlow: Number(((Math.random() - 0.5) * 20).toFixed(2)),
        stocks
      })
    }
    
    allIndustries.value = mockIndustries
    totalIndustries.value = mockIndustries.length
    
    // 生成热门行业数据
    hotIndustries.value = mockIndustries
      .sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent))
      .slice(0, 10)
      .map((industry, index) => ({
        ...industry,
        rank: index + 1,
        heatScore: Math.floor(Math.random() * 40) + 60
      }))
    
    sortIndustries()
    await nextTick()
    updateChart()
    
    ElMessage.success('行业数据加载成功')
  } catch (error) {
    ElMessage.error('加载行业数据失败')
  } finally {
    loading.value = false
  }
}

const sortIndustries = () => {
  const sorted = [...allIndustries.value].sort((a, b) => {
    let aValue = a[sortBy.value as keyof IndustryInfo] as number
    let bValue = b[sortBy.value as keyof IndustryInfo] as number
    
    if (sortBy.value === 'name') {
      aValue = a.name.localeCompare(b.name)
      bValue = 0
    }
    
    return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
  })
  
  filterIndustries(sorted)
}

const filterIndustries = (industries = allIndustries.value) => {
  if (!searchKeyword.value) {
    filteredIndustries.value = industries
  } else {
    filteredIndustries.value = industries.filter(industry => 
      industry.name.includes(searchKeyword.value) || 
      industry.code.includes(searchKeyword.value)
    )
  }
}

const updateChart = () => {
  if (!chartContainer.value) return
  
  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }
  
  if (chartType.value === 'scatter') {
    const data = allIndustries.value.map(industry => ([
      industry.turnover,
      industry.changePercent,
      industry.marketCap,
      industry.name
    ]))
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const [turnover, changePercent, marketCap, name] = params.data
          return `${name}<br/>成交额: ${turnover.toFixed(2)}亿<br/>涨跌幅: ${changePercent.toFixed(2)}%<br/>市值: ${marketCap.toFixed(2)}亿`
        }
      },
      xAxis: {
        type: 'value',
        name: '成交额(亿)',
        nameLocation: 'middle',
        nameGap: 30
      },
      yAxis: {
        type: 'value',
        name: '涨跌幅(%)',
        nameLocation: 'middle',
        nameGap: 40
      },
      series: [{
        type: 'scatter',
        data,
        symbolSize: (data: number[]) => Math.sqrt(data[2]) / 10,
        itemStyle: {
          color: (params: any) => {
            const changePercent = params.data[1]
            return changePercent > 0 ? '#f56c6c' : changePercent < 0 ? '#67c23a' : '#909399'
          }
        }
      }]
    }
    
    chartInstance.value.setOption(option)
  } else {
    const data = allIndustries.value
      .sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent))
      .slice(0, 20)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: data.map(d => d.name),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '涨跌幅(%)'
      },
      series: [{
        type: 'bar',
        data: data.map(d => ({
          value: d.changePercent,
          itemStyle: {
            color: d.changePercent > 0 ? '#f56c6c' : d.changePercent < 0 ? '#67c23a' : '#909399'
          }
        }))
      }]
    }
    
    chartInstance.value.setOption(option)
  }
}

const updateCapitalChart = () => {
  if (!capitalChartContainer.value || !selectedIndustry.value) return
  
  if (!capitalChartInstance.value) {
    capitalChartInstance.value = echarts.init(capitalChartContainer.value)
  }
  
  const industry = selectedIndustry.value
  const data = [
    { name: '超大单', value: Math.abs(industry.superLargeFlow) },
    { name: '大单', value: Math.abs(industry.largeFlow) },
    { name: '中单', value: Math.abs(industry.smallFlow / 2) },
    { name: '小单', value: Math.abs(industry.smallFlow / 2) }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}亿 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      name: '资金流向',
      type: 'pie',
      radius: '50%',
      data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
  
  capitalChartInstance.value.setOption(option)
}

const viewIndustryDetail = (industry: IndustryInfo) => {
  selectedIndustry.value = industry
  industryDetailVisible.value = true
  activeTab.value = 'basic'
  
  nextTick(() => {
    updateCapitalChart()
  })
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
}

const addToWatchlist = (stockCode: string) => {
  ElMessage.success(`股票 ${stockCode} 已加入自选`)
}

const addIndustryToWatchlist = () => {
  ElMessage.success(`行业 ${selectedIndustry.value?.name} 已加入关注`)
  industryDetailVisible.value = false
}

const exportHotIndustries = () => {
  ElMessage.success('热门行业导出功能开发中...')
}

const exportStocks = () => {
  ElMessage.success('成份股导出功能开发中...')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadIndustryData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadIndustryData()
}

const formatAmount = (amount: number): string => {
  return Math.abs(amount).toFixed(2)
}

const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : ''
  return sign + change.toFixed(2) + '%'
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getIndustryCardClass = (change: number): string => {
  return change > 0 ? 'rising' : change < 0 ? 'falling' : 'flat'
}

const getTrendPointClass = (point: number): string => {
  return point > 0 ? 'trend-up' : point < 0 ? 'trend-down' : 'trend-flat'
}

const getTagType = (tag: string): string => {
  const types: Record<string, string> = {
    '热门': 'danger',
    '活跃': 'warning',
    '机构重仓': 'success',
    '高分红': 'primary'
  }
  return types[tag] || 'info'
}

onMounted(() => {
  loadIndustryData()
})
</script>

<style scoped>
.industry-components {
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

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

.performance-chart {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.industry-grid {
  margin-bottom: 20px;
}

.industry-card {
  cursor: pointer;
  transition: all 0.3s;
  border-left: 4px solid #e8e8e8;
}

.industry-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.industry-card.rising {
  border-left-color: #f56c6c;
}

.industry-card.falling {
  border-left-color: #67c23a;
}

.industry-card.flat {
  border-left-color: #909399;
}

.industry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.industry-info h3 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 16px;
}

.industry-code {
  color: #909399;
  font-size: 12px;
}

.industry-performance {
  text-align: right;
}

.price-change {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 2px;
}

.price-value {
  color: #606266;
  font-size: 14px;
}

.industry-metrics {
  margin-bottom: 15px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.metric-label {
  color: #909399;
}

.metric-value {
  color: #303133;
}

.leader-stock {
  cursor: pointer;
  color: #409eff;
}

.leader-stock:hover {
  text-decoration: underline;
}

.industry-trend {
  margin-bottom: 15px;
}

.trend-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.trend-chart {
  display: flex;
  align-items: end;
  height: 30px;
  gap: 1px;
}

.trend-point {
  width: 3px;
  min-height: 2px;
  border-radius: 1px;
}

.trend-up {
  background-color: #f56c6c;
}

.trend-down {
  background-color: #67c23a;
}

.trend-flat {
  background-color: #909399;
}

.industry-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-bottom: 20px;
  text-align: right;
}

.hot-industries {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.basic-info {
  padding: 20px 0;
}

.info-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.info-label {
  color: #606266;
}

.info-value {
  font-weight: bold;
  color: #303133;
}

.performance-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
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

.stocks-section {
  padding: 10px 0;
}

.stocks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.capital-flow {
  padding: 10px 0;
}

.capital-summary {
  margin-top: 20px;
}

.capital-item {
  text-align: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.capital-label {
  display: block;
  color: #909399;
  font-size: 14px;
  margin-bottom: 8px;
}

.capital-value {
  display: block;
  font-size: 18px;
  font-weight: bold;
}

.dialog-footer {
  text-align: right;
}
</style>