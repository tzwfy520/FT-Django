<template>
  <div class="dragon-tiger-list">
    <div class="page-header">
      <h2>龙虎榜</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadDragonTigerData"
        />
        <el-select v-model="listType" placeholder="榜单类型" @change="loadDragonTigerData">
          <el-option label="全部" value="all" />
          <el-option label="日涨幅偏离值达7%" value="deviation_7" />
          <el-option label="日换手率达20%" value="turnover_20" />
          <el-option label="日价格振幅达15%" value="amplitude_15" />
          <el-option label="连续三个交易日内收盘价格涨跌幅偏离值累计达20%" value="cumulative_20" />
        </el-select>
        <el-button type="primary" @click="loadDragonTigerData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <div class="summary-info">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="summary-item">
              <div class="summary-title">上榜股票数</div>
              <div class="summary-value">{{ summaryData.totalStocks }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="summary-item">
              <div class="summary-title">总成交额</div>
              <div class="summary-value">{{ summaryData.totalAmount }}亿</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="summary-item">
              <div class="summary-title">净买入额</div>
              <div class="summary-value positive">+{{ summaryData.netBuyAmount }}亿</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="summary-item">
              <div class="summary-title">活跃营业部</div>
              <div class="summary-value">{{ summaryData.activeBranches }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="dragon-tiger-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>龙虎榜详情</span>
            <div class="table-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索股票代码或名称"
                style="width: 200px;"
                clearable
                @input="filterData"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table
          :data="filteredData"
          v-loading="loading"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'netBuyAmount', order: 'descending' }"
        >
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expand-content">
                <h4>买入前五名</h4>
                <el-table :data="row.buyTop5" size="small">
                  <el-table-column prop="rank" label="排名" width="60" />
                  <el-table-column prop="branch" label="营业部" />
                  <el-table-column prop="buyAmount" label="买入金额(万)" width="120" />
                  <el-table-column prop="sellAmount" label="卖出金额(万)" width="120" />
                  <el-table-column prop="netAmount" label="净额(万)" width="100">
                    <template #default="{ row: buyRow }">
                      <span :class="getAmountClass(buyRow.netAmount)">{{ formatAmount(buyRow.netAmount) }}</span>
                    </template>
                  </el-table-column>
                </el-table>
                
                <h4 style="margin-top: 20px;">卖出前五名</h4>
                <el-table :data="row.sellTop5" size="small">
                  <el-table-column prop="rank" label="排名" width="60" />
                  <el-table-column prop="branch" label="营业部" />
                  <el-table-column prop="buyAmount" label="买入金额(万)" width="120" />
                  <el-table-column prop="sellAmount" label="卖出金额(万)" width="120" />
                  <el-table-column prop="netAmount" label="净额(万)" width="100">
                    <template #default="{ row: sellRow }">
                      <span :class="getAmountClass(sellRow.netAmount)">{{ formatAmount(sellRow.netAmount) }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="stockCode" label="股票代码" width="100" />
          <el-table-column prop="stockName" label="股票名称" width="120">
            <template #default="{ row }">
              <el-button type="text" @click="viewStockDetail(row.stockCode)">{{ row.stockName }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="closePrice" label="收盘价" width="80" />
          <el-table-column prop="changePercent" label="涨跌幅" width="80" sortable>
            <template #default="{ row }">
              <span :class="getChangeClass(row.changePercent)">{{ row.changePercent }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="turnoverRate" label="换手率" width="80" sortable>
            <template #default="{ row }">
              {{ row.turnoverRate }}%
            </template>
          </el-table-column>
          <el-table-column prop="amplitude" label="振幅" width="80" sortable>
            <template #default="{ row }">
              {{ row.amplitude }}%
            </template>
          </el-table-column>
          <el-table-column prop="totalAmount" label="龙虎榜成交额" width="120" sortable>
            <template #default="{ row }">
              {{ (row.totalAmount / 10000).toFixed(2) }}万
            </template>
          </el-table-column>
          <el-table-column prop="netBuyAmount" label="净买入额" width="100" sortable>
            <template #default="{ row }">
              <span :class="getAmountClass(row.netBuyAmount)">{{ formatAmount(row.netBuyAmount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="上榜原因" min-width="200">
            <template #default="{ row }">
              <el-tag :type="getReasonType(row.reason)" size="small">{{ row.reason }}</el-tag>
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
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>热门营业部</span>
            </template>
            <el-table :data="hotBranches" size="small">
              <el-table-column prop="rank" label="排名" width="60" />
              <el-table-column prop="branch" label="营业部" />
              <el-table-column prop="appearCount" label="上榜次数" width="100" />
              <el-table-column prop="totalAmount" label="总成交额(万)" width="120" />
              <el-table-column prop="netAmount" label="净买入(万)" width="100">
                <template #default="{ row }">
                  <span :class="getAmountClass(row.netAmount)">{{ formatAmount(row.netAmount) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>板块分析</span>
            </template>
            <div ref="sectorChartContainer" class="chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface DragonTigerItem {
  stockCode: string
  stockName: string
  closePrice: number
  changePercent: number
  turnoverRate: number
  amplitude: number
  totalAmount: number
  netBuyAmount: number
  reason: string
  buyTop5: BranchData[]
  sellTop5: BranchData[]
}

interface BranchData {
  rank: number
  branch: string
  buyAmount: number
  sellAmount: number
  netAmount: number
}

interface HotBranch {
  rank: number
  branch: string
  appearCount: number
  totalAmount: number
  netAmount: number
}

const loading = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const listType = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

const sectorChartContainer = ref<HTMLElement>()
const sectorChartInstance = ref<echarts.ECharts>()

const dragonTigerData = ref<DragonTigerItem[]>([])
const filteredData = ref<DragonTigerItem[]>([])

const summaryData = ref({
  totalStocks: 45,
  totalAmount: 156.8,
  netBuyAmount: 23.5,
  activeBranches: 128
})

const hotBranches = ref<HotBranch[]>([
  { rank: 1, branch: '中信证券北京总部', appearCount: 8, totalAmount: 12580, netAmount: 3450 },
  { rank: 2, branch: '华泰证券上海分公司', appearCount: 6, totalAmount: 9870, netAmount: -1230 },
  { rank: 3, branch: '国泰君安深圳分公司', appearCount: 5, totalAmount: 8760, netAmount: 2180 },
  { rank: 4, branch: '招商证券深圳蛇口', appearCount: 4, totalAmount: 7650, netAmount: 890 },
  { rank: 5, branch: '广发证券广州分公司', appearCount: 4, totalAmount: 6540, netAmount: -560 }
])

const loadDragonTigerData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟数据
    const mockData: DragonTigerItem[] = []
    const reasons = [
      '日涨幅偏离值达7%',
      '日换手率达20%',
      '日价格振幅达15%',
      '连续三个交易日内收盘价格涨跌幅偏离值累计达20%'
    ]
    
    for (let i = 0; i < 45; i++) {
      const changePercent = (Math.random() - 0.3) * 20
      const buyTop5: BranchData[] = []
      const sellTop5: BranchData[] = []
      
      // 生成买入前五名
      for (let j = 0; j < 5; j++) {
        const buyAmount = Math.random() * 5000 + 1000
        const sellAmount = Math.random() * 2000
        buyTop5.push({
          rank: j + 1,
          branch: `营业部${i}-${j + 1}`,
          buyAmount: Number(buyAmount.toFixed(2)),
          sellAmount: Number(sellAmount.toFixed(2)),
          netAmount: Number((buyAmount - sellAmount).toFixed(2))
        })
      }
      
      // 生成卖出前五名
      for (let j = 0; j < 5; j++) {
        const buyAmount = Math.random() * 1000
        const sellAmount = Math.random() * 5000 + 1000
        sellTop5.push({
          rank: j + 1,
          branch: `营业部${i + 50}-${j + 1}`,
          buyAmount: Number(buyAmount.toFixed(2)),
          sellAmount: Number(sellAmount.toFixed(2)),
          netAmount: Number((buyAmount - sellAmount).toFixed(2))
        })
      }
      
      const totalBuyAmount = buyTop5.reduce((sum, item) => sum + item.buyAmount, 0)
      const totalSellAmount = sellTop5.reduce((sum, item) => sum + item.sellAmount, 0)
      
      mockData.push({
        stockCode: `${String(i + 1).padStart(6, '0')}`,
        stockName: `股票${i + 1}`,
        closePrice: Number((Math.random() * 100 + 10).toFixed(2)),
        changePercent: Number(changePercent.toFixed(2)),
        turnoverRate: Number((Math.random() * 30 + 5).toFixed(2)),
        amplitude: Number((Math.random() * 20 + 5).toFixed(2)),
        totalAmount: Number(((totalBuyAmount + totalSellAmount) * 10000).toFixed(0)),
        netBuyAmount: Number(((totalBuyAmount - totalSellAmount) / 10).toFixed(2)),
        reason: reasons[Math.floor(Math.random() * reasons.length)],
        buyTop5,
        sellTop5
      })
    }
    
    dragonTigerData.value = mockData
    filteredData.value = mockData
    totalRecords.value = mockData.length
    
    await nextTick()
    updateSectorChart()
    
    ElMessage.success('龙虎榜数据加载成功')
  } catch (error) {
    ElMessage.error('加载龙虎榜数据失败')
  } finally {
    loading.value = false
  }
}

const filterData = () => {
  if (!searchKeyword.value) {
    filteredData.value = dragonTigerData.value
  } else {
    filteredData.value = dragonTigerData.value.filter(item => 
      item.stockCode.includes(searchKeyword.value) || 
      item.stockName.includes(searchKeyword.value)
    )
  }
}

const updateSectorChart = () => {
  if (!sectorChartContainer.value) return
  
  if (!sectorChartInstance.value) {
    sectorChartInstance.value = echarts.init(sectorChartContainer.value)
  }
  
  const sectorData = [
    { name: '科技股', value: 15, itemStyle: { color: '#5470c6' } },
    { name: '医药股', value: 8, itemStyle: { color: '#91cc75' } },
    { name: '新能源', value: 12, itemStyle: { color: '#fac858' } },
    { name: '消费股', value: 6, itemStyle: { color: '#ee6666' } },
    { name: '金融股', value: 4, itemStyle: { color: '#73c0de' } }
  ]
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '板块分布',
        type: 'pie',
        radius: '60%',
        data: sectorData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  sectorChartInstance.value.setOption(option)
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadDragonTigerData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadDragonTigerData()
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
}

const formatAmount = (amount: number): string => {
  const sign = amount >= 0 ? '+' : ''
  return sign + amount.toFixed(2)
}

const getAmountClass = (amount: number): string => {
  return amount > 0 ? 'positive' : amount < 0 ? 'negative' : 'neutral'
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

const getReasonType = (reason: string): string => {
  if (reason.includes('涨幅')) return 'danger'
  if (reason.includes('换手')) return 'warning'
  if (reason.includes('振幅')) return 'info'
  return 'success'
}

onMounted(() => {
  loadDragonTigerData()
})
</script>

<style scoped>
.dragon-tiger-list {
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

.summary-info {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
}

.summary-item {
  padding: 10px;
}

.summary-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
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

.dragon-tiger-table {
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

.expand-content {
  padding: 20px;
  background-color: #f8f9fa;
}

.expand-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.analysis-section {
  margin-bottom: 20px;
}
</style>