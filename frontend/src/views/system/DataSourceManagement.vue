<template>
  <div class="datasource-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>数据管理</h1>
      <div class="header-actions">
        <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        <el-button type="primary" @click="refreshAll" :loading="refreshing" icon="Refresh">
          刷新状态
        </el-button>
      </div>
    </div>

    <!-- 数据源表格 -->
    <el-card class="data-table-card">
      <template #header>
        <div class="card-header">
          <span>数据源信息</span>
        </div>
      </template>
      
      <el-table :data="dataSourceList" stripe style="width: 100%">
        <el-table-column prop="name" label="数据库(桶)" width="200" />
        <el-table-column prop="source_type" label="数据库类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.source_type === 'mysql' ? 'primary' : 'warning'">
              {{ row.source_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" width="200" />
        <el-table-column prop="config.host" label="IP地址" width="150" />
        <el-table-column prop="config.port" label="端口" width="100" />
        <el-table-column prop="config.username" label="用户名" width="150" />
        <el-table-column prop="config.password" label="密码" width="150">
          <template #default="{ row }">
            <span v-if="!row.passwordVisible">••••••••</span>
            <span v-else>{{ row.config.password }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              @click="viewTables(row)" 
              type="primary" 
              size="small"
              :loading="row.loading"
            >
              {{ row.source_type === 'mysql' ? '查看表' : '查看桶' }}
            </el-button>
            <el-button 
              @click="togglePassword(row)" 
              type="info" 
              size="small"
            >
              {{ row.passwordVisible ? '隐藏密码' : '查看密码' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- MySQL 表信息对话框 -->
    <el-dialog 
      v-model="mysqlTablesVisible" 
      title="MySQL 数据表信息" 
      width="80%"
      :before-close="handleClose"
    >
      <MySQLDataSource />
    </el-dialog>

    <!-- MinIO 存储桶对话框 -->
    <el-dialog 
      v-model="minioBucketsVisible" 
      title="MinIO 存储桶信息" 
      width="80%"
      :before-close="handleClose"
    >
      <MinIODataSource />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Refresh
} from '@element-plus/icons-vue'
import MySQLDataSource from './MySQLDataSource.vue'
import MinIODataSource from './MinIODataSource.vue'

const router = useRouter()
const refreshing = ref(false)
const mysqlTablesVisible = ref(false)
const minioBucketsVisible = ref(false)

// 数据源列表
const dataSourceList = ref([])
const loading = ref(false)

// 返回系统设置
const goBack = () => {
  router.push('/system-settings')
}

// 获取数据源列表
const fetchDataSources = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/system/datasources/')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const result = await response.json()
    if (result.success) {
      // 转换后端数据格式为前端需要的格式
      dataSourceList.value = result.data.sources.map((source: any) => ({
        ...source,
        passwordVisible: false,
        loading: false,
        is_active: source.is_active,
        last_sync_time: source.last_sync_time,
        created_at: source.created_at
      }))
    } else {
      throw new Error(result.message || '获取数据源列表失败')
    }
  } catch (error: any) {
    console.error('获取数据源列表失败:', error)
    ElMessage.error('获取数据源列表失败: ' + (error.message || error))
  } finally {
    loading.value = false
  }
}

// 刷新所有状态
const refreshAll = async () => {
  refreshing.value = true
  try {
    await fetchDataSources()
    ElMessage.success('状态刷新成功')
  } catch (error: any) {
    ElMessage.error('状态刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 查看表/桶
const viewTables = (row: any) => {
  row.loading = true
  setTimeout(() => {
    row.loading = false
    if (row.source_type === 'mysql') {
      mysqlTablesVisible.value = true
    } else if (row.source_type === 'minio') {
      minioBucketsVisible.value = true
    } else {
      ElMessage.warning(`暂不支持 ${row.source_type} 类型的数据源查看`)
    }
  }, 1000)
}

// 关闭对话框
const handleClose = (done: () => void) => {
  done()
}

// 切换密码可见性
const togglePassword = async (row: any) => {
  if (!row.passwordVisible) {
    // 显示密码 - 从后端获取真实密码
    try {
      const response = await fetch(`http://localhost:8000/api/v1/system/datasources/${row.id}/password/`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      if (result.success) {
        row.config.password = result.data.password
        row.passwordVisible = true
        
        // 5秒后自动隐藏密码
        setTimeout(() => {
          row.passwordVisible = false
          row.config.password = '***'
        }, 5000)
      } else {
        throw new Error(result.message || '获取密码失败')
      }
    } catch (error: any) {
      console.error('获取密码失败:', error)
      ElMessage.error('获取密码失败: ' + (error.message || error))
    }
  } else {
    // 隐藏密码
    row.passwordVisible = false
    row.config.password = '***'
  }
}

// 组件挂载时加载数据
onMounted(() => {
  fetchDataSources()
})
</script>

<style scoped>
.datasource-management {
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

.overview-row {
  margin-bottom: 24px;
}

.overview-card {
  height: 100%;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px;
}

.overview-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.overview-icon.mysql {
  background: linear-gradient(135deg, #4285f4, #34a853);
}

.overview-icon.minio {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.overview-content {
  flex: 1;
}

.overview-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.overview-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.overview-status {
  display: flex;
  align-items: center;
}

.datasource-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.header-icon.mysql {
  color: #4285f4;
}

.header-icon.minio {
  color: #ff6b6b;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.config-content {
  padding: 16px 0;
}

.config-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.status-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.form-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}
</style>