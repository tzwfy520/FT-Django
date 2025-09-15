<template>
  <div class="task-settings">
    <div class="page-header">
      <h2>任务设置</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索任务名称"
          style="width: 200px;"
          @keyup.enter="searchTasks"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建任务
        </el-button>
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 数据概览 -->
    <div class="stats-section">
      <div class="stats-header">
        <h3>数据概览</h3>
        <el-radio-group v-model="statsType" @change="loadStats">
          <el-radio-button label="today">今日数据</el-radio-button>
          <el-radio-button label="history">历史数据</el-radio-button>
        </el-radio-group>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon running">
                <el-icon><Loading /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ taskStats.running }}</div>
                <div class="stats-label">运行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon completed">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ taskStats.completed }}</div>
                <div class="stats-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon failed">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ taskStats.failed }}</div>
                <div class="stats-label">失败</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-item">
              <div class="stats-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ taskStats.total }}</div>
                <div class="stats-label">总任务数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
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
                <el-option label="启用" value="enabled" />
                <el-option label="禁用" value="disabled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="触发方式">
              <el-select v-model="filters.trigger_method" placeholder="选择触发方式" @change="applyFilters">
                <el-option label="全部方式" value="" />
                <el-option label="手动触发" value="manual" />
                <el-option label="定时触发" value="scheduled" />
                <el-option label="周期触发" value="periodic" />
                <el-option label="事件触发" value="event" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="任务目标">
              <el-select v-model="filters.task_target" placeholder="选择任务目标" @change="applyFilters">
                <el-option label="全部目标" value="" />
                <el-option label="股票数据更新" value="stock_data_update" />
            <el-option label="行业板块更新" value="industry_sector_update" />
            <el-option label="概念板块更新" value="concept_sector_update" />
            <el-option label="大盘数据更新" value="market_data_update" />
            <el-option label="AI分析" value="ai_analysis" />
            <el-option label="其他" value="other" />
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
      </el-card>
    </div>

    <!-- 任务管理表格 -->
    <div class="task-table">
      <el-card>
        <template #header>
          <div class="table-header">
            <span>任务管理 ({{ filteredTasks.length }})</span>
            <div class="table-actions">
              <el-button size="small" @click="batchEnable" :disabled="selectedTasks.length === 0">
                批量启用
              </el-button>
              <el-button size="small" @click="batchDisable" :disabled="selectedTasks.length === 0">
                批量禁用
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="paginatedTasks" 
          :loading="loading"
          stripe 
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="name" label="任务名称" width="200">
            <template #default="{ row }">
              <div class="task-name">
                <div class="name">{{ row.name }}</div>
                <div class="description">{{ row.description }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="trigger_method" label="触发方式" width="120">
            <template #default="{ row }">
              <el-tag :type="getTriggerMethodColor(row.trigger_method)" size="small">
                {{ getTriggerMethodLabel(row.trigger_method) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="task_target" label="任务目标" width="120">
            <template #default="{ row }">
              <el-tag :type="getTaskTargetColor(row.task_target)" size="small">
                {{ getTaskTargetLabel(row.task_target) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalCount" label="任务总数" width="100" />
          <el-table-column prop="lastExecutedAt" label="最后执行时间" width="180">
            <template #default="{ row }">
              {{ row.lastExecutedAt ? formatDateTime(row.lastExecutedAt) : '--' }}
            </template>
          </el-table-column>
          <el-table-column prop="lastExecutionResult" label="最后执行结果" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="row.lastExecutionResult && row.lastExecutionResult !== 'running'"
                type="text" 
                :class="getResultClass(row.lastExecutionResult)"
                @click="viewTaskDetail(row)"
              >
                {{ getResultLabel(row.lastExecutionResult) }}
              </el-button>
              <el-tag v-else-if="row.lastExecutionResult === 'running'" type="warning" size="small">
                进行中
              </el-tag>
              <span v-else>--</span>
            </template>
          </el-table-column>
          <el-table-column prop="isActive" label="启用状态" width="100">
            <template #default="{ row }">
              <el-switch 
                v-model="row.isActive" 
                @change="toggleTaskStatus(row)"
                :loading="row.statusLoading"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewTask(row)">
                查看
              </el-button>
              <el-button size="small" type="primary" @click="editTask(row)">
                编辑
              </el-button>
              <el-button size="small" type="success" @click="executeTask(row)" :loading="row.executing">
                执行
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
            :total="filteredTasks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建任务" width="600px">
      <el-form :model="newTask" :rules="taskRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="newTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="newTask.description" type="textarea" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="触发方式" prop="trigger_method">
          <el-select v-model="newTask.trigger_method" placeholder="选择触发方式" @change="handleTriggerMethodChange">
            <el-option label="手动触发" value="manual" />
            <el-option label="定时触发" value="scheduled" />
            <el-option label="周期触发" value="periodic" />
            <el-option label="事件触发" value="event" />
          </el-select>
        </el-form-item>
        <el-form-item label="任务目标" prop="task_target">
          <el-select v-model="newTask.task_target" placeholder="选择任务目标">
            <el-option label="股票数据更新" value="stock_data_update" />
            <el-option label="行业板块更新" value="industry_sector_update" />
            <el-option label="概念板块更新" value="concept_sector_update" />
            <el-option label="大盘数据更新" value="market_data_update" />
            <el-option label="AI分析" value="ai_analysis" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="newTask.trigger_method === 'periodic'" label="执行间隔" prop="intervalSeconds">
          <el-input-number v-model="newTask.intervalSeconds" :min="60" placeholder="秒" />
        </el-form-item>
        <el-form-item v-if="newTask.trigger_method === 'scheduled'" label="Cron表达式" prop="cronExpression">
          <el-input v-model="newTask.cronExpression" placeholder="如: 0 0 9 * * ?" />
        </el-form-item>
        <el-form-item v-if="newTask.trigger_method === 'scheduled'" label="执行时间" prop="executeAt">
          <el-date-picker 
            v-model="newTask.executeAt" 
            type="datetime" 
            placeholder="选择执行时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="管理模块" prop="module">
          <el-select v-model="newTask.module" placeholder="选择管理模块">
            <el-option label="大盘信息" value="market" />
            <el-option label="行业板块" value="industry" />
            <el-option label="概念板块" value="concept" />
            <el-option label="股票数据" value="stock" />
            <el-option label="AI分析" value="ai" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑任务对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑任务" width="600px">
      <el-form :model="editingTask" :rules="taskRules" ref="editFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="editingTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input v-model="editingTask.description" type="textarea" placeholder="请输入任务描述" />
        </el-form-item>
        <el-form-item label="任务类型" prop="taskType">
          <el-select v-model="editingTask.taskType" placeholder="选择任务类型" @change="handleEditTaskTypeChange">
            <el-option label="周期任务" value="periodic" />
            <el-option label="定时任务" value="scheduled" />
            <el-option label="特殊任务" value="special" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editingTask.taskType === 'periodic'" label="执行间隔" prop="intervalSeconds">
          <el-input-number v-model="editingTask.intervalSeconds" :min="60" placeholder="秒" />
        </el-form-item>
        <el-form-item v-if="editingTask.taskType === 'scheduled'" label="Cron表达式" prop="cronExpression">
          <el-input v-model="editingTask.cronExpression" placeholder="如: 0 0 9 * * ?" />
        </el-form-item>
        <el-form-item v-if="editingTask.taskType === 'scheduled'" label="执行时间" prop="executeAt">
          <el-date-picker 
            v-model="editingTask.executeAt" 
            type="datetime" 
            placeholder="选择执行时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="任务目标" prop="task_target">
          <el-select v-model="editingTask.task_target" placeholder="选择任务目标">
            <el-option label="股票数据更新" value="stock_data_update" />
            <el-option label="行业板块更新" value="industry_sector_update" />
            <el-option label="概念板块更新" value="concept_sector_update" />
            <el-option label="大盘数据更新" value="market_data_update" />
            <el-option label="AI分析" value="ai_analysis" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理模块" prop="module">
          <el-select v-model="editingTask.module" placeholder="选择管理模块">
            <el-option label="大盘信息" value="market" />
            <el-option label="行业板块" value="industry" />
            <el-option label="概念板块" value="concept" />
            <el-option label="股票数据" value="stock" />
            <el-option label="AI分析" value="ai" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateTask" :loading="updating">更新</el-button>
      </template>
    </el-dialog>

    <!-- 查看任务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="任务详情" width="800px">
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ selectedTask.name }}</el-descriptions-item>
          <el-descriptions-item label="触发方式">
            <el-tag :type="getTriggerMethodColor(selectedTask.trigger_method)" size="small">
              {{ getTriggerMethodLabel(selectedTask.trigger_method) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="任务目标">
            <el-tag :type="getTaskTargetColor(selectedTask.task_target)" size="small">
              {{ getTaskTargetLabel(selectedTask.task_target) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="管理模块">{{ getModuleLabel(selectedTask.module) }}</el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="selectedTask.isActive ? 'success' : 'danger'" size="small">
              {{ selectedTask.isActive ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(selectedTask.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="最后执行时间">
            {{ selectedTask.lastExecutedAt ? formatDateTime(selectedTask.lastExecutedAt) : '--' }}
          </el-descriptions-item>
          <el-descriptions-item label="任务描述" :span="2">
            {{ selectedTask.description || '--' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="task-config" v-if="selectedTask.config">
          <h4>任务配置</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item v-if="selectedTask.intervalSeconds" label="执行间隔">
              {{ selectedTask.intervalSeconds }}秒
            </el-descriptions-item>
            <el-descriptions-item v-if="selectedTask.cronExpression" label="Cron表达式">
              {{ selectedTask.cronExpression }}
            </el-descriptions-item>
            <el-descriptions-item v-if="selectedTask.executeAt" label="执行时间">
              {{ formatDateTime(selectedTask.executeAt) }}
            </el-descriptions-item>
            <el-descriptions-item label="使用接口">
              {{ selectedTask.apiEndpoint || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="更新数据表">
              {{ selectedTask.targetTables ? selectedTask.targetTables.join(', ') : '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="关联模块" :span="2">
              {{ selectedTask.relatedModules ? selectedTask.relatedModules.join(', ') : '--' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 根据任务目标展示具体内容 -->
        <div class="task-target-details" style="margin-top: 20px;">
          <!-- 股票数据更新 -->
          <div v-if="selectedTask.task_target === 'stock_data_update'">
            <h4>更新的股票清单</h4>
            <el-table :data="getStockList()" border style="width: 100%" max-height="300">
              <el-table-column prop="code" label="股票代码" width="120" />
              <el-table-column prop="name" label="股票名称" />
              <el-table-column prop="market" label="市场" width="80" />
              <el-table-column prop="status" label="状态" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'" size="small">
                    {{ scope.row.status === 'active' ? '正常' : '停牌' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 行业板块更新 -->
          <div v-if="selectedTask.task_target === 'industry_sector_update'">
            <h4>更新的行业板块清单</h4>
            <el-table :data="getIndustrySectorList()" border style="width: 100%" max-height="300">
              <el-table-column prop="code" label="板块代码" width="120" />
              <el-table-column prop="name" label="板块名称" />
              <el-table-column prop="stockCount" label="成分股数量" width="120" />
              <el-table-column prop="updateTime" label="更新时间" width="180" />
            </el-table>
          </div>

          <!-- 概念板块更新 -->
          <div v-if="selectedTask.task_target === 'concept_sector_update'">
            <h4>更新的概念板块清单</h4>
            <el-table :data="getConceptSectorList()" border style="width: 100%" max-height="300">
              <el-table-column prop="code" label="概念代码" width="120" />
              <el-table-column prop="name" label="概念名称" />
              <el-table-column prop="stockCount" label="相关股票数" width="120" />
              <el-table-column prop="hotLevel" label="热度" width="80">
                <template #default="scope">
                  <el-tag :type="getHotLevelColor(scope.row.hotLevel)" size="small">
                    {{ scope.row.hotLevel }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Plus, Refresh, Loading, CircleCheck, CircleClose, Document 
} from '@element-plus/icons-vue'
import { tasksAPI, stocksAPI } from '@/services/api'

interface Task {
  id: number
  name: string
  description: string
  trigger_method: 'manual' | 'scheduled' | 'periodic' | 'event'
  task_target: string
  module: string
  intervalSeconds?: number
  cronExpression?: string
  executeAt?: string
  isActive: boolean
  createdAt: string
  lastExecutedAt?: string
  lastExecutionResult?: 'success' | 'failed' | 'running'
  totalCount: number
  config?: any
  apiEndpoint?: string
  targetTables?: string[]
  relatedModules?: string[]
  statusLoading?: boolean
  executing?: boolean
  // 保持向后兼容
  taskType?: 'periodic' | 'scheduled' | 'special'
}

interface TaskStats {
  running: number
  completed: number
  failed: number
  total: number
}

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const updating = ref(false)
const statsType = ref('today')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedTasks = ref<Task[]>([])
const selectedTask = ref<Task | null>(null)

// 表单引用
const taskFormRef = ref()
const editFormRef = ref()

// 数据
const tasks = ref<Task[]>([])
const taskStats = ref<TaskStats>({
  running: 0,
  completed: 0,
  failed: 0,
  total: 0
})

// 筛选条件
const filters = ref({
  status: '',
  trigger_method: '',
  task_target: '',
  module: '',
  name: ''
})

// 新建任务表单
const newTask = ref({
  name: '',
  description: '',
  trigger_method: '',
  task_target: '',
  module: '',
  intervalSeconds: 3600,
  cronExpression: '',
  executeAt: ''
})

// 编辑任务表单
const editingTask = ref<Partial<Task>>({})

// 表单验证规则
const taskRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  trigger_method: [{ required: true, message: '请选择触发方式', trigger: 'change' }],
  task_target: [{ required: true, message: '请选择任务目标', trigger: 'change' }],
  module: [{ required: true, message: '请选择管理模块', trigger: 'change' }]
}

// 计算属性
const filteredTasks = computed(() => {
  let result = tasks.value
  
  if (filters.value.status) {
    result = result.filter(task => {
      if (filters.value.status === 'enabled') return task.isActive
      if (filters.value.status === 'disabled') return !task.isActive
      return true
    })
  }
  
  if (filters.value.trigger_method) {
    result = result.filter(task => task.trigger_method === filters.value.trigger_method)
  }
  
  if (filters.value.task_target) {
    result = result.filter(task => task.task_target === filters.value.task_target)
  }
  
  if (filters.value.module) {
    result = result.filter(task => task.module === filters.value.module)
  }
  
  if (filters.value.name) {
    result = result.filter(task => 
      task.name.toLowerCase().includes(filters.value.name.toLowerCase())
    )
  }
  
  if (searchKeyword.value) {
    result = result.filter(task => 
      task.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  return result
})

const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTasks.value.slice(start, end)
})

// 方法
const loadTasks = async () => {
  loading.value = true
  try {
    const response = await tasksAPI.getTaskDefinitions({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    if (response.data.success) {
      tasks.value = response.data.data.tasks || []
    } else {
      // 如果API调用失败，使用模拟数据作为后备
      tasks.value = [
        {
          id: 1,
          name: '股票基础数据同步',
          description: '同步股票基础信息和实时价格数据',
          trigger_method: 'periodic',
          task_target: 'stock_data_update',
          taskType: 'periodic',
          module: 'stock',
          intervalSeconds: 3600,
          isActive: true,
          createdAt: '2024-01-15 09:00:00',
          lastExecutedAt: '2024-01-20 14:30:00',
          lastExecutionResult: 'success',
          totalCount: 156,
          apiEndpoint: '/api/stocks/sync',
          targetTables: ['stocks_basic', 'stocks_realtime'],
          relatedModules: ['股票实时数据']
        },
        {
          id: 2,
          name: '行业板块数据更新',
          description: '更新行业板块分类和成分股信息',
          trigger_method: 'scheduled',
          task_target: 'industry_sector_update',
          taskType: 'scheduled',
          module: 'industry',
          cronExpression: '0 0 9 * * ?',
          executeAt: '2024-01-21 09:00:00',
          isActive: true,
          createdAt: '2024-01-15 10:00:00',
          lastExecutedAt: '2024-01-20 09:00:00',
          lastExecutionResult: 'success',
          totalCount: 89,
          apiEndpoint: '/api/industry/sync',
          targetTables: ['industry_sectors', 'industry_stocks'],
          relatedModules: ['行业板块数据']
        },
        {
          id: 3,
          name: 'AI股票分析任务',
          description: 'AI自动分析股票走势和推荐',
          trigger_method: 'manual',
          task_target: 'ai_analysis',
          taskType: 'special',
          module: 'ai',
          isActive: false,
          createdAt: '2024-01-16 11:00:00',
          lastExecutedAt: '2024-01-19 16:00:00',
          lastExecutionResult: 'failed',
          totalCount: 23,
          apiEndpoint: '/api/ai/analyze',
          targetTables: ['ai_analysis_results'],
          relatedModules: ['AI分析结果']
        }
      ]
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
    // 使用模拟数据作为后备
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await tasksAPI.getTaskStats()
    
    if (response.data.success) {
      taskStats.value = response.data.data
    } else {
      // 使用模拟数据作为后备
      if (statsType.value === 'today') {
        taskStats.value = {
          running: 2,
          completed: 15,
          failed: 1,
          total: 18
        }
      } else {
        taskStats.value = {
          running: 3,
          completed: 156,
          failed: 8,
          total: 167
        }
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据作为后备
    if (statsType.value === 'today') {
      taskStats.value = {
        running: 2,
        completed: 15,
        failed: 1,
        total: 18
      }
    } else {
      taskStats.value = {
        running: 3,
        completed: 156,
        failed: 8,
        total: 167
      }
    }
  }
}

const refreshData = async () => {
  await Promise.all([loadTasks(), loadStats()])
}

const searchTasks = () => {
  // 搜索逻辑已在计算属性中处理
}

const applyFilters = () => {
  currentPage.value = 1
}

const handleSelectionChange = (selection: Task[]) => {
  selectedTasks.value = selection
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const handleTriggerMethodChange = () => {
  // 清空相关字段
  newTask.value.intervalSeconds = 3600
  newTask.value.cronExpression = ''
  newTask.value.executeAt = ''
}

const handleEditTaskTypeChange = () => {
  // 清空相关字段
  editingTask.value.intervalSeconds = 3600
  editingTask.value.cronExpression = ''
  editingTask.value.executeAt = ''
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    creating.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
    
    // 重置表单
    Object.assign(newTask.value, {
      name: '',
      description: '',
      trigger_method: '',
      task_target: '',
      module: '',
      intervalSeconds: 3600,
      cronExpression: '',
      executeAt: ''
    })
    
    await loadTasks()
  } catch (error) {
    ElMessage.error('任务创建失败')
  } finally {
    creating.value = false
  }
}

const editTask = (task: Task) => {
  editingTask.value = { ...task }
  showEditDialog.value = true
}

const updateTask = async () => {
  if (!editFormRef.value) return
  
  try {
    await editFormRef.value.validate()
    updating.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('任务更新成功')
    showEditDialog.value = false
    await loadTasks()
  } catch (error) {
    ElMessage.error('任务更新失败')
  } finally {
    updating.value = false
  }
}

const viewTask = async (task: Task) => {
  selectedTask.value = task
  showDetailDialog.value = true
}

const viewTaskDetail = async (task: Task) => {
  selectedTask.value = task
  showDetailDialog.value = true
}

const executeTask = async (task: Task) => {
  try {
    task.executing = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success(`任务 "${task.name}" 执行成功`)
    await loadTasks()
  } catch (error) {
    ElMessage.error(`任务 "${task.name}" 执行失败`)
  } finally {
    task.executing = false
  }
}

const toggleTaskStatus = async (task: Task) => {
  try {
    task.statusLoading = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(`任务已${task.isActive ? '启用' : '禁用'}`)
  } catch (error) {
    ElMessage.error('状态切换失败')
    task.isActive = !task.isActive // 回滚状态
  } finally {
    task.statusLoading = false
  }
}

const batchEnable = async () => {
  try {
    await ElMessageBox.confirm(`确定要启用选中的 ${selectedTasks.value.length} 个任务吗？`, '批量启用', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    selectedTasks.value.forEach(task => {
      task.isActive = true
    })
    
    ElMessage.success('批量启用成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量启用失败')
    }
  }
}

const batchDisable = async () => {
  try {
    await ElMessageBox.confirm(`确定要禁用选中的 ${selectedTasks.value.length} 个任务吗？`, '批量禁用', {
      type: 'warning'
    })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    selectedTasks.value.forEach(task => {
      task.isActive = false
    })
    
    ElMessage.success('批量禁用成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量禁用失败')
    }
  }
}

// 工具函数
const getTriggerMethodLabel = (method: string) => {
  const labels: Record<string, string> = {
    manual: '手动触发',
    scheduled: '定时触发',
    periodic: '周期触发',
    event: '事件触发'
  }
  return labels[method] || method
}

const getTriggerMethodColor = (method: string) => {
  const colors: Record<string, string> = {
    manual: 'info',
    scheduled: 'warning',
    periodic: 'success',
    event: 'primary'
  }
  return colors[method] || 'info'
}

const getTaskTargetLabel = (target: string) => {
  const labels: Record<string, string> = {
    stock_data_update: '股票数据更新',
    industry_sector_update: '行业板块更新',
    concept_sector_update: '概念板块更新',
    market_data_update: '大盘数据更新',
    ai_analysis: 'AI分析',
    other: '其他'
  }
  return labels[target] || target
}

const getTaskTargetColor = (target: string) => {
  const colors: Record<string, string> = {
    stock_data_update: 'success',
    industry_sector_update: 'warning',
    concept_sector_update: 'info',
    market_data_update: 'primary',
    ai_analysis: 'danger',
    other: 'info'
  }
  return colors[target] || 'info'
}

const getModuleLabel = (module: string) => {
  const labels: Record<string, string> = {
    market: '大盘信息',
    industry: '行业板块',
    concept: '概念板块',
    stock: '股票数据',
    ai: 'AI分析'
  }
  return labels[module] || module
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

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

// 获取股票清单数据
const getStockList = () => {
  // 返回模拟数据用于展示
  return [
    { code: '000001', name: '平安银行', market: 'SZ', status: 'active' },
    { code: '000002', name: '万科A', market: 'SZ', status: 'active' },
    { code: '600000', name: '浦发银行', market: 'SH', status: 'active' },
    { code: '600036', name: '招商银行', market: 'SH', status: 'active' },
    { code: '000858', name: '五粮液', market: 'SZ', status: 'active' }
  ]
}

// 获取行业板块清单数据
const getIndustrySectorList = () => {
  // 返回模拟数据用于展示
  return [
    { code: 'BK0001', name: '银行', stockCount: 42, updateTime: new Date().toLocaleString() },
    { code: 'BK0002', name: '房地产', stockCount: 38, updateTime: new Date().toLocaleString() },
    { code: 'BK0003', name: '食品饮料', stockCount: 56, updateTime: new Date().toLocaleString() },
    { code: 'BK0004', name: '医药生物', stockCount: 89, updateTime: new Date().toLocaleString() }
  ]
}

// 获取概念板块清单数据
const getConceptSectorList = () => {
  // 返回模拟数据用于展示
  return [
    { code: 'BK0401', name: '网络游戏', stockCount: 156, hotLevel: '高' },
    { code: 'BK0402', name: '人工智能', stockCount: 98, hotLevel: '中' },
    { code: 'BK0403', name: '新能源汽车', stockCount: 187, hotLevel: '高' },
    { code: 'BK0404', name: '5G概念', stockCount: 76, hotLevel: '低' }
  ]
}

// 获取热度颜色
const getHotLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return colors[level] || 'info'
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.task-settings {
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

.stats-section {
  margin-bottom: 20px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stats-header h3 {
  margin: 0;
  color: #2c3e50;
}

.stats-card {
  height: 100px;
}

.stats-item {
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 20px;
}

.stats-icon.running {
  background-color: #fef0e6;
  color: #f39c12;
}

.stats-icon.completed {
  background-color: #e8f5e8;
  color: #27ae60;
}

.stats-icon.failed {
  background-color: #fde8e8;
  color: #e74c3c;
}

.stats-icon.total {
  background-color: #e6f3ff;
  color: #3498db;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stats-label {
  color: #7f8c8d;
  font-size: 14px;
}

.search-section {
  margin-bottom: 20px;
}

.task-table {
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

.task-name .description {
  font-size: 12px;
  color: #7f8c8d;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.task-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.task-config {
  margin-top: 20px;
}

.task-config h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.success-link {
  color: #27ae60;
}

.error-link {
  color: #e74c3c;
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
  
  .stats-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}
</style>