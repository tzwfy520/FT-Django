<template>
  <div class="concept-components">
    <div class="page-header">
      <h2>概念板块成份</h2>
      <div class="header-actions">
        <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
          <el-option label="涨跌幅" value="changePercent" />
          <el-option label="成交额" value="turnover" />
          <el-option label="市值" value="marketCap" />
          <el-option label="概念名称" value="name" />
        </el-select>
        <el-select v-model="sortOrder" @change="handleSort">
          <el-option label="降序" value="desc" />
          <el-option label="升序" value="asc" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索概念板块"
          style="width: 200px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon rise">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overviewData.totalConcepts }}</div>
                <div class="overview-label">概念总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon rise">
                <el-icon><CaretTop /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value positive">{{ overviewData.risingConcepts }}</div>
                <div class="overview-label">上涨概念</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon fall">
                <el-icon><CaretBottom /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value negative">{{ overviewData.fallingConcepts }}</div>
                <div class="overview-label">下跌概念</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="overview-item">
              <div class="overview-icon neutral">
                <el-icon><Minus /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-value">{{ overviewData.flatConcepts }}</div>
                <div class="overview-label">平盘概念</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="chart-section">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card title="概念板块涨跌分布">
            <div ref="distributionChart" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card title="热门概念TOP10">
            <div class="hot-concepts">
              <div
                v-for="(concept, index) in hotConcepts"
                :key="concept.code"
                class="hot-concept-item"
                @click="viewConceptDetail(concept)"
              >
                <div class="rank">{{ index + 1 }}</div>
                <div class="concept-info">
                  <div class="concept-name">{{ concept.name }}</div>
                  <div class="concept-stats">
                    <span class="stock-count">{{ concept.stockCount }}只</span>
                    <span class="turnover">{{ formatAmount(concept.turnover) }}亿</span>
                  </div>
                </div>
                <div class="concept-change" :class="getChangeClass(concept.changePercent)">
                  {{ formatChange(concept.changePercent) }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="concept-grid">
      <el-row :gutter="20">
        <el-col
          v-for="concept in paginatedConcepts"
          :key="concept.code"
          :span="6"
          class="concept-col"
        >
          <el-card class="concept-card" @click="viewConceptDetail(concept)">
            <div class="concept-header">
              <div class="concept-title">
                <h4>{{ concept.name }}</h4>
                <span class="concept-code">{{ concept.code }}</span>
              </div>
              <div class="concept-change-badge" :class="getChangeClass(concept.changePercent)">
                {{ formatChange(concept.changePercent) }}
              </div>
            </div>
            
            <div class="concept-stats">
              <div class="stat-row">
                <span class="stat-label">成份股数量:</span>
                <span class="stat-value">{{ concept.stockCount }}只</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">总市值:</span>
                <span class="stat-value">{{ formatAmount(concept.marketCap) }}亿</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">成交额:</span>
                <span class="stat-value">{{ formatAmount(concept.turnover) }}亿</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">平均涨跌:</span>
                <span class="stat-value" :class="getChangeClass(concept.avgChange)">
                  {{ formatChange(concept.avgChange) }}
                </span>
              </div>
            </div>
            
            <div class="concept-leaders">
              <div class="leaders-title">领涨股票:</div>
              <div class="leaders-list">
                <span
                  v-for="leader in concept.leaders.slice(0, 3)"
                  :key="leader.code"
                  class="leader-stock"
                  :class="getChangeClass(leader.changePercent)"
                >
                  {{ leader.name }}
                </span>
              </div>
            </div>
            
            <div class="concept-tags">
              <el-tag
                v-for="tag in concept.tags"
                :key="tag"
                size="small"
                class="concept-tag"
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
        :page-sizes="[12, 24, 48, 96]"
        :total="filteredConcepts.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 概念详情对话框 -->
    <el-dialog
      v-model="showConceptDetail"
      :title="selectedConcept?.name"
      width="80%"
      top="5vh"
    >
      <div v-if="selectedConcept" class="concept-detail">
        <div class="detail-header">
          <div class="detail-info">
            <h3>{{ selectedConcept.name }}</h3>
            <span class="detail-code">{{ selectedConcept.code }}</span>
            <div class="detail-change" :class="getChangeClass(selectedConcept.changePercent)">
              {{ formatChange(selectedConcept.changePercent) }}
            </div>
          </div>
          <div class="detail-stats">
            <div class="detail-stat">
              <span class="detail-stat-label">成份股数量</span>
              <span class="detail-stat-value">{{ selectedConcept.stockCount }}只</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">总市值</span>
              <span class="detail-stat-value">{{ formatAmount(selectedConcept.marketCap) }}亿</span>
            </div>
            <div class="detail-stat">
              <span class="detail-stat-label">成交额</span>
              <span class="detail-stat-value">{{ formatAmount(selectedConcept.turnover) }}亿</span>
            </div>
          </div>
        </div>
        
        <div class="detail-description">
          <h4>概念描述</h4>
          <p>{{ selectedConcept.description }}</p>
        </div>
        
        <div class="detail-stocks">
          <h4>成份股列表</h4>
          <el-table :data="selectedConcept.stocks" stripe max-height="300">
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
            <el-table-column prop="marketCap" label="市值" width="120">
              <template #default="{ row }">
                <span>{{ formatAmount(row.marketCap) }}亿</span>
              </template>
            </el-table-column>
            <el-table-column prop="weight" label="权重" width="100">
              <template #default="{ row }">
                <span>{{ row.weight.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="text" size="small" @click="viewStockDetail(row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, TrendCharts, CaretTop, CaretBottom, Minus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface Stock {
  code: string
  name: string
  price: number
  changePercent: number
  turnover: number
  marketCap: number
  weight: number
}

interface ConceptInfo {
  code: string
  name: string
  changePercent: number
  stockCount: number
  marketCap: number
  turnover: number
  avgChange: number
  leaders: Stock[]
  tags: string[]
  description: string
  stocks: Stock[]
}

const loading = ref(false)
const sortBy = ref('changePercent')
const sortOrder = ref('desc')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(24)
const showConceptDetail = ref(false)
const selectedConcept = ref<ConceptInfo | null>(null)

const distributionChart = ref<HTMLElement>()
const distributionChartInstance = ref<echarts.ECharts>()

const overviewData = ref({
  totalConcepts: 0,
  risingConcepts: 0,
  fallingConcepts: 0,
  flatConcepts: 0
})

const conceptsData = ref<ConceptInfo[]>([])
const hotConcepts = ref<ConceptInfo[]>([])

const filteredConcepts = computed(() => {
  let filtered = [...conceptsData.value]
  
  if (searchKeyword.value) {
    filtered = filtered.filter(concept => 
      concept.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      concept.code.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  // 排序
  filtered.sort((a, b) => {
    let aValue = a[sortBy.value as keyof ConceptInfo] as number
    let bValue = b[sortBy.value as keyof ConceptInfo] as number
    
    if (sortBy.value === 'name') {
      aValue = a.name.localeCompare(b.name)
      bValue = 0
    }
    
    return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
  })
  
  return filtered
})

const paginatedConcepts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConcepts.value.slice(start, end)
})

const loadConceptsData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟概念板块数据
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
    
    const mockConcepts: ConceptInfo[] = conceptNames.map((name, index) => {
      const changePercent = (Math.random() - 0.5) * 20 // -10% 到 +10%
      const stockCount = Math.floor(Math.random() * 50) + 10
      const marketCap = Math.random() * 5000 + 500
      const turnover = Math.random() * 200 + 10
      
      // 生成成份股
      const stocks: Stock[] = []
      for (let i = 0; i < stockCount; i++) {
        stocks.push({
          code: `${String(Math.floor(Math.random() * 900000) + 100000)}`,
          name: `股票${i + 1}`,
          price: Math.random() * 100 + 10,
          changePercent: (Math.random() - 0.5) * 20,
          turnover: Math.random() * 50 + 1,
          marketCap: Math.random() * 500 + 50,
          weight: Math.random() * 10 + 1
        })
      }
      
      // 按涨跌幅排序获取领涨股
      const leaders = stocks.sort((a, b) => b.changePercent - a.changePercent).slice(0, 5)
      
      return {
        code: `BK${String(index + 1).padStart(4, '0')}`,
        name,
        changePercent: Number(changePercent.toFixed(2)),
        stockCount,
        marketCap: Number(marketCap.toFixed(2)),
        turnover: Number(turnover.toFixed(2)),
        avgChange: Number((stocks.reduce((sum, s) => sum + s.changePercent, 0) / stocks.length).toFixed(2)),
        leaders,
        tags: generateTags(name),
        description: generateDescription(name),
        stocks
      }
    })
    
    conceptsData.value = mockConcepts
    
    // 计算概览数据
    overviewData.value = {
      totalConcepts: mockConcepts.length,
      risingConcepts: mockConcepts.filter(c => c.changePercent > 0).length,
      fallingConcepts: mockConcepts.filter(c => c.changePercent < 0).length,
      flatConcepts: mockConcepts.filter(c => c.changePercent === 0).length
    }
    
    // 获取热门概念（按成交额排序）
    hotConcepts.value = [...mockConcepts]
      .sort((a, b) => b.turnover - a.turnover)
      .slice(0, 10)
    
    await nextTick()
    renderDistributionChart()
    
    ElMessage.success('概念板块数据加载成功')
  } catch (error) {
    ElMessage.error('加载概念板块数据失败')
  } finally {
    loading.value = false
  }
}

const generateTags = (name: string): string[] => {
  const allTags = ['热门', '新兴', '成长', '价值', '科技', '传统', '周期', '防御']
  const tagCount = Math.floor(Math.random() * 3) + 1
  return allTags.sort(() => Math.random() - 0.5).slice(0, tagCount)
}

const generateDescription = (name: string): string => {
  const descriptions = {
    '人工智能': '人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。',
    '新能源汽车': '新能源汽车是指采用非常规的车用燃料作为动力来源，综合车辆的动力控制和驱动方面的先进技术。',
    '5G通信': '5G网络是第五代移动通信网络，其峰值理论传输速度可达每秒数十Gb，比4G网络的传输速度快数百倍。'
  }
  
  return descriptions[name as keyof typeof descriptions] || `${name}相关的概念板块，包含了该领域的主要上市公司。`
}

const renderDistributionChart = () => {
  if (!distributionChart.value) return
  
  if (!distributionChartInstance.value) {
    distributionChartInstance.value = echarts.init(distributionChart.value)
  }
  
  const ranges = [
    { name: '跌停', min: -10, max: -9.5, color: '#006400' },
    { name: '-9%~-7%', min: -9, max: -7, color: '#228B22' },
    { name: '-7%~-5%', min: -7, max: -5, color: '#32CD32' },
    { name: '-5%~-3%', min: -5, max: -3, color: '#90EE90' },
    { name: '-3%~-1%', min: -3, max: -1, color: '#98FB98' },
    { name: '-1%~1%', min: -1, max: 1, color: '#F5F5F5' },
    { name: '1%~3%', min: 1, max: 3, color: '#FFB6C1' },
    { name: '3%~5%', min: 3, max: 5, color: '#FF69B4' },
    { name: '5%~7%', min: 5, max: 7, color: '#FF1493' },
    { name: '7%~9%', min: 7, max: 9, color: '#DC143C' },
    { name: '涨停', min: 9.5, max: 10, color: '#8B0000' }
  ]
  
  const data = ranges.map(range => {
    const count = conceptsData.value.filter(concept => 
      concept.changePercent >= range.min && concept.changePercent < range.max
    ).length
    
    return {
      name: range.name,
      value: count,
      itemStyle: { color: range.color }
    }
  })
  
  const option = {
    title: {
      text: '概念板块涨跌分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ranges.map(r => r.name)
    },
    series: [{
      name: '概念数量',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
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
  
  distributionChartInstance.value.setOption(option)
}

const refreshData = () => {
  loadConceptsData()
}

const handleSort = () => {
  // 触发计算属性重新计算
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const viewConceptDetail = (concept: ConceptInfo) => {
  selectedConcept.value = concept
  showConceptDetail.value = true
}

const viewStockDetail = (stock: Stock) => {
  ElMessage.info(`查看股票详情: ${stock.name} (${stock.code})`)
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

onMounted(() => {
  loadConceptsData()
})
</script>

<style scoped>
.concept-components {
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

.overview-section {
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

.overview-icon.rise {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.fall {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-icon.neutral {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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

.chart-section {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.hot-concepts {
  padding: 10px 0;
}

.hot-concept-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  background-color: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hot-concept-item:hover {
  background-color: #e9ecef;
  transform: translateX(5px);
}

.rank {
  width: 24px;
  height: 24px;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  margin-right: 10px;
}

.concept-info {
  flex: 1;
}

.concept-name {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.concept-stats {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.stock-count,
.turnover {
  background-color: #e1f3ff;
  padding: 2px 6px;
  border-radius: 3px;
}

.concept-change {
  font-size: 14px;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

.concept-grid {
  margin-bottom: 20px;
}

.concept-col {
  margin-bottom: 20px;
}

.concept-card {
  height: 280px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.concept-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.concept-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.concept-title h4 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 16px;
}

.concept-code {
  font-size: 12px;
  color: #909399;
}

.concept-change-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.concept-stats {
  margin-bottom: 15px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.concept-leaders {
  margin-bottom: 15px;
}

.leaders-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.leaders-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.leader-stock {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #f0f0f0;
}

.concept-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.concept-tag {
  font-size: 11px;
}

.pagination-container {
  text-align: right;
  margin-top: 20px;
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

.detail-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.detail-info h3 {
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

.detail-stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.detail-stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.detail-description {
  margin-bottom: 20px;
}

.detail-description h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.detail-description p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.detail-stocks h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.positive {
  color: #f56c6c;
  background-color: #f56c6c;
}

.negative {
  color: #67c23a;
  background-color: #67c23a;
}

.neutral {
  color: #909399;
  background-color: #909399;
}

.positive.concept-change-badge,
.positive.detail-change {
  background-color: #f56c6c;
}

.negative.concept-change-badge,
.negative.detail-change {
  background-color: #67c23a;
}

.neutral.concept-change-badge,
.neutral.detail-change {
  background-color: #909399;
}

.positive.leader-stock {
  background-color: #fef0f0;
  color: #f56c6c;
}

.negative.leader-stock {
  background-color: #f0f9ff;
  color: #67c23a;
}
</style>