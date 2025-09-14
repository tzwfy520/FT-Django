<template>
  <div class="dashboard">
    <!-- 加载状态 -->
    <Loading v-if="loading" message="正在加载仪表板数据..." />
    
    <!-- 错误提示 -->
    <ErrorMessage 
      v-if="error" 
      :message="error" 
      type="error"
      :actions="[{ label: '重试', action: refreshData }]"
      @close="clearError"
    />
    
    <!-- 主要内容 -->
    <div v-if="!loading && !error" class="dashboard-content">
      <div class="dashboard-header">
        <h1>股票分析系统</h1>
        <div class="update-info">
          <span>系统状态: {{ stats.systemStatus === 'normal' ? '正常' : '异常' }}</span>
          <button @click="refreshData" class="refresh-btn">刷新</button>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>股票总数</h3>
            <p class="stat-number">{{ stats.totalStocks }}</p>
            <span class="stat-label">支股票</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-content">
            <h3>活跃股票</h3>
            <p class="stat-number">{{ stats.activeStocks }}</p>
            <span class="stat-label">正在监控</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">⚙️</div>
          <div class="stat-content">
            <h3>运行任务</h3>
            <p class="stat-number">{{ stats.runningTasks }}</p>
            <span class="stat-label">/ {{ stats.totalTasks }} 总任务</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🤖</div>
          <div class="stat-content">
            <h3>今日分析</h3>
            <p class="stat-number">{{ stats.todayAnalyses }}</p>
            <span class="stat-label">次分析</span>
          </div>
        </div>
      </div>

      <div class="content-grid">
        <div class="chart-section">
          <div class="section-header">
            <h2>市场概览</h2>
          </div>
          <div class="market-overview">
            <div v-if="marketOverview.length === 0" class="empty-state">
              <p>暂无市场数据</p>
            </div>
            <div v-else class="market-list">
              <div v-for="item in marketOverview" :key="item.id" class="market-item">
                <!-- 市场数据项 -->
              </div>
            </div>
          </div>
        </div>
        
        <div class="activity-section">
          <div class="section-header">
            <h2>最近活动</h2>
          </div>
          <div class="activity-list">
            <div v-if="recentActivities.length === 0" class="empty-state">
              <p>暂无活动记录</p>
            </div>
            <div v-else>
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <div class="activity-icon" :class="activity.type">
                  <span v-if="activity.type === 'data_sync'">🔄</span>
                  <span v-else-if="activity.type === 'analysis'">🤖</span>
                  <span v-else-if="activity.type === 'alert'">⚠️</span>
                  <span v-else>📝</span>
                </div>
                <div class="activity-content">
                  <div class="activity-message">{{ activity.message }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { stocksAPI, tasksAPI, aiAPI, systemAPI } from '@/services/api'
import Loading from '@/components/Loading.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

// 响应式数据
const stats = ref({
  totalStocks: 0,
  activeStocks: 0,
  totalTasks: 0,
  runningTasks: 0,
  todayAnalyses: 0,
  systemStatus: 'normal'
})

const recentActivities = ref([])
const marketOverview = ref([])
const taskStatus = ref([])
const loading = ref(true)
const error = ref('')

// 生命周期方法
onMounted(async () => {
  await loadDashboardData()
})

// 数据加载方法
const loadDashboardData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 并行加载各种统计数据
    const [stockStats, taskStats, aiStats, systemStats] = await Promise.all([
      stocksAPI.getStats().catch(() => ({ data: { total_stocks: 0, active_stocks: 0 } })),
      tasksAPI.getTaskStats().catch(() => ({ data: { total_tasks: 0, active_tasks: 0 } })),
      aiAPI.getAIStats().catch(() => ({ data: { total_analyses: 0 } })),
      systemAPI.getStats().catch(() => ({ data: { system_status: 'normal' } }))
    ])
    
    stats.value = {
      totalStocks: stockStats.data.total_stocks || 0,
      activeStocks: stockStats.data.active_stocks || 0,
      totalTasks: taskStats.data.total_tasks || 0,
      runningTasks: taskStats.data.active_tasks || 0,
      todayAnalyses: aiStats.data.total_analyses || 0,
      systemStatus: systemStats.data.system_status || 'normal'
    }
    
    // 模拟最近活动数据
    recentActivities.value = [
      { id: 1, type: 'data_sync', message: '股票数据同步完成', time: '2分钟前' },
      { id: 2, type: 'analysis', message: 'AI分析任务执行完成', time: '5分钟前' },
      { id: 3, type: 'alert', message: '检测到异常波动股票', time: '10分钟前' }
    ]
    
  } catch (err: any) {
    console.error('加载仪表板数据失败:', err)
    error.value = err.response?.data?.message || '加载数据失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadDashboardData()
}

const clearError = () => {
  error.value = ''
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

.dashboard-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
}

.dashboard-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 28px;
}

.update-info {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #6c757d;
  font-size: 14px;
}

.refresh-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background: #0056b3;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.07);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-content h3 {
  color: #6c757d;
  font-size: 14px;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  font-weight: 500;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.stat-label {
  color: #6c757d;
  font-size: 12px;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.chart-section, .activity-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.07);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.section-header h2 {
  color: #2c3e50;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.market-overview, .activity-list {
  padding: 24px;
}

.empty-state {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.activity-icon.data_sync {
  background: #e3f2fd;
}

.activity-icon.analysis {
  background: #f3e5f5;
}

.activity-icon.alert {
  background: #fff3e0;
}

.activity-content {
  flex: 1;
}

.activity-message {
  color: #2c3e50;
  font-size: 14px;
  margin-bottom: 4px;
}

.activity-time {
  color: #6c757d;
  font-size: 12px;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 15px;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .dashboard-header h1 {
    font-size: 24px;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
  
  .stat-number {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>