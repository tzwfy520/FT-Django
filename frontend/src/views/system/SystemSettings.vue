<template>
  <div class="system-settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>系统设置</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshAll" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 设置导航卡片 -->
    <div class="settings-grid">
      <el-card 
        v-for="item in settingsItems" 
        :key="item.key"
        class="settings-card"
        shadow="hover"
        @click="navigateTo(item.path)"
      >
        <div class="card-content">
          <div class="card-icon">
            <el-icon :size="32" :color="item.color">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <div class="card-info">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统状态概览 -->
    <div class="system-status">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>系统状态概览</span>
            <el-button text @click="refreshStatus" :loading="statusLoading">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </template>
        
        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">系统运行时间</div>
            <div class="status-value">{{ systemStatus.uptime }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">数据库状态</div>
            <div class="status-value">
              <el-tag :type="systemStatus.database.status === 'connected' ? 'success' : 'danger'">
                {{ systemStatus.database.status === 'connected' ? '已连接' : '连接失败' }}
              </el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">存储状态</div>
            <div class="status-value">
              <el-tag :type="systemStatus.storage.status === 'connected' ? 'success' : 'danger'">
                {{ systemStatus.storage.status === 'connected' ? '正常' : '异常' }}
              </el-tag>
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">最后更新</div>
            <div class="status-value">{{ systemStatus.lastUpdate }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 子路由视图 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  ArrowRight,
  Monitor,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const refreshing = ref(false)
const statusLoading = ref(false)

// 设置项配置
const settingsItems = ref([
  {
    key: 'overview',
    title: '系统概览',
    description: '查看系统运行状态和基本信息',
    icon: Monitor,
    color: '#409EFF',
    path: '/system-settings/overview'
  }
])

// 系统状态
const systemStatus = ref({
  uptime: '0天 0小时 0分钟',
  database: {
    status: 'unknown'
  },
  storage: {
    status: 'unknown'
  },
  lastUpdate: '未知'
})

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

// 刷新所有数据
const refreshAll = async () => {
  refreshing.value = true
  try {
    await refreshStatus()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 刷新系统状态
const refreshStatus = async () => {
  statusLoading.value = true
  try {
    // TODO: 调用API获取系统状态
    // const response = await systemAPI.getStatus()
    // systemStatus.value = response.data
    
    // 模拟数据
    systemStatus.value = {
      uptime: '2天 14小时 32分钟',
      database: {
        status: 'connected'
      },
      storage: {
        status: 'connected'
      },
      lastUpdate: new Date().toLocaleString()
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
    ElMessage.error('获取系统状态失败')
  } finally {
    statusLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.system-settings {
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

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.settings-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.settings-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px;
}

.card-icon {
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
  line-height: 1.4;
}

.card-arrow {
  flex-shrink: 0;
  color: #C0C4CC;
}

.system-status {
  margin-top: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.status-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.status-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>