<template>
  <div class="stock-data">
    <div class="page-header">
      <h1>股票数据</h1>
      <div class="search-controls">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索股票代码或名称"
          class="search-input"
          @input="handleSearch"
        />
        <select v-model="selectedMarket" class="market-select" @change="handleMarketChange">
          <option value="all">全部市场</option>
          <option value="sh">上海</option>
          <option value="sz">深圳</option>
          <option value="bj">北京</option>
        </select>
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <div class="data-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="data-content">
      <!-- 实时数据 -->
      <div v-if="activeTab === 'realtime'" class="data-table-container">
        <div class="table-header">
          <h3>实时行情</h3>
          <span class="update-time">更新时间: {{ lastUpdateTime }}</span>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>最新价</th>
                <th>涨跌幅</th>
                <th>涨跌额</th>
                <th>成交量</th>
                <th>成交额</th>
                <th>换手率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stock in filteredRealtimeData" :key="stock.code" class="stock-row">
                <td class="stock-code">{{ stock.code }}</td>
                <td class="stock-name">{{ stock.name }}</td>
                <td class="price">{{ stock.price }}</td>
                <td :class="['change-percent', stock.changePercent >= 0 ? 'positive' : 'negative']">
                  {{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent }}%
                </td>
                <td :class="['change-amount', stock.changeAmount >= 0 ? 'positive' : 'negative']">
                  {{ stock.changeAmount >= 0 ? '+' : '' }}{{ stock.changeAmount }}
                </td>
                <td class="volume">{{ formatVolume(stock.volume) }}</td>
                <td class="amount">{{ formatAmount(stock.amount) }}</td>
                <td class="turnover">{{ stock.turnover }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 历史数据 -->
      <div v-if="activeTab === 'history'" class="data-table-container">
        <div class="table-header">
          <h3>历史数据</h3>
          <div class="date-controls">
            <input v-model="startDate" type="date" class="date-input" />
            <span>至</span>
            <input v-model="endDate" type="date" class="date-input" />
            <button @click="loadHistoryData" class="query-btn">查询</button>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>开盘</th>
                <th>最高</th>
                <th>最低</th>
                <th>收盘</th>
                <th>涨跌幅</th>
                <th>成交量</th>
                <th>成交额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in historyData" :key="record.date" class="stock-row">
                <td>{{ record.date }}</td>
                <td>{{ record.open }}</td>
                <td>{{ record.high }}</td>
                <td>{{ record.low }}</td>
                <td>{{ record.close }}</td>
                <td :class="['change-percent', record.changePercent >= 0 ? 'positive' : 'negative']">
                  {{ record.changePercent >= 0 ? '+' : '' }}{{ record.changePercent }}%
                </td>
                <td class="volume">{{ formatVolume(record.volume) }}</td>
                <td class="amount">{{ formatAmount(record.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分钟数据 -->
      <div v-if="activeTab === 'minute'" class="data-table-container">
        <div class="table-header">
          <h3>分钟数据</h3>
          <div class="stock-selector">
            <input 
              v-model="selectedStockCode" 
              type="text" 
              placeholder="输入股票代码"
              class="stock-input"
            />
            <button @click="loadMinuteData" class="query-btn">查询</button>
          </div>
        </div>
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>价格</th>
                <th>成交量</th>
                <th>成交额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in minuteData" :key="record.time" class="stock-row">
                <td>{{ record.time }}</td>
                <td>{{ record.price }}</td>
                <td class="volume">{{ formatVolume(record.volume) }}</td>
                <td class="amount">{{ formatAmount(record.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 接口定义
interface RealtimeStock {
  code: string
  name: string
  price: number
  changePercent: number
  changeAmount: number
  volume: number
  amount: number
  turnover: number
  market: string
}

interface HistoryRecord {
  date: string
  open: number
  high: number
  low: number
  close: number
  changePercent: number
  volume: number
  amount: number
}

interface MinuteRecord {
  time: string
  price: number
  volume: number
  amount: number
}

// 响应式数据
const activeTab = ref('realtime')
const searchQuery = ref('')
const selectedMarket = ref('all')
const loading = ref(false)
const lastUpdateTime = ref('')
const startDate = ref('')
const endDate = ref('')
const selectedStockCode = ref('')

// 标签页配置
const tabs = [
  { key: 'realtime', label: '实时数据' },
  { key: 'history', label: '历史数据' },
  { key: 'minute', label: '分钟数据' }
]

// 模拟数据
const realtimeData = ref<RealtimeStock[]>([
  {
    code: '000001',
    name: '平安银行',
    price: 12.50,
    changePercent: 2.3,
    changeAmount: 0.28,
    volume: 15680000,
    amount: 195840000,
    turnover: 1.2,
    market: 'sz'
  },
  {
    code: '000002',
    name: '万科A',
    price: 18.20,
    changePercent: -1.2,
    changeAmount: -0.22,
    volume: 8950000,
    amount: 162790000,
    turnover: 0.8,
    market: 'sz'
  },
  {
    code: '600036',
    name: '招商银行',
    price: 45.80,
    changePercent: 1.8,
    changeAmount: 0.81,
    volume: 12340000,
    amount: 565172000,
    turnover: 0.5,
    market: 'sh'
  }
])

const historyData = ref<HistoryRecord[]>([])
const minuteData = ref<MinuteRecord[]>([])

// 计算属性
const filteredRealtimeData = computed(() => {
  let filtered = realtimeData.value
  
  // 市场筛选
  if (selectedMarket.value !== 'all') {
    filtered = filtered.filter(stock => stock.market === selectedMarket.value)
  }
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(stock => 
      stock.code.toLowerCase().includes(query) || 
      stock.name.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

// 生命周期
onMounted(() => {
  loadRealtimeData()
  // 设置默认日期
  const today = new Date()
  const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
  startDate.value = lastMonth.toISOString().split('T')[0]
  endDate.value = today.toISOString().split('T')[0]
})

// 方法
const loadRealtimeData = async () => {
  loading.value = true
  try {
    // 这里将调用后端API获取实时数据
    // const response = await fetch('/api/stocks/realtime')
    // realtimeData.value = await response.json()
    lastUpdateTime.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('加载实时数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadHistoryData = async () => {
  try {
    // 这里将调用后端API获取历史数据
    // const response = await fetch(`/api/stocks/history?start=${startDate.value}&end=${endDate.value}`)
    // historyData.value = await response.json()
    
    // 模拟数据
    historyData.value = [
      {
        date: '2024-01-15',
        open: 12.20,
        high: 12.58,
        low: 12.15,
        close: 12.50,
        changePercent: 2.3,
        volume: 15680000,
        amount: 195840000
      }
    ]
  } catch (error) {
    console.error('加载历史数据失败:', error)
  }
}

const loadMinuteData = async () => {
  if (!selectedStockCode.value) {
    alert('请输入股票代码')
    return
  }
  
  try {
    // 这里将调用后端API获取分钟数据
    // const response = await fetch(`/api/stocks/minute/${selectedStockCode.value}`)
    // minuteData.value = await response.json()
    
    // 模拟数据
    minuteData.value = [
      {
        time: '09:30',
        price: 12.45,
        volume: 156800,
        amount: 1958400
      }
    ]
  } catch (error) {
    console.error('加载分钟数据失败:', error)
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleMarketChange = () => {
  // 市场切换逻辑已在计算属性中处理
}

const refreshData = () => {
  loadRealtimeData()
}

// 工具函数
const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

const formatAmount = (amount: number): string => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toString()
}
</script>

<style scoped>
.stock-data {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2.5em;
  font-weight: 300;
}

.search-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input, .market-select, .date-input, .stock-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  width: 200px;
}

.refresh-btn, .query-btn {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:hover, .query-btn:hover {
  background-color: #2980b9;
}

.refresh-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.data-tabs {
  display: flex;
  gap: 2px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 12px 24px;
  background-color: white;
  border: 1px solid #ddd;
  border-bottom: none;
  cursor: pointer;
  font-size: 14px;
  color: #7f8c8d;
}

.tab-btn.active {
  background-color: #3498db;
  color: white;
  border-color: #3498db;
}

.data-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.data-table-container {
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
}

.update-time {
  color: #7f8c8d;
  font-size: 14px;
}

.date-controls, .stock-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  background-color: #f8f9fa;
  padding: 12px 8px;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  color: #495057;
  font-weight: 600;
}

.data-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #dee2e6;
}

.stock-row:hover {
  background-color: #f8f9fa;
}

.stock-code {
  font-weight: bold;
  color: #2c3e50;
}

.stock-name {
  color: #34495e;
}

.price {
  font-weight: bold;
  text-align: right;
}

.positive {
  color: #e74c3c;
}

.negative {
  color: #27ae60;
}

.change-percent, .change-amount {
  text-align: right;
  font-weight: bold;
}

.volume, .amount, .turnover {
  text-align: right;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .search-controls {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>