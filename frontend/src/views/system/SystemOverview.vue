<template>
  <div class="system-overview">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>系统概览</h1>
      <div class="header-actions">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <el-button type="primary" @click="refreshAll" :loading="refreshing" icon="Refresh">
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 系统基本信息 -->
    <el-row :gutter="20" class="info-row">
      <el-col :span="8">
        <el-card class="info-card">
          <div class="info-item">
            <div class="info-icon">
              <el-icon :size="24" color="#409EFF"><Monitor /></el-icon>
            </div>
            <div class="info-content">
              <div class="info-label">系统版本</div>
              <div class="info-value">{{ systemInfo.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="info-card">
          <div class="info-item">
            <div class="info-icon">
              <el-icon :size="24" color="#67C23A"><Timer /></el-icon>
            </div>
            <div class="info-content">
              <div class="info-label">运行时间</div>
              <div class="info-value">{{ systemInfo.uptime }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="info-card">
          <div class="info-item">
            <div class="info-icon">
              <el-icon :size="24" color="#E6A23C"><Calendar /></el-icon>
            </div>
            <div class="info-content">
              <div class="info-label">启动时间</div>
              <div class="info-value">{{ systemInfo.startTime }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统性能监控 -->
    <el-row :gutter="20" class="performance-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统性能</span>
              <el-button text @click="refreshPerformance" :loading="performanceLoading">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="performance-metrics">
            <div class="metric-item">
              <div class="metric-label">CPU使用率</div>
              <el-progress 
                :percentage="performance.cpu" 
                :color="getProgressColor(performance.cpu)"
                :show-text="true"
              />
            </div>
            <div class="metric-item">
              <div class="metric-label">内存使用率</div>
              <el-progress 
                :percentage="performance.memory" 
                :color="getProgressColor(performance.memory)"
                :show-text="true"
              />
            </div>
            <div class="metric-item">
              <div class="metric-label">磁盘使用率</div>
              <el-progress 
                :percentage="performance.disk" 
                :color="getProgressColor(performance.disk)"
                :show-text="true"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>服务状态</span>
              <el-button text @click="refreshServices" :loading="servicesLoading">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="services-list">
            <div v-for="service in services" :key="service.name" class="service-item">
              <div class="service-info">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-desc">{{ service.description }}</div>
              </div>
              <div class="service-status">
                <el-tag :type="service.status === 'running' ? 'success' : 'danger'">
                  {{ service.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据统计</span>
              <el-button text @click="refreshStats" :loading="statsLoading">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6" v-for="stat in dataStats" :key="stat.key">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon :size="32" :color="stat.color">
                    <component :is="stat.icon" />
                  </el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-label">{{ stat.label }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动日志 -->
    <el-row class="logs-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <div>
                <el-button text @click="refreshLogs" :loading="logsLoading">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-button text @click="viewAllLogs">
                  查看全部
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="logs-list">
            <div v-for="log in recentLogs" :key="log.id" class="log-item">
              <div class="log-time">{{ log.time }}</div>
              <div class="log-content">
                <el-tag :type="getLogType(log.level)" size="small">{{ log.level }}</el-tag>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Refresh,
  Monitor,
  Timer,
  Calendar,
  DataBoard,
  Document,
  TrendCharts,
  Files
} from '@element-plus/icons-vue'

const router = useRouter()
const refreshing = ref(false)
const performanceLoading = ref(false)
const servicesLoading = ref(false)
const statsLoading = ref(false)
const logsLoading = ref(false)

// 系统基本信息
const systemInfo = ref({
  version: 'v1.0.0',
  uptime: '2天 14小时 32分钟',
  startTime: '2024-01-15 09:30:00'
})

// 系统性能数据
const performance = ref({
  cpu: 45,
  memory: 68,
  disk: 32
})

// 服务状态
const services = ref([
  {
    name: 'Django后端服务',
    description: 'API服务和业务逻辑处理',
    status: 'running'
  },
  {
    name: 'Celery任务队列',
    description: '异步任务处理服务',
    status: 'running'
  },
  {
    name: 'MySQL数据库',
    description: '股票交易数据存储',
    status: 'running'
  },
  {
    name: 'MinIO存储服务',
    description: '股票分析数据存储',
    status: 'running'
  }
])

// 数据统计
const dataStats = ref([
  {
    key: 'stocks',
    label: '股票数量',
    value: '4,856',
    icon: TrendCharts,
    color: '#409EFF'
  },
  {
    key: 'records',
    label: '交易记录',
    value: '2.3M',
    icon: DataBoard,
    color: '#67C23A'
  },
  {
    key: 'analysis',
    label: '分析报告',
    value: '1,234',
    icon: Document,
    color: '#E6A23C'
  },
  {
    key: 'files',
    label: '存储文件',
    value: '8.9GB',
    icon: Files,
    color: '#F56C6C'
  }
])

// 最近日志
const recentLogs = ref([
  {
    id: 1,
    time: '2024-01-17 14:30:25',
    level: 'INFO',
    message: '股票数据同步完成，共处理4856只股票'
  },
  {
    id: 2,
    time: '2024-01-17 14:25:10',
    level: 'INFO',
    message: '用户登录：admin@example.com'
  },
  {
    id: 3,
    time: '2024-01-17 14:20:05',
    level: 'WARNING',
    message: 'API请求频率较高，建议优化调用策略'
  },
  {
    id: 4,
    time: '2024-01-17 14:15:30',
    level: 'INFO',
    message: '定时任务执行完成：市场数据更新'
  },
  {
    id: 5,
    time: '2024-01-17 14:10:15',
    level: 'ERROR',
    message: '连接超时：获取实时行情数据失败'
  }
])

// 返回系统设置
const goBack = () => {
  router.push('/system-settings')
}

// 刷新所有数据
const refreshAll = async () => {
  refreshing.value = true
  try {
    await Promise.all([
      refreshPerformance(),
      refreshServices(),
      refreshStats(),
      refreshLogs()
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 刷新性能数据
const refreshPerformance = async () => {
  performanceLoading.value = true
  try {
    // TODO: 调用API获取性能数据
    // 模拟数据更新
    performance.value = {
      cpu: Math.floor(Math.random() * 100),
      memory: Math.floor(Math.random() * 100),
      disk: Math.floor(Math.random() * 100)
    }
  } catch (error) {
    console.error('获取性能数据失败:', error)
  } finally {
    performanceLoading.value = false
  }
}

// 刷新服务状态
const refreshServices = async () => {
  servicesLoading.value = true
  try {
    // TODO: 调用API获取服务状态
  } catch (error) {
    console.error('获取服务状态失败:', error)
  } finally {
    servicesLoading.value = false
  }
}

// 刷新统计数据
const refreshStats = async () => {
  statsLoading.value = true
  try {
    // TODO: 调用API获取统计数据
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    statsLoading.value = false
  }
}

// 刷新日志数据
const refreshLogs = async () => {
  logsLoading.value = true
  try {
    // TODO: 调用API获取最新日志
  } catch (error) {
    console.error('获取日志数据失败:', error)
  } finally {
    logsLoading.value = false
  }
}

// 查看全部日志
const viewAllLogs = () => {
  // TODO: 跳转到日志管理页面
  ElMessage.info('日志管理功能开发中')
}

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

// 获取日志类型
const getLogType = (level: string) => {
  switch (level) {
    case 'ERROR': return 'danger'
    case 'WARNING': return 'warning'
    case 'INFO': return 'success'
    default: return 'info'
  }
}

// 组件挂载时加载数据
onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.system-overview {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  color: #303133;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-row,
.performance-row,
.stats-row,
.logs-row {
  margin-bottom: 20px;
}

.info-card {
  height: 100%;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-icon {
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.info-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.services-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.service-info {
  flex: 1;
}

.service-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.service-desc {
  font-size: 14px;
  color: #909399;
}

.service-status {
  flex-shrink: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  height: 100%;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.log-time {
  flex-shrink: 0;
  font-size: 12px;
  color: #909399;
  width: 140px;
}

.log-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.log-message {
  font-size: 14px;
  color: #606266;
}
</style>