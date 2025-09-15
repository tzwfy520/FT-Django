<template>
  <div class="history-data-table">
    <div class="table-header">
      <span>历史数据 ({{ pagination.total }}条)</span>
      <div class="table-actions">
        <el-button size="small" @click="downloadData">
          <el-icon><Download /></el-icon>
          下载数据
        </el-button>
        <el-button size="small" @click="analyzeData">
          <el-icon><DataAnalysis /></el-icon>
          数据分析
        </el-button>
      </div>
    </div>
    
    <el-table 
      :data="data" 
      stripe 
      height="400"
      v-loading="loading"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="date" label="日期" width="120" sortable="custom" />
      <el-table-column prop="open_price" label="开盘价" width="100" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatPrice(row.open_price) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="high_price" label="最高价" width="100" sortable="custom">
        <template #default="{ row }">
          <span class="positive">{{ formatPrice(row.high_price) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="low_price" label="最低价" width="100" sortable="custom">
        <template #default="{ row }">
          <span class="negative">{{ formatPrice(row.low_price) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="close_price" label="收盘价" width="100" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatPrice(row.close_price) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable="custom">
        <template #default="{ row }">
          <span :class="getChangeClass(row.change_percent)">
            {{ formatChange(row.change_percent) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="change_amount" label="涨跌额" width="100" sortable="custom">
        <template #default="{ row }">
          <span :class="getChangeClass(row.change_amount)">
            {{ formatChangeAmount(row.change_amount) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="成交量" width="120" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatVolume(row.volume) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="turnover" label="成交额" width="120" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatAmount(row.turnover) }}万</span>
        </template>
      </el-table-column>
      <el-table-column prop="turnover_rate" label="换手率" width="100" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatPercent(row.turnover_rate) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="amplitude" label="振幅" width="100" sortable="custom">
        <template #default="{ row }">
          <span>{{ formatPercent(row.amplitude) }}</span>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 数据分析对话框 -->
    <el-dialog v-model="analysisDialog" title="数据分析" width="800px">
      <div v-if="analysisResult" class="analysis-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="analysis-section">
              <h4>基本统计</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="数据天数">{{ analysisResult.totalDays }}</el-descriptions-item>
                <el-descriptions-item label="最高价">{{ formatPrice(analysisResult.maxPrice) }}</el-descriptions-item>
                <el-descriptions-item label="最低价">{{ formatPrice(analysisResult.minPrice) }}</el-descriptions-item>
                <el-descriptions-item label="平均价">{{ formatPrice(analysisResult.avgPrice) }}</el-descriptions-item>
                <el-descriptions-item label="总成交量">{{ formatVolume(analysisResult.totalVolume) }}</el-descriptions-item>
                <el-descriptions-item label="平均成交量">{{ formatVolume(analysisResult.avgVolume) }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="analysis-section">
              <h4>涨跌统计</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="上涨天数">{{ analysisResult.risingDays }}</el-descriptions-item>
                <el-descriptions-item label="下跌天数">{{ analysisResult.fallingDays }}</el-descriptions-item>
                <el-descriptions-item label="平盘天数">{{ analysisResult.flatDays }}</el-descriptions-item>
                <el-descriptions-item label="上涨概率">{{ formatPercent(analysisResult.risingRate) }}</el-descriptions-item>
                <el-descriptions-item label="最大涨幅">{{ formatChange(analysisResult.maxRise) }}</el-descriptions-item>
                <el-descriptions-item label="最大跌幅">{{ formatChange(analysisResult.maxFall) }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
        </el-row>
        
        <div class="analysis-section">
          <h4>收益率分析</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">期间收益率</div>
                <div class="return-value" :class="getChangeClass(analysisResult.totalReturn)">
                  {{ formatChange(analysisResult.totalReturn) }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">年化收益率</div>
                <div class="return-value" :class="getChangeClass(analysisResult.annualizedReturn)">
                  {{ formatChange(analysisResult.annualizedReturn) }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="return-item">
                <div class="return-label">波动率</div>
                <div class="return-value">{{ formatPercent(analysisResult.volatility) }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="analysisDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportAnalysis">
          导出分析报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, DataAnalysis } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['page-change', 'size-change', 'sort-change'])

// 响应式数据
const analysisDialog = ref(false)
const analysisResult = ref(null)

// 方法
const handleSortChange = ({ prop, order }) => {
  emit('sort-change', { prop, order })
}

const handleSizeChange = (size) => {
  emit('size-change', size)
}

const handleCurrentChange = (page) => {
  emit('page-change', page)
}

const downloadData = () => {
  if (props.data.length === 0) {
    ElMessage.warning('暂无数据可下载')
    return
  }
  
  try {
    // 生成CSV数据
    const headers = ['日期', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅(%)', '涨跌额', '成交量', '成交额(万)', '换手率(%)', '振幅(%)']
    const csvContent = [headers.join(',')]
    
    props.data.forEach(row => {
      const csvRow = [
        row.date,
        formatPrice(row.open_price),
        formatPrice(row.high_price),
        formatPrice(row.low_price),
        formatPrice(row.close_price),
        row.change_percent || 0,
        row.change_amount || 0,
        row.volume || 0,
        formatAmount(row.turnover),
        row.turnover_rate || 0,
        row.amplitude || 0
      ]
      csvContent.push(csvRow.join(','))
    })
    
    // 创建下载链接
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `历史数据_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('数据下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('数据下载失败')
  }
}

const analyzeData = () => {
  if (props.data.length === 0) {
    ElMessage.warning('暂无数据可分析')
    return
  }
  
  try {
    const data = props.data
    const prices = data.map(item => item.close_price || 0)
    const changes = data.map(item => item.change_percent || 0)
    
    const totalDays = data.length
    const maxPrice = Math.max(...prices)
    const minPrice = Math.min(...prices)
    const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length
    const totalVolume = data.reduce((sum, item) => sum + (item.volume || 0), 0)
    const avgVolume = totalVolume / totalDays
    
    const risingDays = changes.filter(change => change > 0).length
    const fallingDays = changes.filter(change => change < 0).length
    const flatDays = changes.filter(change => change === 0).length
    const risingRate = (risingDays / totalDays) * 100
    
    const maxRise = Math.max(...changes)
    const maxFall = Math.min(...changes)
    
    // 计算收益率
    const firstPrice = prices[prices.length - 1]
    const lastPrice = prices[0]
    const totalReturn = firstPrice > 0 ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0
    const annualizedReturn = totalReturn * (365 / totalDays)
    
    // 计算波动率
    const avgChange = changes.reduce((sum, change) => sum + change, 0) / changes.length
    const variance = changes.reduce((sum, change) => sum + Math.pow(change - avgChange, 2), 0) / changes.length
    const volatility = Math.sqrt(variance)
    
    analysisResult.value = {
      totalDays,
      maxPrice,
      minPrice,
      avgPrice,
      totalVolume,
      avgVolume,
      risingDays,
      fallingDays,
      flatDays,
      risingRate,
      maxRise,
      maxFall,
      totalReturn,
      annualizedReturn,
      volatility
    }
    
    analysisDialog.value = true
  } catch (error) {
    console.error('数据分析失败:', error)
    ElMessage.error('数据分析失败')
  }
}

const exportAnalysis = () => {
  if (!analysisResult.value) return
  
  try {
    const result = analysisResult.value
    const reportContent = [
      '# 股票历史数据分析报告',
      '',
      '## 基本统计',
      `- 数据天数: ${result.totalDays}`,
      `- 最高价: ${formatPrice(result.maxPrice)}`,
      `- 最低价: ${formatPrice(result.minPrice)}`,
      `- 平均价: ${formatPrice(result.avgPrice)}`,
      `- 总成交量: ${formatVolume(result.totalVolume)}`,
      `- 平均成交量: ${formatVolume(result.avgVolume)}`,
      '',
      '## 涨跌统计',
      `- 上涨天数: ${result.risingDays}`,
      `- 下跌天数: ${result.fallingDays}`,
      `- 平盘天数: ${result.flatDays}`,
      `- 上涨概率: ${formatPercent(result.risingRate)}`,
      `- 最大涨幅: ${formatChange(result.maxRise)}`,
      `- 最大跌幅: ${formatChange(result.maxFall)}`,
      '',
      '## 收益率分析',
      `- 期间收益率: ${formatChange(result.totalReturn)}`,
      `- 年化收益率: ${formatChange(result.annualizedReturn)}`,
      `- 波动率: ${formatPercent(result.volatility)}`,
      '',
      `报告生成时间: ${new Date().toLocaleString()}`
    ]
    
    const blob = new Blob([reportContent.join('\n')], { type: 'text/markdown;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `数据分析报告_${new Date().toISOString().split('T')[0]}.md`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('分析报告导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('分析报告导出失败')
  }
}

// 工具函数
const formatPrice = (value) => {
  if (!value && value !== 0) return '--'
  return value.toFixed(2)
}

const formatChange = (value) => {
  if (!value && value !== 0) return '--'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

const formatChangeAmount = (value) => {
  if (!value && value !== 0) return '--'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}`
}

const formatVolume = (value) => {
  if (!value && value !== 0) return '--'
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `${(value / 10000).toFixed(2)}万`
  }
  return value.toString()
}

const formatAmount = (value) => {
  if (!value && value !== 0) return '--'
  return (value / 10000).toFixed(2)
}

const formatPercent = (value) => {
  if (!value && value !== 0) return '--'
  return `${value.toFixed(2)}%`
}

const getChangeClass = (value) => {
  if (!value && value !== 0) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}
</script>

<style scoped>
.history-data-table {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  text-align: right;
  margin-top: 15px;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

.analysis-content {
  padding: 20px 0;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.return-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.return-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.return-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
</style>