<template>
  <div class="task-execution-records">
    <!-- 筛选条件 -->
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>执行状态:</label>
          <select v-model="filters.status" class="filter-select">
            <option value="">全部状态</option>
            <option value="success">成功</option>
            <option value="failed">失败</option>
            <option value="running">运行中</option>
            <option value="pending">等待中</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>任务类型:</label>
          <select v-model="filters.taskType" class="filter-select">
            <option value="">全部类型</option>
            <option value="periodic">周期任务</option>
            <option value="scheduled">定时任务</option>
            <option value="immediate">立即任务</option>
            <option value="special">特殊任务</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>时间范围:</label>
          <select v-model="filters.timeRange" class="filter-select">
            <option value="">全部时间</option>
            <option value="today">今天</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="custom">自定义</option>
          </select>
        </div>
        
        <div class="filter-group" v-if="filters.timeRange === 'custom'">
          <label>开始时间:</label>
          <input 
            type="datetime-local" 
            v-model="filters.startTime" 
            class="filter-input"
          >
        </div>
        
        <div class="filter-group" v-if="filters.timeRange === 'custom'">
          <label>结束时间:</label>
          <input 
            type="datetime-local" 
            v-model="filters.endTime" 
            class="filter-input"
          >
        </div>
      </div>
      
      <div class="filter-row">
        <div class="filter-group">
          <label>任务名称:</label>
          <input 
            type="text" 
            v-model="filters.taskName" 
            placeholder="搜索任务名称"
            class="filter-input"
          >
        </div>
        
        <div class="filter-group">
          <label>执行结果:</label>
          <select v-model="filters.result" class="filter-select">
            <option value="">全部结果</option>
            <option value="success">执行成功</option>
            <option value="error">执行错误</option>
            <option value="timeout">执行超时</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button @click="applyFilters" class="btn-primary">筛选</button>
          <button @click="resetFilters" class="btn-secondary">重置</button>
          <button @click="exportRecords" class="btn-export">导出</button>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总执行次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.success }}</div>
        <div class="stat-label">成功次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.failed }}</div>
        <div class="stat-label">失败次数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.successRate }}%</div>
        <div class="stat-label">成功率</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.avgDuration }}s</div>
        <div class="stat-label">平均耗时</div>
      </div>
    </div>
    
    <!-- 执行记录表格 -->
    <div class="records-table">
      <div class="table-header">
        <h3>执行记录</h3>
        <div class="table-actions">
          <button @click="refreshRecords" class="btn-refresh">刷新</button>
        </div>
      </div>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th @click="sortBy('taskName')" class="sortable">
                任务名称
                <span class="sort-icon" :class="getSortClass('taskName')">↕</span>
              </th>
              <th @click="sortBy('taskType')" class="sortable">
                任务类型
                <span class="sort-icon" :class="getSortClass('taskType')">↕</span>
              </th>
              <th @click="sortBy('status')" class="sortable">
                执行状态
                <span class="sort-icon" :class="getSortClass('status')">↕</span>
              </th>
              <th @click="sortBy('startTime')" class="sortable">
                开始时间
                <span class="sort-icon" :class="getSortClass('startTime')">↕</span>
              </th>
              <th @click="sortBy('endTime')" class="sortable">
                结束时间
                <span class="sort-icon" :class="getSortClass('endTime')">↕</span>
              </th>
              <th @click="sortBy('duration')" class="sortable">
                执行耗时
                <span class="sort-icon" :class="getSortClass('duration')">↕</span>
              </th>
              <th>执行结果</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in paginatedRecords" :key="record.id">
              <td>{{ record.taskName }}</td>
              <td>
                <span class="task-type-badge" :class="record.taskType">
                  {{ getTaskTypeLabel(record.taskType) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="record.status">
                  {{ getStatusLabel(record.status) }}
                </span>
              </td>
              <td>{{ formatDateTime(record.startTime) }}</td>
              <td>{{ record.endTime ? formatDateTime(record.endTime) : '-' }}</td>
              <td>{{ record.duration ? record.duration + 's' : '-' }}</td>
              <td>
                <span class="result-badge" :class="record.result">
                  {{ getResultLabel(record.result) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="viewDetails(record)" 
                    class="btn-action view"
                    title="查看详情"
                  >
                    👁️
                  </button>
                  <button 
                    @click="viewLogs(record)" 
                    class="btn-action logs"
                    title="查看日志"
                  >
                    📋
                  </button>
                  <button 
                    v-if="record.status === 'failed'"
                    @click="retryTask(record)" 
                    class="btn-action retry"
                    title="重新执行"
                  >
                    🔄
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination">
        <div class="pagination-info">
          显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredRecords.length) }} 条，
          共 {{ filteredRecords.length }} 条记录
        </div>
        <div class="pagination-controls">
          <button 
            @click="currentPage = 1" 
            :disabled="currentPage === 1"
            class="btn-page"
          >
            首页
          </button>
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="btn-page"
          >
            上一页
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="btn-page"
          >
            下一页
          </button>
          <button 
            @click="currentPage = totalPages" 
            :disabled="currentPage === totalPages"
            class="btn-page"
          >
            末页
          </button>
        </div>
      </div>
    </div>
    
    <!-- 详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>执行记录详情</h3>
          <button @click="closeDetailModal" class="btn-close">×</button>
        </div>
        <div class="modal-body" v-if="selectedRecord">
          <div class="detail-section">
            <h4>基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>任务名称:</label>
                <span>{{ selectedRecord.taskName }}</span>
              </div>
              <div class="detail-item">
                <label>任务类型:</label>
                <span>{{ getTaskTypeLabel(selectedRecord.taskType) }}</span>
              </div>
              <div class="detail-item">
                <label>执行状态:</label>
                <span class="status-badge" :class="selectedRecord.status">
                  {{ getStatusLabel(selectedRecord.status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>执行结果:</label>
                <span class="result-badge" :class="selectedRecord.result">
                  {{ getResultLabel(selectedRecord.result) }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h4>时间信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>开始时间:</label>
                <span>{{ formatDateTime(selectedRecord.startTime) }}</span>
              </div>
              <div class="detail-item">
                <label>结束时间:</label>
                <span>{{ selectedRecord.endTime ? formatDateTime(selectedRecord.endTime) : '未结束' }}</span>
              </div>
              <div class="detail-item">
                <label>执行耗时:</label>
                <span>{{ selectedRecord.duration ? selectedRecord.duration + '秒' : '计算中' }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedRecord.errorMessage">
            <h4>错误信息</h4>
            <div class="error-message">
              {{ selectedRecord.errorMessage }}
            </div>
          </div>
          
          <div class="detail-section" v-if="selectedRecord.taskArgs">
            <h4>任务参数</h4>
            <pre class="task-args">{{ JSON.stringify(selectedRecord.taskArgs, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 日志模态框 -->
    <div v-if="showLogModal" class="modal-overlay" @click="closeLogModal">
      <div class="modal-content log-modal" @click.stop>
        <div class="modal-header">
          <h3>执行日志</h3>
          <button @click="closeLogModal" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="log-content">
            <pre>{{ selectedRecord?.logs || '暂无日志' }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface ExecutionRecord {
  id: string
  taskId: string
  taskName: string
  taskType: 'periodic' | 'scheduled' | 'immediate' | 'special'
  status: 'pending' | 'running' | 'success' | 'failed'
  result: 'success' | 'error' | 'timeout' | 'cancelled'
  startTime: string
  endTime?: string
  duration?: number
  errorMessage?: string
  logs?: string
  taskArgs?: Record<string, any>
}

interface FilterOptions {
  status: string
  taskType: string
  timeRange: string
  startTime: string
  endTime: string
  taskName: string
  result: string
}

// 响应式数据
const records = ref<ExecutionRecord[]>([])
const loading = ref(false)
const showDetailModal = ref(false)
const showLogModal = ref(false)
const selectedRecord = ref<ExecutionRecord | null>(null)

// 筛选条件
const filters = ref<FilterOptions>({
  status: '',
  taskType: '',
  timeRange: '',
  startTime: '',
  endTime: '',
  taskName: '',
  result: ''
})

// 排序
const sortField = ref('startTime')
const sortOrder = ref<'asc' | 'desc'>('desc')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 统计信息
const stats = computed(() => {
  const total = filteredRecords.value.length
  const success = filteredRecords.value.filter(r => r.result === 'success').length
  const failed = filteredRecords.value.filter(r => r.result === 'error').length
  const successRate = total > 0 ? Math.round((success / total) * 100) : 0
  
  const durations = filteredRecords.value
    .filter(r => r.duration)
    .map(r => r.duration!)
  const avgDuration = durations.length > 0 
    ? Math.round(durations.reduce((a, b) => a + b, 0) / durations.length)
    : 0
  
  return {
    total,
    success,
    failed,
    successRate,
    avgDuration
  }
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let filtered = records.value
  
  // 状态筛选
  if (filters.value.status) {
    filtered = filtered.filter(r => r.status === filters.value.status)
  }
  
  // 任务类型筛选
  if (filters.value.taskType) {
    filtered = filtered.filter(r => r.taskType === filters.value.taskType)
  }
  
  // 执行结果筛选
  if (filters.value.result) {
    filtered = filtered.filter(r => r.result === filters.value.result)
  }
  
  // 任务名称搜索
  if (filters.value.taskName) {
    const query = filters.value.taskName.toLowerCase()
    filtered = filtered.filter(r => r.taskName.toLowerCase().includes(query))
  }
  
  // 时间范围筛选
  if (filters.value.timeRange) {
    const now = new Date()
    let startDate: Date
    
    switch (filters.value.timeRange) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        break
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1)
        break
      case 'custom':
        if (filters.value.startTime) {
          startDate = new Date(filters.value.startTime)
          filtered = filtered.filter(r => new Date(r.startTime) >= startDate)
        }
        if (filters.value.endTime) {
          const endDate = new Date(filters.value.endTime)
          filtered = filtered.filter(r => new Date(r.startTime) <= endDate)
        }
        return filtered
      default:
        return filtered
    }
    
    filtered = filtered.filter(r => new Date(r.startTime) >= startDate)
  }
  
  // 排序
  filtered.sort((a, b) => {
    const field = sortField.value as keyof ExecutionRecord
    const aVal = a[field]
    const bVal = b[field]
    
    if (aVal == null && bVal == null) return 0
    if (aVal == null) return 1
    if (bVal == null) return -1
    
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  
  return filtered
})

// 分页后的记录
const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / pageSize.value)
})

// 方法
const loadRecords = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 生成模拟数据
    records.value = generateMockRecords()
  } catch (error) {
    console.error('加载执行记录失败:', error)
  } finally {
    loading.value = false
  }
}

const generateMockRecords = (): ExecutionRecord[] => {
  const mockRecords: ExecutionRecord[] = []
  const taskNames = ['股票实时数据更新', '市场指数分析', '日报生成', '数据清理', '系统备份']
  const taskTypes: ExecutionRecord['taskType'][] = ['periodic', 'scheduled', 'immediate', 'special']
  const statuses: ExecutionRecord['status'][] = ['success', 'failed', 'running']
  const results: ExecutionRecord['result'][] = ['success', 'error', 'timeout']
  
  for (let i = 0; i < 100; i++) {
    const startTime = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
    const duration = Math.floor(Math.random() * 300) + 10
    const endTime = new Date(startTime.getTime() + duration * 1000)
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const result = status === 'success' ? 'success' : results[Math.floor(Math.random() * results.length)]
    
    mockRecords.push({
      id: `record_${i + 1}`,
      taskId: `task_${Math.floor(Math.random() * 10) + 1}`,
      taskName: taskNames[Math.floor(Math.random() * taskNames.length)],
      taskType: taskTypes[Math.floor(Math.random() * taskTypes.length)],
      status,
      result,
      startTime: startTime.toISOString(),
      endTime: status !== 'running' ? endTime.toISOString() : undefined,
      duration: status !== 'running' ? duration : undefined,
      errorMessage: result === 'error' ? '网络连接超时' : undefined,
      logs: `任务开始执行...\n正在处理数据...\n${result === 'success' ? '执行完成' : '执行失败'}`,
      taskArgs: {
        param1: 'value1',
        param2: Math.floor(Math.random() * 100)
      }
    })
  }
  
  return mockRecords.sort((a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  filters.value = {
    status: '',
    taskType: '',
    timeRange: '',
    startTime: '',
    endTime: '',
    taskName: '',
    result: ''
  }
  currentPage.value = 1
}

const refreshRecords = () => {
  loadRecords()
}

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

const getSortClass = (field: string) => {
  if (sortField.value !== field) return ''
  return sortOrder.value === 'asc' ? 'sort-asc' : 'sort-desc'
}

const viewDetails = (record: ExecutionRecord) => {
  selectedRecord.value = record
  showDetailModal.value = true
}

const viewLogs = (record: ExecutionRecord) => {
  selectedRecord.value = record
  showLogModal.value = true
}

const retryTask = async (record: ExecutionRecord) => {
  try {
    // 模拟重新执行任务
    console.log('重新执行任务:', record.taskName)
    // 这里应该调用实际的API
  } catch (error) {
    console.error('重新执行任务失败:', error)
  }
}

const exportRecords = () => {
  // 导出功能实现
  const csvContent = generateCSV(filteredRecords.value)
  downloadCSV(csvContent, 'task_execution_records.csv')
}

const generateCSV = (data: ExecutionRecord[]) => {
  const headers = ['任务名称', '任务类型', '执行状态', '开始时间', '结束时间', '执行耗时', '执行结果']
  const rows = data.map(record => [
    record.taskName,
    getTaskTypeLabel(record.taskType),
    getStatusLabel(record.status),
    formatDateTime(record.startTime),
    record.endTime ? formatDateTime(record.endTime) : '',
    record.duration ? record.duration + 's' : '',
    getResultLabel(record.result)
  ])
  
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

const downloadCSV = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedRecord.value = null
}

const closeLogModal = () => {
  showLogModal.value = false
  selectedRecord.value = null
}

// 格式化函数
const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getTaskTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'periodic': '周期任务',
    'scheduled': '定时任务',
    'immediate': '立即任务',
    'special': '特殊任务'
  }
  return labels[type] || type
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'pending': '等待中',
    'running': '运行中',
    'success': '成功',
    'failed': '失败'
  }
  return labels[status] || status
}

const getResultLabel = (result: string) => {
  const labels: Record<string, string> = {
    'success': '执行成功',
    'error': '执行错误',
    'timeout': '执行超时',
    'cancelled': '已取消'
  }
  return labels[result] || result
}

// 生命周期
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.task-execution-records {
  padding: 20px;
}

.filters-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-row {
  display: flex;
  gap: 20px;
  align-items: end;
  margin-bottom: 15px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.btn-primary,
.btn-secondary,
.btn-export {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-export {
  background: #28a745;
  color: white;
}

.stats-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.records-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.table-header h3 {
  margin: 0;
  color: #333;
}

.btn-refresh {
  padding: 8px 16px;
  background: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #e9ecef;
}

.sort-icon {
  margin-left: 5px;
  opacity: 0.5;
}

.sort-icon.sort-asc::after {
  content: '↑';
  opacity: 1;
}

.sort-icon.sort-desc::after {
  content: '↓';
  opacity: 1;
}

.task-type-badge,
.status-badge,
.result-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.task-type-badge.periodic {
  background: #e3f2fd;
  color: #1976d2;
}

.task-type-badge.scheduled {
  background: #f3e5f5;
  color: #7b1fa2;
}

.task-type-badge.immediate {
  background: #fff3e0;
  color: #f57c00;
}

.task-type-badge.special {
  background: #fce4ec;
  color: #c2185b;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.running {
  background: #cce5ff;
  color: #004085;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.result-badge.success {
  background: #d4edda;
  color: #155724;
}

.result-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.result-badge.timeout {
  background: #fff3cd;
  color: #856404;
}

.result-badge.cancelled {
  background: #e2e3e5;
  color: #383d41;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-action {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-action.view {
  background: #17a2b8;
  color: white;
}

.btn-action.logs {
  background: #6c757d;
  color: white;
}

.btn-action.retry {
  background: #ffc107;
  color: #212529;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid #eee;
}

.pagination-info {
  color: #666;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-page {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #333;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content.log-modal {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.detail-item span {
  color: #333;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
}

.task-args {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.log-content {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
}

.log-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>