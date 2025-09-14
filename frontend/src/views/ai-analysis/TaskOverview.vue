<template>
  <div class="task-overview">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalTasks }}</div>
          <div class="stat-label">AI分析任务总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon today">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.todayTasks }}</div>
          <div class="stat-label">今日分析总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.successRate }}%</div>
          <div class="stat-label">AI分析成功比例</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon accuracy">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.topModel }}</div>
          <div class="stat-label">模型准确性排行</div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filters">
      <div class="filter-group">
        <el-select v-model="statusFilter" placeholder="任务状态" @change="loadTasks">
          <el-option label="全部状态" value="" />
          <el-option label="进行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="超时" value="timeout" />
        </el-select>
      </div>
      
      <div class="filter-group">
        <el-input
          v-model="searchQuery"
          placeholder="搜索股票代码"
          @input="loadTasks"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="filter-group">
        <el-button type="primary" @click="loadTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 任务记录表格 -->
    <div class="table-container">
      <el-table
        :data="tasks"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="stock_code" label="股票代码" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.stock_code }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="任务状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="duration" label="任务耗时" width="120">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="summary" label="分析总结" min-width="200">
          <template #default="{ row }">
            <div class="summary-text">{{ row.summary || '暂无总结' }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="分析详情" width="120">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(row)"
              :disabled="!row.detail"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="分析详情"
      width="80%"
      :before-close="closeDetail"
    >
      <div class="detail-content">
        <div v-if="selectedTask && selectedTask.detail" v-html="renderMarkdown(selectedTask.detail)"></div>
        <div v-else-if="selectedTask">暂无详细信息</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  Calendar,
  SuccessFilled,
  TrendCharts,
  Search,
  Refresh
} from '@element-plus/icons-vue'
// import { marked } from 'marked'
// import apiClient from '../../services/apiClient'

// 响应式数据
const loading = ref(false)
const stats = ref({
  totalTasks: 0,
  todayTasks: 0,
  successRate: 0,
  topModel: 'GPT-4'
})

interface Task {
  id: number
  stock_code: string
  start_time: string
  status: string
  duration: number | null
  summary: string | null
  detail: string | null
}

const tasks = ref<Task[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const searchQuery = ref('')

const detailVisible = ref(false)
const selectedTask = ref<Task | null>(null)

// 方法
const loadStats = async () => {
  try {
    // 暂时使用模拟数据
    stats.value = {
      totalTasks: 156,
      todayTasks: 23,
      successRate: 87.5,
      topModel: 'GPT-4'
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadTasks = async () => {
  loading.value = true
  try {
    // 模拟数据，实际应该调用API
    const mockTasks = [
      {
        id: 1,
        stock_code: '000001',
        start_time: new Date().toISOString(),
        status: 'completed',
        duration: 120000, // 2分钟
        summary: '该股票呈现上涨趋势，建议关注',
        detail: '# 分析报告\n\n## 技术指标\n- RSI: 65\n- MACD: 向上\n\n## 结论\n建议买入'
      },
      {
        id: 2,
        stock_code: '000002',
        start_time: new Date(Date.now() - 3600000).toISOString(),
        status: 'running',
        duration: null,
        summary: null,
        detail: null
      },
      {
        id: 3,
        stock_code: '600000',
        start_time: new Date(Date.now() - 7200000).toISOString(),
        status: 'timeout',
        duration: 300000, // 5分钟
        summary: '分析超时',
        detail: null
      }
    ]
    
    // 应用筛选
    let filteredTasks = mockTasks
    if (statusFilter.value) {
      filteredTasks = filteredTasks.filter(task => task.status === statusFilter.value)
    }
    if (searchQuery.value) {
      filteredTasks = filteredTasks.filter(task => 
        task.stock_code.includes(searchQuery.value)
      )
    }
    
    tasks.value = filteredTasks
    total.value = filteredTasks.length
  } catch (error) {
    console.error('加载任务数据失败:', error)
    ElMessage.error('加载任务数据失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    running: 'warning',
    completed: 'success',
    timeout: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    running: '进行中',
    completed: '已完成',
    timeout: '超时'
  }
  return statusMap[status] || status
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const formatDuration = (duration: number) => {
  if (!duration) return '-'
  const minutes = Math.floor(duration / 60000)
  const seconds = Math.floor((duration % 60000) / 1000)
  return `${minutes}分${seconds}秒`
}

const viewDetail = (task: Task) => {
  selectedTask.value = task
  detailVisible.value = true
}

const closeDetail = () => {
  detailVisible.value = false
  selectedTask.value = null
}

const renderMarkdown = (content: string) => {
  if (!content) return ''
  // 简单的markdown渲染，实际项目中可以使用marked库
  return content.replace(/\n/g, '<br>').replace(/# (.*)/g, '<h1>$1</h1>').replace(/## (.*)/g, '<h2>$1</h2>')
}

// 生命周期
onMounted(() => {
  loadStats()
  loadTasks()
})
</script>

<style scoped>
.task-overview {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-icon.today {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-icon.success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-icon.accuracy {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
}

.table-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.summary-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.detail-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    margin-bottom: 10px;
  }
}
</style>