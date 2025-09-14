<template>
  <div class="task-records">
    <div class="page-header">
      <h2>任务记录</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索任务名称"
          style="width: 200px;"
          @keyup.enter="searchRecords"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportRecords">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 搜索功能 -->
    <div class="search-section">
      <el-card>
        <template #header>
          <span>搜索筛选</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="任务状态">
              <el-select v-model="filters.status" placeholder="选择状态" @change="applyFilters">
                <el-option label="全部状态" value="" />
                <el-option label="进行中" value="running" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="任务类型">
              <el-select v-model="filters.taskType" placeholder="选择类型" @change="applyFilters">
                <el-option label="全部类型" value="" />
                <el-option label="周期任务" value="periodic" />
                <el-option label="定时任务" value="scheduled" />
                <el-option label="特殊任务" value="special" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="管理模块">
              <el-select v-model="filters.module" placeholder="选择模块" @change="applyFilters">
                <el-option label="全部模块" value="" />
                <el-option label="大盘信息" value="market" />
                <el-option label="行业板块" value="industry" />
                <el-option label="概念板块" value="concept" />
                <el-option label="股票数据" value="stock" />
                <el-option label="AI分析" value="ai" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="任务名称">
              <el-input v-model="filters.name" placeholder="输入任务名称" @input="applyFilters" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="触发方式">
              <el-select v-model="filters.triggerType" placeholder="选择触发方式" @change="applyFilters">
                <el-option label="全部方式" value="" />
                <el-option label="自动" value="auto" />
                <el-option label="手动" value="manual" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="执行时间">
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="applyFilters"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <div class="filter-actions">
              <el-button @click="resetFilters">重置</el-button>
              <el-button type="primary" @click="applyFilters">搜索</el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 任务记录表格 -->
    <div class="records-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>任务记录 ({{ filteredRecords.length }})</span>
            <div class="table-actions">
              <el-button size="small" @click="batchDelete" :disabled="selectedRecords.length === 0">
                批量删除
              </el-button>
              <el-button size="small" @click="clearOldRecords">
                清理历史记录
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedRecords" 
          :loading="loading"
          stripe 
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="taskName" label="任务名称" width="200">
            <template #default="{ row }">
              <div class="task-name">
                <div class="name">{{ row.taskName }}</div>
                <div class="id">ID: {{ row.taskId }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="taskType" label="任务类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getTaskTypeColor(row.taskType)" size="small">
                {{ getTaskTypeLabel(row.taskType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="triggerType" label="触发方式" width="100">
            <template #default="{ row }">
              <el-tag :type="row.triggerType === 'auto' ? 'success' : 'warning'" size="small">
                {{ row.triggerType === 'auto' ? '自动' : '手动' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="startTime" label="开始时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.startTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="endTime" label="结束时间" width="180">
            <template #default="{ row }">
              <template v-if="row.endTime">
                {{ formatDateTime(row.endTime) }}
              </template>
              <span v-else class="running-text">运行中...</span>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="执行时长" width="120">
            <template #default="{ row }">
              {{ getDuration(row) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="执行结果" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="row.status && row.status !== 'running'"
                type="text" 
                :class="getResultClass(row.status)"
                @click="viewRecordDetail(row)"
              >
                {{ getResultLabel(row.status) }}
              </el-button>
              <el-tag v-else-if="row.status === 'running'" type="warning" size="small">
                <el-icon class="rotating"><Loading /></el-icon>
                进行中
              </el-tag>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="processedCount" label="处理数量" width="100">
            <template #default="{ row }">
              {{ row.processedCount || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewRecord(row)">
                查看
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteRecord(row)"
                :disabled="row.status === 'running'"
              >
                删除
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
            :total="filteredRecords.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 查看记录详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="任务记录详情" width="900px">
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ selectedRecord.taskName }}</el-descriptions-item>
          <el-descriptions-item label="任务ID">{{ selectedRecord.taskId }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="getTaskTypeColor(selectedRecord.taskType)" size="small">
              {{ getTaskTypeLabel(selectedRecord.taskType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="触发方式">
            <el-tag :type="selectedRecord.triggerType === 'auto' ? 'success' : 'warning'" size="small">
              {{ selectedRecord.triggerType === 'auto' ? '自动' : '手动' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDateTime(selectedRecord.startTime) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ selectedRecord.endTime ? formatDateTime(selectedRecord.endTime) : '运行中...' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ getDuration(selectedRecord) }}</el-descriptions-item>
          <el-descriptions-item label="执行结果">
            <el-tag :type="getStatusColor(selectedRecord.status)" size="small">
              {{ getResultLabel(selectedRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="处理数量">{{ selectedRecord.processedCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="错误数量">{{ selectedRecord.errorCount || 0 }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="record-config" v-if="selectedRecord.config">
          <h4>任务配置</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="使用接口">
              {{ selectedRecord.apiEndpoint || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="更新数据表">
              {{ selectedRecord.targetTables ? selectedRecord.targetTables.join(', ') : '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="关联模块" :span="2">
              {{ selectedRecord.relatedModules ? selectedRecord.relatedModules.join(', ') : '--' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="execution-log" v-if="selectedRecord.logs">
          <h4>执行日志</h4>
          <el-input
            v-model="selectedRecord.logs"
            type="textarea"
            :rows="10"
            readonly
            class="log-textarea"
          />
        </div>
        
        <div class="error-details" v-if="selectedRecord.errorMessage">
          <h4>错误详情</h4>
          <el-alert
            :title="selectedRecord.errorMessage"
            type="error"
            :description="selectedRecord.errorDetails"
            show-icon
            :closable="false"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Refresh, Download, Loading 
} from '@element-plus/icons-vue'

interface TaskRecord {
  id: number
  taskId: number
  taskName: string
  taskType: 'periodic' | 'scheduled' | 'special'
  module: string
  triggerType: 'auto' | 'manual'
  startTime: string
  endTime?: string
  status: 'running' | 'success' | 'failed'
  processedCount?: number
  errorCount?: number
  logs?: string
  errorMessage?: string
  errorDetails?: string
  config?: any
  apiEndpoint?: string
  targetTables?: string[]
  relatedModules?: string[]
}

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const showDetailDialog = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedRecords = ref<TaskRecord[]>([])
const selectedRecord = ref<TaskRecord | null>(null)
const dateRange = ref<[string, string] | null>(null)

// 数据
const records = ref<TaskRecord[]>([])

// 筛选条件
const filters = ref({
  status: '',
  taskType: '',
  module: '',
  name: '',
  triggerType: ''
})

// 计算属性
const filteredRecords = computed(() => {
  let result = records.value
  
  if (filters.value.status) {
    result = result.filter(record => record.status === filters.value.status)
  }
  
  if (filters.value.taskType) {
    result = result.filter(record => record.taskType === filters.value.taskType)
  }
  
  if (filters.value.module) {
    result = result.filter(record => record.module === filters.value.module)
  }
  
  if (filters.value.triggerType) {
    result = result.filter(record => record.triggerType === filters.value.triggerType)
  }
  
  if (filters.value.name) {
    result = result.filter(record => 
      record.taskName.toLowerCase().includes(filters.value.name.toLowerCase())
    )
  }
  
  if (searchKeyword.value) {
    result = result.filter(record => 
      record.taskName.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  if (dateRange.value && dateRange.value.length === 2) {
    const [startDate, endDate] = dateRange.value
    result = result.filter(record => {
      const recordDate = new Date(record.startTime)
      return recordDate >= new Date(startDate) && recordDate <= new Date(endDate)
    })
  }
  
  // 按开始时间倒序排列
  return result.sort((a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// 方法
const loadRecords = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    records.value = [
      {
        id: 1,
        taskId: 1,
        taskName: '股票基础数据同步',
        taskType: 'periodic',
        module: 'stock',
        triggerType: 'auto',
        startTime: '2024-01-20 14:30:00',
        endTime: '2024-01-20 14:32:15',
        status: 'success',
        processedCount: 3456,
        errorCount: 0,
        apiEndpoint: '/api/stocks/sync',
        targetTables: ['stocks_basic', 'stocks_realtime'],
        relatedModules: ['股票实时数据'],
        logs: '2024-01-20 14:30:00 [INFO] 开始同步股票数据\n2024-01-20 14:30:15 [INFO] 获取股票列表成功，共3456只股票\n2024-01-20 14:31:30 [INFO] 数据同步进度: 50%\n2024-01-20 14:32:10 [INFO] 数据同步完成\n2024-01-20 14:32:15 [INFO] 任务执行成功'
      },
      {
        id: 2,
        taskId: 2,
        taskName: '行业板块数据更新',
        taskType: 'scheduled',
        module: 'industry',
        triggerType: 'auto',
        startTime: '2024-01-20 09:00:00',
        endTime: '2024-01-20 09:05:30',
        status: 'success',
        processedCount: 89,
        errorCount: 0,
        apiEndpoint: '/api/industry/sync',
        targetTables: ['industry_sectors', 'industry_stocks'],
        relatedModules: ['行业板块数据'],
        logs: '2024-01-20 09:00:00 [INFO] 开始更新行业板块数据\n2024-01-20 09:01:00 [INFO] 获取行业分类成功\n2024-01-20 09:03:00 [INFO] 更新成分股信息\n2024-01-20 09:05:30 [INFO] 任务执行成功'
      },
      {
        id: 3,
        taskId: 3,
        taskName: 'AI股票分析任务',
        taskType: 'special',
        module: 'ai',
        triggerType: 'manual',
        startTime: '2024-01-19 16:00:00',
        endTime: '2024-01-19 16:15:45',
        status: 'failed',
        processedCount: 12,
        errorCount: 11,
        apiEndpoint: '/api/ai/analyze',
        targetTables: ['ai_analysis_results'],
        relatedModules: ['AI分析结果'],
        errorMessage: 'API调用超时',
        errorDetails: '连接AI分析服务超时，请检查网络连接和服务状态',
        logs: '2024-01-19 16:00:00 [INFO] 开始AI分析任务\n2024-01-19 16:05:00 [ERROR] API调用超时\n2024-01-19 16:15:45 [ERROR] 任务执行失败'
      },
      {
        id: 4,
        taskId: 1,
        taskName: '股票基础数据同步',
        taskType: 'periodic',
        module: 'stock',
        triggerType: 'auto',
        startTime: '2024-01-20 15:30:00',
        status: 'running',
        processedCount: 1234,
        errorCount: 0,
        apiEndpoint: '/api/stocks/sync',
        targetTables: ['stocks_basic', 'stocks_realtime'],
        relatedModules: ['股票实时数据'],
        logs: '2024-01-20 15:30:00 [INFO] 开始同步股票数据\n2024-01-20 15:30:15 [INFO] 获取股票列表成功\n2024-01-20 15:31:30 [INFO] 数据同步进度: 35%'
      }
    ]
  } catch (error) {
    ElMessage.error('加载任务记录失败')
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadRecords()
}

const searchRecords = () => {
  // 搜索逻辑已在计算属性中处理
}

const applyFilters = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  filters.value = {
    status: '',
    taskType: '',
    module: '',
    name: '',
    triggerType: ''
  }
  dateRange.value = null
  searchKeyword.value = ''
  currentPage.value = 1
}

const handleSelectionChange = (selection: TaskRecord[]) => {
  selectedRecords.value = selection
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const viewRecord = (record: TaskRecord) => {
  selectedRecord.value = record
  showDetailDialog.value = true
}

const viewRecordDetail = (record: TaskRecord) => {
  selectedRecord.value = record
  showDetailDialog.value = true
}

const deleteRecord = async (record: TaskRecord) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务记录 "${record.taskName}" 吗？`, '删除确认', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const index = records.value.findIndex(r => r.id === record.id)
    if (index > -1) {
      records.value.splice(index, 1)
    }
    
    ElMessage.success('记录删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('记录删除失败')
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRecords.value.length} 条记录吗？`, '批量删除', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const selectedIds = selectedRecords.value.map(r => r.id)
    records.value = records.value.filter(r => !selectedIds.includes(r.id))
    
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const clearOldRecords = async () => {
  try {
    await ElMessageBox.confirm('确定要清理30天前的历史记录吗？', '清理历史记录', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    
    const beforeCount = records.value.length
    records.value = records.value.filter(r => new Date(r.startTime) > thirtyDaysAgo)
    const afterCount = records.value.length
    
    ElMessage.success(`清理完成，删除了 ${beforeCount - afterCount} 条历史记录`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理历史记录失败')
    }
  }
}

const exportRecords = async () => {
  try {
    // 模拟导出功能
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('记录导出成功')
  } catch (error) {
    ElMessage.error('记录导出失败')
  }
}

// 工具函数
const getTaskTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    periodic: '周期任务',
    scheduled: '定时任务',
    special: '特殊任务'
  }
  return labels[type] || type
}

const getTaskTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    periodic: 'success',
    scheduled: 'warning',
    special: 'info'
  }
  return colors[type] || 'info'
}

const getResultLabel = (result: string) => {
  const labels: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '进行中'
  }
  return labels[result] || result
}

const getResultClass = (result: string) => {
  const classes: Record<string, string> = {
    success: 'success-link',
    failed: 'error-link'
  }
  return classes[result] || ''
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    success: 'success',
    failed: 'danger',
    running: 'warning'
  }
  return colors[status] || 'info'
}

const getDuration = (record: TaskRecord) => {
  if (!record.endTime) {
    if (record.status === 'running') {
      const now = new Date()
      const start = new Date(record.startTime)
      const diff = Math.floor((now.getTime() - start.getTime()) / 1000)
      return formatDuration(diff)
    }
    return '--'
  }
  
  const start = new Date(record.startTime)
  const end = new Date(record.endTime)
  const diff = Math.floor((end.getTime() - start.getTime()) / 1000)
  return formatDuration(diff)
}

const formatDuration = (seconds: number) => {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}分${remainingSeconds}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分钟`
  }
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

// 生命周期
onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.task-records {
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

.page-header h2 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  align-items: flex-end;
  height: 100%;
  padding-top: 30px;
}

.records-table {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.task-name .name {
  font-weight: bold;
  margin-bottom: 4px;
}

.task-name .id {
  font-size: 12px;
  color: #7f8c8d;
}

.running-text {
  color: #f39c12;
  font-style: italic;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.record-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.record-config {
  margin-top: 20px;
}

.record-config h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.execution-log {
  margin-top: 20px;
}

.execution-log h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.log-textarea {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.error-details {
  margin-top: 20px;
}

.error-details h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.success-link {
  color: #27ae60;
}

.error-link {
  color: #e74c3c;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .filter-actions {
    justify-content: center;
    padding-top: 15px;
  }
}
</style>