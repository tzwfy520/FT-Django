<template>
  <div class="market-realtime-data">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>大盘实时数据</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="refreshData" :disabled="loading">
          <i class="icon-refresh"></i>
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载大盘实时数据...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="refreshData" class="btn btn-secondary">重试</button>
    </div>

    <!-- 数据展示 -->
    <div v-if="!loading && !error" class="data-container">
      <!-- 主要指数 -->
      <div class="indices-section">
        <h2>主要指数</h2>
        <div class="indices-grid">
          <div v-for="index in indices" :key="index.code" class="index-card">
            <div class="index-header">
              <h3>{{ index.name }}</h3>
              <span class="index-code">{{ index.code }}</span>
            </div>
            <div class="index-data">
              <div class="current-price" :class="getPriceClass(index.change)">
                {{ index.current }}
              </div>
              <div class="change-info" :class="getPriceClass(index.change)">
                <span class="change">{{ formatChange(index.change) }}</span>
                <span class="change-percent">{{ formatPercent(index.changePercent) }}</span>
              </div>
            </div>
            <div class="index-stats">
              <div class="stat-item">
                <span class="label">开盘:</span>
                <span class="value">{{ index.open }}</span>
              </div>
              <div class="stat-item">
                <span class="label">最高:</span>
                <span class="value">{{ index.high }}</span>
              </div>
              <div class="stat-item">
                <span class="label">最低:</span>
                <span class="value">{{ index.low }}</span>
              </div>
              <div class="stat-item">
                <span class="label">成交量:</span>
                <span class="value">{{ formatVolume(index.volume) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 市场概况 -->
      <div class="market-overview">
        <h2>市场概况</h2>
        <div class="overview-grid">
          <div class="overview-card">
            <h4>上涨家数</h4>
            <div class="value up">{{ marketOverview.upCount }}</div>
          </div>
          <div class="overview-card">
            <h4>下跌家数</h4>
            <div class="value down">{{ marketOverview.downCount }}</div>
          </div>
          <div class="overview-card">
            <h4>平盘家数</h4>
            <div class="value flat">{{ marketOverview.flatCount }}</div>
          </div>
          <div class="overview-card">
            <h4>涨停家数</h4>
            <div class="value limit-up">{{ marketOverview.limitUpCount }}</div>
          </div>
          <div class="overview-card">
            <h4>跌停家数</h4>
            <div class="value limit-down">{{ marketOverview.limitDownCount }}</div>
          </div>
        </div>
      </div>

      <!-- 更新时间 -->
      <div class="update-time">
        <p>数据更新时间: {{ updateTime }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// 响应式数据
const loading = ref(false)
const error = ref('')
const updateTime = ref('')
const indices = ref([])
const marketOverview = ref({
  upCount: 0,
  downCount: 0,
  flatCount: 0,
  limitUpCount: 0,
  limitDownCount: 0
})

// 定时器
let refreshTimer: NodeJS.Timeout

// 生命周期
onMounted(() => {
  loadData()
  // 每30秒自动刷新
  refreshTimer = setInterval(loadData, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 方法
const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    indices.value = [
      {
        name: '上证指数',
        code: '000001',
        current: 3245.67,
        change: 12.34,
        changePercent: 0.38,
        open: 3233.33,
        high: 3256.78,
        low: 3228.90,
        volume: 234567890
      },
      {
        name: '深证成指',
        code: '399001',
        current: 12456.78,
        change: -23.45,
        changePercent: -0.19,
        open: 12480.23,
        high: 12489.12,
        low: 12445.67,
        volume: 345678901
      },
      {
        name: '创业板指',
        code: '399006',
        current: 2567.89,
        change: 5.67,
        changePercent: 0.22,
        open: 2562.22,
        high: 2578.90,
        low: 2558.34,
        volume: 156789012
      }
    ]
    
    marketOverview.value = {
      upCount: 2156,
      downCount: 1834,
      flatCount: 234,
      limitUpCount: 45,
      limitDownCount: 23
    }
    
    updateTime.value = new Date().toLocaleString('zh-CN')
  } catch (err) {
    error.value = '加载数据失败，请稍后重试'
    console.error('加载大盘实时数据失败:', err)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const getPriceClass = (change: number) => {
  if (change > 0) return 'up'
  if (change < 0) return 'down'
  return 'flat'
}

const formatChange = (change: number) => {
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${change.toFixed(2)}`
}

const formatPercent = (percent: number) => {
  const prefix = percent > 0 ? '+' : ''
  return `${prefix}${percent.toFixed(2)}%`
}

const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}
</script>

<style scoped>
.market-realtime-data {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2.5em;
  font-weight: 300;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  padding: 20px;
  background: #e74c3c;
  color: white;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.data-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.indices-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.indices-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.8em;
  font-weight: 400;
}

.indices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.index-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.index-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2em;
}

.index-code {
  color: #7f8c8d;
  font-size: 0.9em;
}

.index-data {
  margin-bottom: 15px;
}

.current-price {
  font-size: 2em;
  font-weight: bold;
  margin-bottom: 5px;
}

.change-info {
  display: flex;
  gap: 10px;
  font-size: 1.1em;
}

.index-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid #e9ecef;
}

.stat-item .label {
  color: #7f8c8d;
  font-size: 0.9em;
}

.stat-item .value {
  color: #2c3e50;
  font-weight: 500;
}

.market-overview {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.market-overview h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.8em;
  font-weight: 400;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.overview-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.overview-card h4 {
  margin: 0 0 10px 0;
  color: #7f8c8d;
  font-size: 0.9em;
  font-weight: 400;
}

.overview-card .value {
  font-size: 2em;
  font-weight: bold;
}

.up {
  color: #e74c3c;
}

.down {
  color: #27ae60;
}

.flat {
  color: #7f8c8d;
}

.limit-up {
  color: #e74c3c;
}

.limit-down {
  color: #27ae60;
}

.update-time {
  text-align: center;
  color: #7f8c8d;
  font-size: 0.9em;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .indices-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .index-stats {
    grid-template-columns: 1fr;
  }
}
</style>