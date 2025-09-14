<template>
  <div class="custom-query">
    <div class="page-header">
      <h2>自助查询复盘</h2>
      <div class="header-actions">
        <div class="query-status">
          <el-tag :type="queryStatus.type" size="large">
            <el-icon><Clock /></el-icon>
            {{ queryStatus.text }}
          </el-tag>
        </div>
        <el-button @click="clearAll">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 股票搜索 -->
    <div class="search-section">
      <el-card>
        <template #header>
          <span>股票查询</span>
        </template>
        
        <el-row :gutter="20" align="middle">
          <el-col :span="8">
            <el-input
              v-model="searchCode"
              placeholder="输入股票代码或名称"
              size="large"
              @keyup.enter="searchStock"
              @input="handleSearchInput"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button @click="searchStock" :loading="searching">
                  查询
                </el-button>
              </template>
            </el-input>
            
            <!-- 搜索建议 -->
            <div v-if="searchSuggestions.length > 0" class="search-suggestions">
              <div 
                v-for="suggestion in searchSuggestions" 
                :key="suggestion.code"
                class="suggestion-item"
                @click="selectSuggestion(suggestion)"
              >
                <span class="suggestion-code">{{ suggestion.code }}</span>
                <span class="suggestion-name">{{ suggestion.name }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <el-date-picker
              v-model="queryDate"
              type="date"
              placeholder="选择日期"
              :disabled-date="disabledDate"
              @change="onDateChange"
            />
          </el-col>
          <el-col :span="4">
            <el-select v-model="analysisType" placeholder="分析类型">
              <el-option label="综合分析" value="comprehensive" />
              <el-option label="技术分析" value="technical" />
              <el-option label="资金分析" value="fund" />
              <el-option label="基本面分析" value="fundamental" />
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="addToComparison" :disabled="!currentStock">
              <el-icon><Plus /></el-icon>
              加入对比
            </el-button>
          </el-col>
          <el-col :span="4">
            <el-button @click="addToWatchlist" :disabled="!currentStock">
              <el-icon><Star /></el-icon>
              加入自选
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 当前查询股票 -->
    <div v-if="currentStock" class="current-stock">
      <el-card>
        <template #header>
          <div class="stock-header">
            <div class="stock-title">
              <span class="stock-name">{{ currentStock.name }}</span>
              <span class="stock-code">({{ currentStock.code }})</span>
              <el-tag v-if="currentStock.isLimitUp" type="danger" size="small">涨停</el-tag>
              <el-tag v-else-if="currentStock.isLimitDown" type="success" size="small">跌停</el-tag>
              <el-tag :type="getRecommendationType(currentStock.recommendation)" size="small">
                {{ currentStock.recommendation }}
              </el-tag>
            </div>
            <div class="stock-actions">
              <span class="query-date">查询日期: {{ formatDate(queryDate) }}</span>
              <el-rate v-model="currentStock.reviewScore" disabled show-score />
            </div>
          </div>
        </template>
        
        <!-- 基本信息 -->
        <el-row :gutter="20" class="stock-info">
          <el-col :span="4">
            <div class="info-item main-price">
              <div class="info-label">收盘价</div>
              <div class="info-value" :class="getPriceClass(currentStock.changePercent)">
                {{ currentStock.closePrice.toFixed(2) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌幅</div>
              <div class="info-value" :class="getChangeClass(currentStock.changePercent)">
                {{ formatPercent(currentStock.changePercent) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">涨跌额</div>
              <div class="info-value" :class="getChangeClass(currentStock.changeAmount)">
                {{ formatChangeAmount(currentStock.changeAmount) }}
              </div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交量</div>
              <div class="info-value">{{ formatVolume(currentStock.volume) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">成交额</div>
              <div class="info-value">{{ formatAmount(currentStock.turnover) }}万</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">换手率</div>
              <div class="info-value">{{ currentStock.turnoverRate.toFixed(2) }}%</div>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" class="stock-info">
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">开盘价</div>
              <div class="info-value">{{ currentStock.openPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">最高价</div>
              <div class="info-value positive">{{ currentStock.highPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">最低价</div>
              <div class="info-value negative">{{ currentStock.lowPrice.toFixed(2) }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">振幅</div>
              <div class="info-value">{{ currentStock.amplitude.toFixed(2) }}%</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">市盈率</div>
              <div class="info-value">{{ currentStock.pe > 0 ? currentStock.pe.toFixed(2) : '-' }}</div>
            </div>
          </el-col>
          <el-col :span="4">
            <div class="info-item">
              <div class="info-label">市净率</div>
              <div class="info-value">{{ currentStock.pb.toFixed(2) }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 详细分析 -->
    <div v-if="currentStock" class="analysis-section">
      <el-row :gutter="20">
        <!-- 图表分析 -->
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="chart-header">
                <span>{{ getChartTitle() }}</span>
                <div class="chart-actions">
                  <el-radio-group v-model="chartType" @change="updateChart">
                    <el-radio-button label="kline">K线图</el-radio-button>
                    <el-radio-button label="volume">成交量</el-radio-button>
                    <el-radio-button label="indicators">技术指标</el-radio-button>
                    <el-radio-button label="moneyflow">资金流向</el-radio-button>
                  </el-radio-group>
                  <el-button size="small" @click="fullScreen">
                    <el-icon><FullScreen /></el-icon>
                    全屏
                  </el-button>
                </div>
              </div>
            </template>
            
            <div ref="chartContainer" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <!-- 分析指标 -->
        <el-col :span="8">
          <el-card>
            <template #header>
              <span>{{ analysisType === 'technical' ? '技术指标' : analysisType === 'fund' ? '资金分析' : '综合指标' }}</span>
            </template>
            
            <div v-if="analysisType === 'technical'" class="technical-indicators">
              <div class="indicator-group">
                <h5>趋势指标</h5>
                <div class="indicator-item">
                  <span class="indicator-label">MA5:</span>
                  <span class="indicator-value">{{ currentStock.ma5.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">MA10:</span>
                  <span class="indicator-value">{{ currentStock.ma10.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">MA20:</span>
                  <span class="indicator-value">{{ currentStock.ma20.toFixed(2) }}</span>
                </div>
              </div>
              
              <div class="indicator-group">
                <h5>震荡指标</h5>
                <div class="indicator-item">
                  <span class="indicator-label">RSI:</span>
                  <span class="indicator-value" :class="getRSIClass(currentStock.rsi)">
                    {{ currentStock.rsi.toFixed(2) }}
                  </span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">KDJ-K:</span>
                  <span class="indicator-value">{{ currentStock.kdj.k.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">KDJ-D:</span>
                  <span class="indicator-value">{{ currentStock.kdj.d.toFixed(2) }}</span>
                </div>
              </div>
              
              <div class="indicator-group">
                <h5>能量指标</h5>
                <div class="indicator-item">
                  <span class="indicator-label">MACD:</span>
                  <span class="indicator-value" :class="getChangeClass(currentStock.macd)">
                    {{ currentStock.macd.toFixed(4) }}
                  </span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">BOLL上轨:</span>
                  <span class="indicator-value">{{ currentStock.boll.upper.toFixed(2) }}</span>
                </div>
                <div class="indicator-item">
                  <span class="indicator-label">BOLL下轨:</span>
                  <span class="indicator-value">{{ currentStock.boll.lower.toFixed(2) }}</span>
                </div>
              </div>
            </div>
            
            <div v-else-if="analysisType === 'fund'" class="fund-analysis">
              <div class="fund-group">
                <h5>资金流向</h5>
                <div class="fund-item">
                  <span class="fund-label">主力净流入:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.moneyFlow.mainNet)">
                    {{ formatAmount(Math.abs(currentStock.moneyFlow.mainNet)) }}万
                  </span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">超大单:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.moneyFlow.superLargeNet)">
                    {{ formatAmount(Math.abs(currentStock.moneyFlow.superLargeNet)) }}万
                  </span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">大单:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.moneyFlow.largeNet)">
                    {{ formatAmount(Math.abs(currentStock.moneyFlow.largeNet)) }}万
                  </span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">中单:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.moneyFlow.mediumNet)">
                    {{ formatAmount(Math.abs(currentStock.moneyFlow.mediumNet)) }}万
                  </span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">小单:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.moneyFlow.smallNet)">
                    {{ formatAmount(Math.abs(currentStock.moneyFlow.smallNet)) }}万
                  </span>
                </div>
              </div>
              
              <div class="fund-group">
                <h5>成交分析</h5>
                <div class="fund-item">
                  <span class="fund-label">量比:</span>
                  <span class="fund-value">{{ currentStock.volumeRatio.toFixed(2) }}</span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">委比:</span>
                  <span class="fund-value" :class="getChangeClass(currentStock.bidRatio)">
                    {{ currentStock.bidRatio.toFixed(2) }}%
                  </span>
                </div>
                <div class="fund-item">
                  <span class="fund-label">内外盘比:</span>
                  <span class="fund-value">{{ currentStock.inOutRatio.toFixed(2) }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="comprehensive-indicators">
              <div class="score-section">
                <h5>综合评分</h5>
                <div class="score-item">
                  <span>技术面:</span>
                  <el-progress :percentage="currentStock.technicalScore" :color="getScoreColor(currentStock.technicalScore)" />
                </div>
                <div class="score-item">
                  <span>资金面:</span>
                  <el-progress :percentage="currentStock.fundScore" :color="getScoreColor(currentStock.fundScore)" />
                </div>
                <div class="score-item">
                  <span>基本面:</span>
                  <el-progress :percentage="currentStock.fundamentalScore" :color="getScoreColor(currentStock.fundamentalScore)" />
                </div>
                <div class="score-item">
                  <span>综合评分:</span>
                  <el-progress :percentage="currentStock.overallScore" :color="getScoreColor(currentStock.overallScore)" />
                </div>
              </div>
              
              <div class="recommendation-section">
                <h5>操作建议</h5>
                <div class="recommendation-item">
                  <el-tag :type="getRecommendationType(currentStock.recommendation)" size="large">
                    {{ currentStock.recommendation }}
                  </el-tag>
                </div>
                <div class="risk-item">
                  <span>风险等级:</span>
                  <el-tag :type="getRiskType(currentStock.riskLevel)">
                    {{ currentStock.riskLevel }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 复盘分析报告 -->
    <div v-if="currentStock" class="review-report">
      <el-card>
        <template #header>
          <div class="report-header">
            <span>复盘分析报告</span>
            <el-button size="small" @click="generateReport">
              <el-icon><Refresh /></el-icon>
              重新生成
            </el-button>
          </div>
        </template>
        
        <el-tabs v-model="activeReportTab">
          <el-tab-pane label="交易表现" name="performance">
            <div class="report-content">
              <h4>当日交易表现</h4>
              <p>{{ currentStock.performanceAnalysis }}</p>
              
              <h4>价格走势分析</h4>
              <p>{{ currentStock.priceAnalysis }}</p>
              
              <h4>成交量分析</h4>
              <p>{{ currentStock.volumeAnalysis }}</p>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="技术分析" name="technical">
            <div class="report-content">
              <h4>技术指标分析</h4>
              <p>{{ currentStock.technicalAnalysis }}</p>
              
              <h4>支撑阻力位</h4>
              <p>{{ currentStock.supportResistanceAnalysis }}</p>
              
              <h4>趋势判断</h4>
              <p>{{ currentStock.trendAnalysis }}</p>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="资金分析" name="fund">
            <div class="report-content">
              <h4>资金流向分析</h4>
              <p>{{ currentStock.fundAnalysis }}</p>
              
              <h4>主力行为分析</h4>
              <p>{{ currentStock.mainForceAnalysis }}</p>
              
              <h4>散户情绪分析</h4>
              <p>{{ currentStock.retailAnalysis }}</p>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="后市展望" name="outlook">
            <div class="report-content">
              <h4>短期展望</h4>
              <p>{{ currentStock.shortTermOutlook }}</p>
              
              <h4>中期展望</h4>
              <p>{{ currentStock.mediumTermOutlook }}</p>
              
              <h4>风险提示</h4>
              <p>{{ currentStock.riskWarning }}</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <!-- 对比分析 -->
    <div v-if="comparisonStocks.length > 0" class="comparison-section">
      <el-card>
        <template #header>
          <div class="comparison-header">
            <span>对比分析 ({{ comparisonStocks.length }})</span>
            <el-button size="small" @click="clearComparison">
              清空对比
            </el-button>
          </div>
        </template>
        
        <el-table :data="comparisonStocks" stripe>
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="closePrice" label="收盘价" width="100">
            <template #default="{ row }">
              <span :class="getPriceClass(row.changePercent)">
                {{ row.closePrice.toFixed(2) }}
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
          <el-table-column prop="volume" label="成交量" width="120">
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="reviewScore" label="复盘评分" width="120">
            <template #default="{ row }">
              <el-rate v-model="row.reviewScore" disabled show-score />
            </template>
          </el-table-column>
          <el-table-column prop="recommendation" label="操作建议" width="100">
            <template #default="{ row }">
              <el-tag :type="getRecommendationType(row.recommendation)" size="small">
                {{ row.recommendation }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row, $index }">
              <el-button size="small" type="danger" @click="removeFromComparison($index)">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 查询历史 -->
    <div v-if="queryHistory.length > 0" class="history-section">
      <el-card>
        <template #header>
          <div class="history-header">
            <span>查询历史</span>
            <el-button size="small" @click="clearHistory">
              清空历史
            </el-button>
          </div>
        </template>
        
        <div class="history-list">
          <el-tag
            v-for="(item, index) in queryHistory"
            :key="index"
            class="history-item"
            closable
            @click="quickSearch(item)"
            @close="removeFromHistory(index)"
          >
            {{ item.code }} {{ item.name }} ({{ formatDate(item.date) }})
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Clock, Delete, Download, Search, Plus, Star, FullScreen, Refresh 
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface Stock {
  code: string
  name: string
  closePrice: number
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
  reviewScore: number
  recommendation: string
  riskLevel: string
  
  // 技术指标
  ma5: number
  ma10: number
  ma20: number
  rsi: number
  macd: number
  kdj: {
    k: number
    d: number
    j: number
  }
  boll: {
    upper: number
    middle: number
    lower: number
  }
  
  // 资金分析
  moneyFlow: {
    mainNet: number
    superLargeNet: number
    largeNet: number
    mediumNet: number
    smallNet: number
  }
  volumeRatio: number
  bidRatio: number
  inOutRatio: number
  
  // 综合评分
  technicalScore: number
  fundScore: number
  fundamentalScore: number
  overallScore: number
  
  // 分析报告
  performanceAnalysis: string
  priceAnalysis: string
  volumeAnalysis: string
  technicalAnalysis: string
  supportResistanceAnalysis: string
  trendAnalysis: string
  fundAnalysis: string
  mainForceAnalysis: string
  retailAnalysis: string
  shortTermOutlook: string
  mediumTermOutlook: string
  riskWarning: string
}

interface SearchSuggestion {
  code: string
  name: string
}

interface QueryHistoryItem {
  code: string
  name: string
  date: Date
}

const searching = ref(false)
const searchCode = ref('')
const queryDate = ref(new Date())
const analysisType = ref('comprehensive')
const chartType = ref('kline')
const activeReportTab = ref('performance')

const currentStock = ref<Stock | null>(null)
const searchSuggestions = ref<SearchSuggestion[]>([])
const comparisonStocks = ref<Stock[]>([])
const queryHistory = ref<QueryHistoryItem[]>([])
const chartContainer = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const queryStatus = ref({
  type: 'success' as const,
  text: '可以查询复盘数据'
})

const getChartTitle = () => {
  const titles = {
    kline: 'K线图',
    volume: '成交量分析',
    indicators: '技术指标',
    moneyflow: '资金流向'
  }
  return titles[chartType.value] || 'K线图'
}

const disabledDate = (time: Date) => {
  // 禁用未来日期和周末
  const today = new Date()
  const day = time.getDay()
  return time.getTime() > today.getTime() || day === 0 || day === 6
}

const handleSearchInput = () => {
  if (searchCode.value.length >= 2) {
    // 模拟搜索建议
    const suggestions = [
      { code: '000001', name: '平安银行' },
      { code: '000002', name: '万科A' },
      { code: '000858', name: '五粮液' },
      { code: '600036', name: '招商银行' },
      { code: '600519', name: '贵州茅台' },
      { code: '000063', name: '中兴通讯' },
      { code: '002415', name: '海康威视' },
      { code: '300059', name: '东方财富' }
    ].filter(item => 
      item.code.includes(searchCode.value) || 
      item.name.includes(searchCode.value)
    )
    
    searchSuggestions.value = suggestions.slice(0, 5)
  } else {
    searchSuggestions.value = []
  }
}

const selectSuggestion = (suggestion: SearchSuggestion) => {
  searchCode.value = suggestion.code
  searchSuggestions.value = []
  searchStock()
}

const onDateChange = () => {
  if (currentStock.value) {
    searchStock()
  }
}

const searchStock = async () => {
  if (!searchCode.value.trim()) {
    ElMessage.error('请输入股票代码或名称')
    return
  }
  
  searching.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟股票数据
    const basePrice = Math.random() * 100 + 10
    const changePercent = (Math.random() - 0.5) * 10
    const changeAmount = (basePrice * changePercent) / 100
    const closePrice = basePrice + changeAmount
    
    const stockNames = ['平安银行', '万科A', '五粮液', '招商银行', '贵州茅台', '中兴通讯', '海康威视', '东方财富']
    const stockName = stockNames[Math.floor(Math.random() * stockNames.length)]
    
    const recommendations = ['买入', '持有', '减仓', '观望']
    const riskLevels = ['低风险', '中风险', '高风险']
    
    currentStock.value = {
      code: searchCode.value.toUpperCase(),
      name: stockName,
      closePrice,
      changePercent,
      changeAmount,
      openPrice: basePrice + (Math.random() - 0.5) * 2,
      highPrice: closePrice + Math.random() * 3,
      lowPrice: closePrice - Math.random() * 3,
      prevClose: basePrice,
      volume: Math.floor(Math.random() * 50000000 + 1000000),
      turnover: Math.floor(Math.random() * 500000 + 10000),
      turnoverRate: Math.random() * 5,
      amplitude: Math.random() * 10,
      pe: Math.random() * 50 + 5,
      pb: Math.random() * 5 + 0.5,
      isLimitUp: Math.random() < 0.05,
      isLimitDown: Math.random() < 0.05,
      reviewScore: Math.floor(Math.random() * 5) + 1,
      recommendation: recommendations[Math.floor(Math.random() * recommendations.length)],
      riskLevel: riskLevels[Math.floor(Math.random() * riskLevels.length)],
      
      // 技术指标
      ma5: closePrice + (Math.random() - 0.5) * 2,
      ma10: closePrice + (Math.random() - 0.5) * 4,
      ma20: closePrice + (Math.random() - 0.5) * 6,
      rsi: Math.random() * 100,
      macd: (Math.random() - 0.5) * 2,
      kdj: {
        k: Math.random() * 100,
        d: Math.random() * 100,
        j: Math.random() * 100
      },
      boll: {
        upper: closePrice + Math.random() * 5,
        middle: closePrice,
        lower: closePrice - Math.random() * 5
      },
      
      // 资金分析
      moneyFlow: {
        mainNet: (Math.random() - 0.5) * 100000,
        superLargeNet: (Math.random() - 0.5) * 50000,
        largeNet: (Math.random() - 0.5) * 30000,
        mediumNet: (Math.random() - 0.5) * 20000,
        smallNet: (Math.random() - 0.5) * 10000
      },
      volumeRatio: Math.random() * 3 + 0.5,
      bidRatio: (Math.random() - 0.5) * 20,
      inOutRatio: Math.random() * 2 + 0.5,
      
      // 综合评分
      technicalScore: Math.floor(Math.random() * 100),
      fundScore: Math.floor(Math.random() * 100),
      fundamentalScore: Math.floor(Math.random() * 100),
      overallScore: Math.floor(Math.random() * 100),
      
      // 分析报告
      performanceAnalysis: `${stockName}在${formatDate(queryDate.value)}的交易中表现${changePercent >= 0 ? '强势' : '疲软'}，全天${changePercent >= 0 ? '上涨' : '下跌'}${Math.abs(changePercent).toFixed(2)}%，成交量较前一交易日${Math.random() > 0.5 ? '放大' : '缩小'}${Math.floor(Math.random() * 50)}%。`,
      priceAnalysis: `价格走势分析显示，该股开盘后${Math.random() > 0.5 ? '高开' : '低开'}，盘中${Math.random() > 0.5 ? '震荡上行' : '震荡下行'}，最终以${changePercent >= 0 ? '红盘' : '绿盘'}收场。技术面上呈现${Math.random() > 0.5 ? '多头' : '空头'}格局。`,
      volumeAnalysis: `成交量分析表明，该股成交活跃度${Math.random() > 0.5 ? '较高' : '一般'}，量价配合${Math.random() > 0.5 ? '良好' : '不佳'}，显示市场参与度${Math.random() > 0.5 ? '积极' : '谨慎'}。`,
      technicalAnalysis: `技术指标综合分析：RSI指标显示${Math.random() > 0.5 ? '超买' : '超卖'}信号，MACD指标呈现${Math.random() > 0.5 ? '金叉' : '死叉'}形态，KDJ指标${Math.random() > 0.5 ? '向上' : '向下'}发散，整体技术面${Math.random() > 0.5 ? '偏强' : '偏弱'}。`,
      supportResistanceAnalysis: `支撑阻力位分析：重要支撑位在${(closePrice * 0.95).toFixed(2)}元附近，关键阻力位在${(closePrice * 1.05).toFixed(2)}元附近。`,
      trendAnalysis: `趋势判断：短期趋势${Math.random() > 0.5 ? '向上' : '向下'}，中期趋势${Math.random() > 0.5 ? '向上' : '向下'}，长期趋势${Math.random() > 0.5 ? '向上' : '向下'}。`,
      fundAnalysis: `资金流向分析：主力资金呈现${Math.random() > 0.5 ? '净流入' : '净流出'}态势，大单资金${Math.random() > 0.5 ? '积极' : '谨慎'}参与，散户资金${Math.random() > 0.5 ? '跟进' : '观望'}情绪明显。`,
      mainForceAnalysis: `主力行为分析：机构投资者${Math.random() > 0.5 ? '增持' : '减持'}意愿${Math.random() > 0.5 ? '强烈' : '一般'}，操作手法${Math.random() > 0.5 ? '积极' : '谨慎'}，显示对后市${Math.random() > 0.5 ? '看好' : '谨慎'}。`,
      retailAnalysis: `散户情绪分析：散户投资者情绪${Math.random() > 0.5 ? '乐观' : '悲观'}，参与度${Math.random() > 0.5 ? '较高' : '一般'}，追涨杀跌情绪${Math.random() > 0.5 ? '明显' : '不明显'}。`,
      shortTermOutlook: `短期展望：基于当前技术面和资金面分析，预计短期内该股将${Math.random() > 0.5 ? '继续上涨' : '震荡调整'}，建议投资者${Math.random() > 0.5 ? '积极关注' : '谨慎操作'}。`,
      mediumTermOutlook: `中期展望：从基本面和行业发展趋势看，该股中期投资价值${Math.random() > 0.5 ? '较好' : '一般'}，适合${Math.random() > 0.5 ? '中长期持有' : '波段操作'}。`,
      riskWarning: `风险提示：投资有风险，需注意市场波动风险、政策风险、行业风险等，建议合理控制仓位，做好风险管理。`
    }
    
    // 添加到查询历史
    const historyItem = { 
      code: currentStock.value.code, 
      name: currentStock.value.name,
      date: new Date(queryDate.value)
    }
    const existingIndex = queryHistory.value.findIndex(item => 
      item.code === historyItem.code && 
      item.date.toDateString() === historyItem.date.toDateString()
    )
    if (existingIndex >= 0) {
      queryHistory.value.splice(existingIndex, 1)
    }
    queryHistory.value.unshift(historyItem)
    if (queryHistory.value.length > 20) {
      queryHistory.value = queryHistory.value.slice(0, 20)
    }
    
    // 初始化图表
    await nextTick()
    initChart()
    
    searchSuggestions.value = []
    ElMessage.success('查询成功')
    
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    searching.value = false
  }
}

const initChart = () => {
  if (!chartContainer.value || !currentStock.value) return
  
  chart.value = echarts.init(chartContainer.value)
  updateChart()
}

const updateChart = () => {
  if (!chart.value || !currentStock.value) return
  
  // 根据图表类型生成不同的配置
  let option = {}
  
  switch (chartType.value) {
    case 'kline':
      option = generateKlineOption()
      break
    case 'volume':
      option = generateVolumeOption()
      break
    case 'indicators':
      option = generateIndicatorsOption()
      break
    case 'moneyflow':
      option = generateMoneyFlowOption()
      break
  }
  
  chart.value.setOption(option, true)
}

const generateKlineOption = () => {
  // 生成模拟K线数据
  const data = []
  let basePrice = currentStock.value!.prevClose
  
  for (let i = 0; i < 30; i++) {
    const open = basePrice + (Math.random() - 0.5) * 2
    const close = open + (Math.random() - 0.5) * 3
    const high = Math.max(open, close) + Math.random() * 2
    const low = Math.min(open, close) - Math.random() * 2
    
    data.push([open, close, low, high])
    basePrice = close
  }
  
  return {
    title: {
      text: `${currentStock.value!.name} K线图`,
      left: 'center'
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
    },
    yAxis: {
      scale: true
    },
    series: [{
      type: 'candlestick',
      data: data,
      itemStyle: {
        color: '#f56c6c',
        color0: '#67c23a',
        borderColor: '#f56c6c',
        borderColor0: '#67c23a'
      }
    }]
  }
}

const generateVolumeOption = () => {
  const data = Array.from({ length: 30 }, () => Math.floor(Math.random() * 10000000 + 1000000))
  
  return {
    title: {
      text: `${currentStock.value!.name} 成交量分析`,
      left: 'center'
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'bar',
      data: data,
      itemStyle: {
        color: '#409eff'
      }
    }]
  }
}

const generateIndicatorsOption = () => {
  const rsiData = Array.from({ length: 30 }, () => Math.random() * 100)
  const macdData = Array.from({ length: 30 }, () => (Math.random() - 0.5) * 2)
  
  return {
    title: {
      text: `${currentStock.value!.name} 技术指标`,
      left: 'center'
    },
    legend: {
      data: ['RSI', 'MACD'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
    },
    yAxis: [
      {
        type: 'value',
        name: 'RSI',
        position: 'left'
      },
      {
        type: 'value',
        name: 'MACD',
        position: 'right'
      }
    ],
    series: [
      {
        name: 'RSI',
        type: 'line',
        data: rsiData,
        yAxisIndex: 0,
        lineStyle: { color: '#f56c6c' }
      },
      {
        name: 'MACD',
        type: 'line',
        data: macdData,
        yAxisIndex: 1,
        lineStyle: { color: '#67c23a' }
      }
    ]
  }
}

const generateMoneyFlowOption = () => {
  const moneyFlow = currentStock.value!.moneyFlow
  const data = [
    { name: '主力净流入', value: Math.abs(moneyFlow.mainNet) },
    { name: '超大单', value: Math.abs(moneyFlow.superLargeNet) },
    { name: '大单', value: Math.abs(moneyFlow.largeNet) },
    { name: '中单', value: Math.abs(moneyFlow.mediumNet) },
    { name: '小单', value: Math.abs(moneyFlow.smallNet) }
  ]
  
  return {
    title: {
      text: `${currentStock.value!.name} 资金流向`,
      left: 'center'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
}

const addToComparison = () => {
  if (!currentStock.value) return
  
  if (comparisonStocks.value.some(s => s.code === currentStock.value!.code)) {
    ElMessage.warning('该股票已在对比列表中')
    return
  }
  
  if (comparisonStocks.value.length >= 10) {
    ElMessage.warning('对比列表最多支持10只股票')
    return
  }
  
  comparisonStocks.value.push({ ...currentStock.value })
  ElMessage.success('已加入对比列表')
}

const removeFromComparison = (index: number) => {
  comparisonStocks.value.splice(index, 1)
  ElMessage.success('已从对比列表移除')
}

const clearComparison = () => {
  comparisonStocks.value = []
  ElMessage.success('已清空对比列表')
}

const addToWatchlist = () => {
  if (!currentStock.value) return
  
  ElMessage.success(`已将${currentStock.value.name}加入自选`)
}

const quickSearch = (item: QueryHistoryItem) => {
  searchCode.value = item.code
  queryDate.value = new Date(item.date)
  searchStock()
}

const removeFromHistory = (index: number) => {
  queryHistory.value.splice(index, 1)
}

const clearHistory = () => {
  queryHistory.value = []
  ElMessage.success('已清空查询历史')
}

const clearAll = () => {
  currentStock.value = null
  comparisonStocks.value = []
  searchCode.value = ''
  searchSuggestions.value = []
  ElMessage.success('已清空所有数据')
}

const exportReport = () => {
  ElMessage.success('复盘报告导出功能开发中...')
}

const fullScreen = () => {
  ElMessage.info('全屏功能开发中...')
}

const generateReport = () => {
  ElMessage.success('报告重新生成完成')
}

const formatDate = (date: Date): string => {
  return date.toLocaleDateString('zh-CN')
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

const getRSIClass = (rsi: number): string => {
  if (rsi > 70) return 'negative' // 超买
  if (rsi < 30) return 'positive' // 超卖
  return 'neutral'
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

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  // 设置默认查询日期为昨天（排除周末）
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  
  // 如果昨天是周末，设置为上周五
  if (yesterday.getDay() === 0) { // 周日
    yesterday.setDate(yesterday.getDate() - 2)
  } else if (yesterday.getDay() === 6) { // 周六
    yesterday.setDate(yesterday.getDate() - 1)
  }
  
  queryDate.value = yesterday
  
  // 检查查询状态
  const now = new Date()
  const hour = now.getHours()
  
  if (hour >= 16) {
    queryStatus.value = {
      type: 'success',
      text: '可以查询当日复盘数据'
    }
  } else {
    queryStatus.value = {
      type: 'warning',
      text: `等待收盘后查询 (${16 - hour}小时后)`
    }
  }
})
</script>

<style scoped>
.custom-query {
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

.search-section {
  margin-bottom: 20px;
  position: relative;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dcdfe6;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

.suggestion-code {
  font-weight: bold;
  color: #409eff;
}

.suggestion-name {
  color: #606266;
}

.current-stock {
  margin-bottom: 20px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stock-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.stock-code {
  font-size: 14px;
  color: #909399;
}

.stock-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.query-date {
  color: #409eff;
  font-weight: bold;
}

.stock-info {
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item.main-price {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.info-item.main-price .info-value {
  color: white !important;
  font-size: 24px;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.info-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.analysis-section {
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.chart-container {
  height: 500px;
  width: 100%;
}

.technical-indicators,
.fund-analysis,
.comprehensive-indicators {
  padding: 10px 0;
}

.indicator-group,
.fund-group {
  margin-bottom: 20px;
}

.indicator-group h5,
.fund-group h5 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 5px;
}

.indicator-item,
.fund-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  font-size: 13px;
}

.indicator-label,
.fund-label {
  color: #606266;
}

.indicator-value,
.fund-value {
  font-weight: bold;
  color: #303133;
}

.score-section {
  margin-bottom: 20px;
}

.score-section h5 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 14px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.score-item span {
  width: 60px;
  font-size: 12px;
  color: #606266;
}

.recommendation-section {
  text-align: center;
}

.recommendation-section h5 {
  margin: 0 0 15px 0;
  color: #409eff;
  font-size: 14px;
}

.recommendation-item {
  margin-bottom: 10px;
}

.risk-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.review-report {
  margin-bottom: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-content {
  padding: 20px;
  line-height: 1.8;
}

.report-content h4 {
  margin: 20px 0 10px 0;
  color: #409eff;
  font-size: 16px;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.report-content h4:first-child {
  margin-top: 0;
}

.report-content p {
  margin: 0 0 15px 0;
  color: #606266;
  text-indent: 2em;
}

.comparison-section {
  margin-bottom: 20px;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-section {
  margin-bottom: 20px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.history-item {
  cursor: pointer;
  margin-bottom: 5px;
}

.history-item:hover {
  opacity: 0.8;
}

/* 价格颜色样式 */
.positive {
  color: #f56c6c !important;
}

.negative {
  color: #67c23a !important;
}

.neutral {
  color: #909399 !important;
}

.price-up {
  color: #f56c6c !important;
}

.price-down {
  color: #67c23a !important;
}

.price-flat {
  color: #303133 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .stock-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .chart-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .comparison-header,
  .history-header,
  .report-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>