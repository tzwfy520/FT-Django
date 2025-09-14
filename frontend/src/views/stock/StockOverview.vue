<template>
  <div class="stock-overview">
    <div class="page-header">
      <h2>股票概览</h2>
      <div class="header-actions">
        <div class="status-info">
          <span class="update-time">最后更新: {{ lastUpdateTime }}</span>
          <span v-if="isFromLocalCache" class="cache-status local-cache">💾 本地缓存</span>
          <span v-else-if="fromCache" class="cache-status server-cache">📋 服务器缓存</span>
          <span v-if="autoRefresh" class="countdown">🔄 {{ countdown }}s后刷新</span>
        </div>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索股票代码或名称"
          style="width: 300px; margin-right: 10px;"
          @input="searchStocks"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button 
          :type="autoRefresh ? 'success' : 'info'" 
          @click="toggleAutoRefresh"
          style="margin-right: 10px;"
        >
          {{ autoRefresh ? '停止自动刷新' : '开启自动刷新' }}
        </el-button>
        <el-button 
          type="primary" 
          :loading="refreshing"
          @click="refreshData"
        >
          <el-icon><Refresh /></el-icon>
          {{ refreshing ? '刷新中...' : '手动刷新' }}
        </el-button>
      </div>
    </div>



    <!-- 股票列表 -->
    <div class="stock-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>股票列表 ({{ stocks.length }}只)</span>
          </div>
        </template>
        
        <el-table 
          :data="paginatedStocks" 
          :loading="loading || refreshing"
          :element-loading-text="refreshing ? '正在刷新数据...' : '正在加载数据...'"
          stripe 
          style="width: 100%"
          height="600"
        >
          <el-table-column prop="code" label="股票代码" width="100" fixed="left" />
          <el-table-column prop="name" label="股票名称" width="120" fixed="left" />
          <el-table-column prop="industry" label="行业板块" width="120">
            <template #default="{ row }">
              <span>{{ row.industry || '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="listDate" label="上市时间" width="100">
            <template #default="{ row }">
              <span>{{ row.listDate || '--' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="currentPrice" label="现价" width="80">
            <template #default="{ row }">
              <span :class="getPriceClass(row.changePercent)">{{ formatPrice(row.currentPrice) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="涨跌幅" width="90">
            <template #default="{ row }">
              <span :class="getPriceClass(row.changePercent)">{{ formatPercent(row.changePercent) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="changeAmount" label="涨跌额" width="80">
            <template #default="{ row }">
              <span :class="getPriceClass(row.changePercent)">{{ formatPrice(row.changeAmount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="100">
            <template #default="{ row }">
              <span>{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnover" label="成交额" width="100">
            <template #default="{ row }">
              <span>{{ formatAmount(row.turnover) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pe" label="市盈率" width="80">
            <template #default="{ row }">
              <span>{{ formatRatio(row.pe) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="pb" label="市净率" width="80">
            <template #default="{ row }">
              <span>{{ formatRatio(row.pb) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="marketCap" label="总市值" width="100">
            <template #default="{ row }">
              <span>{{ formatAmount(row.marketCap) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnoverRate" label="换手率" width="80">
            <template #default="{ row }">
              <span>{{ formatPercent(row.turnoverRate) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="80">
            <template #default="{ row }">
              <span>{{ formatPercent(row.amplitude) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="market" label="市场" width="80" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  plain
                  :icon="Star" 
                  @click="toggleWatchlist(row)"
                  class="action-btn watchlist-btn"
                  :class="{ 'in-watchlist': isInWatchlist(row.code) }"
                >
                  {{ isInWatchlist(row.code) ? '已自选' : '自选' }}
                </el-button>
                <el-button 
                  size="small" 
                  type="info" 
                  :icon="View" 
                  @click="viewStockDetail(row)"
                  class="action-btn"
                >
                  详情
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[50, 100, 200, 500]"
            :total="stocks.length"
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Star, View } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { stocksAPI } from '@/services/api'

interface Stock {
  code: string
  name: string
  industry: string
  market: string
  listDate?: string
  // 新增股票常用数据字段
  currentPrice?: number    // 现价
  changePercent?: number   // 涨跌幅(%)
  changeAmount?: number    // 涨跌额
  volume?: number          // 成交量(手)
  turnover?: number        // 成交额(万元)
  pe?: number              // 市盈率
  pb?: number              // 市净率
  marketCap?: number       // 总市值(万元)
  turnoverRate?: number    // 换手率(%)
  amplitude?: number       // 振幅(%)
}

// 路由
const router = useRouter()

// 缓存相关常量
const CACHE_KEY = 'stock_overview_data'
const CACHE_EXPIRY_KEY = 'stock_overview_expiry'
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存时间

const loading = ref(false)
const refreshing = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(100)
const autoRefresh = ref(true)
const refreshInterval = ref<number | null>(null)
const lastUpdateTime = ref<string>('')
const fromCache = ref(false)
const cacheTime = ref<string>('')
const countdown = ref(30)
const countdownInterval = ref<number | null>(null)
const isFromLocalCache = ref(false) // 标识数据是否来自本地缓存

const stocks = ref<Stock[]>([])
const watchlistStocks = ref<Set<string>>(new Set()) // 自选股票代码集合

const paginatedStocks = computed(() => {
  let filtered = [...stocks.value]
  
  // 搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(stock => 
      stock.code.toLowerCase().includes(keyword) || 
      stock.name.toLowerCase().includes(keyword)
    )
  }
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

// 缓存相关函数
const saveToCache = (data: Stock[], serverFromCache: boolean, serverCacheTime: string) => {
  try {
    const cacheData = {
      stocks: data,
      timestamp: Date.now(),
      serverFromCache,
      serverCacheTime,
      lastUpdateTime: new Date().toLocaleString()
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
    localStorage.setItem(CACHE_EXPIRY_KEY, (Date.now() + CACHE_DURATION).toString())
  } catch (error) {
    console.warn('保存缓存失败:', error)
  }
}

const loadFromCache = (): { stocks: Stock[], serverFromCache: boolean, serverCacheTime: string, lastUpdateTime: string } | null => {
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    const expiry = localStorage.getItem(CACHE_EXPIRY_KEY)
    
    if (!cached || !expiry) return null
    
    // 检查缓存是否过期
    if (Date.now() > parseInt(expiry)) {
      localStorage.removeItem(CACHE_KEY)
      localStorage.removeItem(CACHE_EXPIRY_KEY)
      return null
    }
    
    const cacheData = JSON.parse(cached)
    return {
      stocks: cacheData.stocks || [],
      serverFromCache: cacheData.serverFromCache || false,
      serverCacheTime: cacheData.serverCacheTime || '',
      lastUpdateTime: cacheData.lastUpdateTime || ''
    }
  } catch (error) {
    console.warn('读取缓存失败:', error)
    return null
  }
}

const isCacheValid = (): boolean => {
  const expiry = localStorage.getItem(CACHE_EXPIRY_KEY)
  return expiry ? Date.now() < parseInt(expiry) : false
}

// 加载自选股票列表
const loadWatchlistStocks = async () => {
  try {
    const response = await stocksAPI.getWatchlist()
    if (response.data.success) {
      const watchlistCodes = response.data.data.data.map((item: any) => item.code)
      watchlistStocks.value = new Set(watchlistCodes)
    }
  } catch (error) {
    console.error('获取自选股票列表失败:', error)
  }
}

const loadStockData = async (isRefresh = false, forceFromServer = false) => {
  // 如果不是强制刷新且不是从服务器强制获取，先尝试从本地缓存加载
  if (!isRefresh && !forceFromServer && isCacheValid()) {
    const cachedData = loadFromCache()
    if (cachedData) {
      stocks.value = cachedData.stocks
      fromCache.value = cachedData.serverFromCache
      cacheTime.value = cachedData.serverCacheTime
      lastUpdateTime.value = cachedData.lastUpdateTime
      isFromLocalCache.value = true
      
      ElMessage.success(`从缓存加载股票数据，共${cachedData.stocks.length}只股票 📋`)
      
      // 在后台异步更新数据
      setTimeout(() => {
        loadStockData(false, true)
      }, 100)
      return
    }
  }
  
  if (isRefresh) {
    refreshing.value = true
  } else {
    loading.value = true
  }
  
  try {
    // 调用后端API获取全部股票基础信息，设置较大的page_size以获取所有股票
    const response = await fetch('/api/v1/stocks/overview/?page_size=10000')
    if (!response.ok) {
      throw new Error('Failed to fetch stock data')
    }
    
    const data = await response.json()
    
    // 转换后端数据格式，包含新增的股票常用数据字段
    const stockData: Stock[] = data.data.stocks.map((item: any) => {
      return {
        code: item.code,
        name: item.name,
        industry: item.industry || '未分类',
        market: item.market || getMarketName(item.code),
        listDate: item.listDate || '未知',
        // 新增字段暂时为空，等待后续数据源补充
        currentPrice: undefined,
        changePercent: undefined,
        changeAmount: undefined,
        volume: undefined,
        turnover: undefined,
        pe: undefined,
        pb: undefined,
        marketCap: undefined,
        turnoverRate: undefined,
        amplitude: undefined
      }
    })
    
    stocks.value = stockData
    
    // 更新缓存信息
    const serverFromCache = data.data.from_cache || false
    const serverCacheTime = data.data.cache_time || ''
    fromCache.value = serverFromCache
    cacheTime.value = serverCacheTime
    lastUpdateTime.value = new Date().toLocaleString()
    isFromLocalCache.value = false
    
    // 保存到本地缓存
    saveToCache(stockData, serverFromCache, serverCacheTime)
    
    const cacheStatus = isFromLocalCache.value ? '' : (fromCache.value ? '(来自服务器缓存)' : '')
    const message = isRefresh ? 
      `数据刷新成功，共${stockData.length}只股票${cacheStatus}` :
      forceFromServer ? 
        `后台更新完成，共${stockData.length}只股票${cacheStatus}` :
        `股票数据加载成功，共${stockData.length}只股票${cacheStatus}`
    
    if (!forceFromServer) {
      ElMessage.success(message)
    }
  } catch (error) {
    console.error('加载股票数据失败:', error)
    // 如果网络请求失败，尝试从缓存加载
    if (!isRefresh && !forceFromServer) {
      const cachedData = loadFromCache()
      if (cachedData) {
        stocks.value = cachedData.stocks
        fromCache.value = cachedData.serverFromCache
        cacheTime.value = cachedData.serverCacheTime
        lastUpdateTime.value = cachedData.lastUpdateTime
        isFromLocalCache.value = true
        ElMessage.warning(`网络请求失败，已加载缓存数据，共${cachedData.stocks.length}只股票 📋`)
        return
      }
    }
    if (!forceFromServer) {
      ElMessage.error('加载股票数据失败')
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// 根据股票代码判断市场
const getMarketName = (code: string): string => {
  if (code.startsWith('60') || code.startsWith('68')) {
    return code.startsWith('68') ? '科创板' : '沪市主板'
  } else if (code.startsWith('00')) {
    return '深市主板'
  } else if (code.startsWith('30')) {
    return '创业板'
  } else if (code.startsWith('8') || code.startsWith('4')) {
    return '北交所'
  }
  return '其他'
}

const searchStocks = () => {
  // 搜索功能已集成到计算属性中
}

const refreshData = () => {
  loadStockData(true)
  resetCountdown()
}

// 自动刷新相关函数
const startAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
  
  refreshInterval.value = setInterval(() => {
    if (autoRefresh.value) {
      loadStockData(true)
      resetCountdown()
    }
  }, 30000) // 30秒
  
  startCountdown()
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
    countdownInterval.value = null
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startCountdown = () => {
  countdown.value = 30
  countdownInterval.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = 30
    }
  }, 1000)
}

const resetCountdown = () => {
  countdown.value = 30
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 格式化函数
const formatPrice = (price?: number): string => {
  if (price === undefined || price === null) return '--'
  return price.toFixed(2)
}

const formatPercent = (percent?: number): string => {
  if (percent === undefined || percent === null) return '--'
  return `${percent.toFixed(2)}%`
}

const formatVolume = (volume?: number): string => {
  if (volume === undefined || volume === null) return '--'
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万手`
  }
  return `${volume}手`
}

const formatAmount = (amount?: number): string => {
  if (amount === undefined || amount === null) return '--'
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toFixed(2)
}

const formatRatio = (ratio?: number): string => {
  if (ratio === undefined || ratio === null || ratio <= 0) return '--'
  return ratio.toFixed(2)
}

// 价格颜色样式
const getPriceClass = (changePercent?: number): string => {
  if (changePercent === undefined || changePercent === null) return ''
  if (changePercent > 0) return 'positive'
  if (changePercent < 0) return 'negative'
  return 'neutral'
}

// 判断股票是否在自选列表中
const isInWatchlist = (stockCode: string): boolean => {
  return watchlistStocks.value.has(stockCode)
}

// 操作函数 - 切换自选状态
const toggleWatchlist = async (stock: Stock) => {
  const inWatchlist = isInWatchlist(stock.code)
  
  if (inWatchlist) {
    // 从自选中移除
    await removeFromWatchlist(stock)
  } else {
    // 添加到自选
    await addToWatchlist(stock)
  }
}

const addToWatchlist = async (stock: Stock) => {
  try {
    const response = await stocksAPI.addToWatchlist({
      stock_code: stock.code,
      add_price: stock.currentPrice || 0,
      notes: `从股票概览添加 - ${new Date().toLocaleString()}`
    })
    
    if (response.data.success) {
      watchlistStocks.value.add(stock.code)
      ElMessage.success(`${stock.name} 已加入自选清单`)
    } else {
      ElMessage.error(response.data.message || '加入自选失败')
    }
  } catch (error: any) {
    const message = error.response?.data?.message || '加入自选失败'
    ElMessage.error(message)
  }
}

const removeFromWatchlist = async (stock: Stock) => {
  try {
    const response = await stocksAPI.removeFromWatchlist({
      stock_code: stock.code
    })
    
    if (response.data.success) {
      watchlistStocks.value.delete(stock.code)
      ElMessage.success(`${stock.name} 已从自选清单移除`)
    } else {
      ElMessage.error(response.data.message || '移除自选失败')
    }
  } catch (error: any) {
    const message = error.response?.data?.message || '移除自选失败'
    ElMessage.error(message)
  }
}

const viewStockDetail = (stock: Stock) => {
  // 跳转到股票详情页面
  router.push({
    name: 'StockDetail',
    params: { stockCode: stock.code },
    query: { name: stock.name }
  })
}

onMounted(() => {
  loadStockData()
  loadWatchlistStocks()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.stock-overview {
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
  flex-wrap: wrap;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-right: 15px;
  font-size: 12px;
}

.update-time {
  color: #606266;
}

.cache-status {
  color: #67c23a;
  font-weight: 500;
}

.countdown {
  color: #409eff;
  font-weight: 500;
}

.market-summary {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-time {
  font-size: 12px;
  color: #909399;
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  height: 80px;
}

.summary-icon {
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

.summary-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.summary-icon.rising {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.summary-icon.falling {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.summary-icon.flat {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.summary-icon.limit-up {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.summary-icon.limit-down {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
}

.filter-section {
  margin-bottom: 20px;
}

.stock-table {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.pagination-container {
  text-align: right;
  margin-top: 15px;
}

.stock-detail {
  padding: 20px;
}

.detail-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.stock-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.current-price {
  font-size: 24px;
  font-weight: bold;
}

.change-info {
  font-size: 16px;
  font-weight: bold;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  font-size: 14px;
  color: #606266;
}

.detail-item .value {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
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

.limit-up-color {
  color: #ff4757;
}

.limit-down-color {
  color: #2ed573;
}

/* 新增价格颜色样式 */
.positive {
  color: #f56c6c;
  font-weight: bold;
}

.negative {
  color: #67c23a;
  font-weight: bold;
}

.neutral {
  color: #909399;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-btn {
  min-width: 60px;
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-btn .el-icon {
  margin-right: 2px;
}

/* 自选按钮样式 */
.watchlist-btn {
  background-color: #f8f9fa !important;
  border-color: #dee2e6 !important;
  color: #6c757d !important;
  font-weight: 500;
}

.watchlist-btn:hover {
  background-color: #e9ecef !important;
  border-color: #adb5bd !important;
  color: #495057 !important;
}

.watchlist-btn.in-watchlist {
  background-color: #fff5f5 !important;
  border-color: #fecaca !important;
  color: #dc2626 !important;
}

.watchlist-btn.in-watchlist:hover {
  background-color: #fef2f2 !important;
  border-color: #fca5a5 !important;
  color: #b91c1c !important;
}

/* 缓存状态样式 */
.cache-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 10px;
}

.local-cache {
  background-color: #e1f3d8;
  color: #67c23a;
  border: 1px solid #b3d8a4;
}

.server-cache {
  background-color: #ecf5ff;
  color: #409eff;
  border: 1px solid #b3d8ff;
}

.countdown {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.update-time {
  color: #606266;
  font-size: 12px;
}
</style>