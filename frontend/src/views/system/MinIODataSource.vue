<template>
  <div class="minio-data-source">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" type="text" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>MinIO 股票分析数据源</h2>
      </div>
      <div class="header-right">
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="testConnection" type="primary" :loading="testingConnection">
          <el-icon><Connection /></el-icon>
          测试连接
        </el-button>
      </div>
    </div>

    <!-- 连接配置卡片 -->
    <el-card class="connection-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>MinIO 连接配置</span>
          <el-tag :type="connectionStatus === 'connected' ? 'success' : 'danger'">
            {{ connectionStatus === 'connected' ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </template>
      
      <el-form :model="minioConfig" label-width="120px" class="config-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务器地址">
              <el-input v-model="minioConfig.endpoint" placeholder="例如: minio.example.com:9000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="端口">
              <el-input-number v-model="minioConfig.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Access Key">
              <el-input v-model="minioConfig.accessKey" placeholder="MinIO Access Key" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Secret Key">
              <el-input 
                v-model="minioConfig.secretKey" 
                :type="showSecretKey ? 'text' : 'password'"
                placeholder="MinIO Secret Key"
              >
                <template #suffix>
                  <el-button @click="toggleSecretKey" type="text" size="small">
                    <el-icon><View v-if="!showSecretKey" /><Hide v-else /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="使用SSL">
              <el-switch v-model="minioConfig.useSSL" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域">
              <el-input v-model="minioConfig.region" placeholder="例如: us-east-1" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认存储桶">
              <el-input v-model="minioConfig.bucketName" placeholder="默认存储桶名称" readonly>
                <template #suffix>
                  <el-tag size="small" type="success">预设</el-tag>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button @click="saveConfig" type="primary" :loading="savingConfig">
            保存配置
          </el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 存储桶信息 -->
    <el-card class="buckets-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>存储桶信息</span>
          <div class="header-actions">
            <el-button @click="createBucketVisible = true" type="primary" size="small">
              <el-icon><Plus /></el-icon>
              创建存储桶
            </el-button>
            <el-button @click="loadBuckets" :loading="loadingBuckets" size="small">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="buckets" v-loading="loadingBuckets" stripe>
        <el-table-column prop="name" label="存储桶名称" width="200" />
        <el-table-column prop="creationDate" label="创建时间" width="180">
          <template #default="{ row }">
            <span>{{ formatDate(row.creationDate) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="objectCount" label="对象数量" width="120">
          <template #default="{ row }">
            <span>{{ formatNumber(row.objectCount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="总大小" width="120">
          <template #default="{ row }">
            <span>{{ formatSize(row.size) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="policy" label="访问策略" width="100">
          <template #default="{ row }">
            <el-tag :type="row.policy === 'public' ? 'success' : 'info'" size="small">
              {{ row.policy === 'public' ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button @click="viewBucketObjects(row)" type="text" size="small">
              查看对象
            </el-button>
            <el-button @click="manageBucketPolicy(row)" type="text" size="small">
              管理策略
            </el-button>
            <el-button @click="deleteBucket(row)" type="text" size="small" class="danger-btn">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建存储桶对话框 -->
    <el-dialog v-model="createBucketVisible" title="创建存储桶" width="500px">
      <el-form :model="newBucket" label-width="100px">
        <el-form-item label="存储桶名称" required>
          <el-input v-model="newBucket.name" placeholder="请输入存储桶名称" />
        </el-form-item>
        <el-form-item label="访问策略">
          <el-select v-model="newBucket.policy" style="width: 100%">
            <el-option label="私有" value="private" />
            <el-option label="公开" value="public" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newBucket.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createBucketVisible = false">取消</el-button>
        <el-button @click="createBucket" type="primary" :loading="creatingBucket">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 存储桶对象查看对话框 -->
    <el-dialog v-model="objectsVisible" :title="`存储桶对象 - ${selectedBucket?.name}`" width="80%" top="5vh">
      <div class="objects-header">
        <el-input 
          v-model="objectSearchKey" 
          placeholder="搜索对象..."
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadBucketObjects" :loading="loadingObjects">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <el-table :data="filteredObjects" v-loading="loadingObjects" stripe max-height="400">
        <el-table-column prop="key" label="对象键" width="300" show-overflow-tooltip />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            <span>{{ formatSize(row.size) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastModified" label="最后修改" width="180">
          <template #default="{ row }">
            <span>{{ formatDate(row.lastModified) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="etag" label="ETag" width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button @click="downloadObject(row)" type="text" size="small">
              下载
            </el-button>
            <el-button @click="deleteObject(row)" type="text" size="small" class="danger-btn">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, Connection, View, Hide, Plus, Search } from '@element-plus/icons-vue'

interface Bucket {
  name: string
  creationDate: Date
  objectCount: number
  size: number
  policy: string
  description: string
}

interface MinIOObject {
  key: string
  size: number
  lastModified: Date
  etag: string
}

const router = useRouter()

// 响应式数据
const loading = ref(false)
const testingConnection = ref(false)
const savingConfig = ref(false)
const loadingBuckets = ref(false)
const loadingObjects = ref(false)
const creatingBucket = ref(false)
const showSecretKey = ref(false)
const connectionStatus = ref('disconnected')
const createBucketVisible = ref(false)
const objectsVisible = ref(false)
const selectedBucket = ref<Bucket | null>(null)
const objectSearchKey = ref('')

// MinIO 配置
const minioConfig = reactive({
  endpoint: '139.196.196.96:29000',
  port: 29000,
  accessKey: 'minioadmin',
  secretKey: 'Eccom@2024',
  useSSL: false,
  region: 'us-east-1',
  bucketName: 'ai-ft-analysis'
})

// 新建存储桶
const newBucket = reactive({
  name: '',
  policy: 'private',
  description: ''
})

// 存储桶和对象数据
const buckets = ref<Bucket[]>([])
const objects = ref<MinIOObject[]>([])

// 计算属性
const filteredObjects = computed(() => {
  if (!objectSearchKey.value) return objects.value
  return objects.value.filter(obj => 
    obj.key.toLowerCase().includes(objectSearchKey.value.toLowerCase())
  )
})

// 返回数据源管理
const goBack = () => {
  router.push('/system-settings/data-source')
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      checkConnection(),
      loadBuckets()
    ])
  } finally {
    loading.value = false
  }
}

const toggleSecretKey = () => {
  showSecretKey.value = !showSecretKey.value
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    connectionStatus.value = 'connected'
    ElMessage.success('MinIO连接测试成功')
  } catch (error) {
    connectionStatus.value = 'disconnected'
    ElMessage.error('MinIO连接测试失败')
  } finally {
    testingConnection.value = false
  }
}

const checkConnection = async () => {
  try {
    // 模拟API调用检查连接状态
    await new Promise(resolve => setTimeout(resolve, 500))
    connectionStatus.value = 'connected'
  } catch (error) {
    connectionStatus.value = 'disconnected'
  }
}

const saveConfig = async () => {
  savingConfig.value = true
  try {
    // 模拟API调用保存配置
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    savingConfig.value = false
  }
}

const resetConfig = () => {
  Object.assign(minioConfig, {
    endpoint: 'minio.example.com',
    port: 9000,
    accessKey: 'minioadmin',
    secretKey: 'minioadmin',
    useSSL: false,
    region: 'us-east-1'
  })
}

const loadBuckets = async () => {
  loadingBuckets.value = true
  try {
    // 模拟API调用获取存储桶信息
    await new Promise(resolve => setTimeout(resolve, 1000))
    buckets.value = [
      {
        name: 'ai-ft-analysis',
        creationDate: new Date('2024-01-15'),
        objectCount: 1250,
        size: 2147483648, // 2GB
        policy: 'private',
        description: 'AI金融分析主存储桶'
      },
      {
        name: 'stock-data',
        creationDate: new Date('2024-01-20'),
        objectCount: 850,
        size: 524288000, // 500MB
        policy: 'private',
        description: '股票数据存储桶'
      },
      {
        name: 'analysis-reports',
        creationDate: new Date('2024-01-22'),
        objectCount: 185,
        size: 268435456, // 256MB
        policy: 'public',
        description: '分析报告存储桶'
      },
      {
        name: 'model-files',
        creationDate: new Date('2024-01-10'),
        objectCount: 25,
        size: 5368709120, // 5GB
        policy: 'private',
        description: 'AI模型文件存储桶'
      },
      {
        name: 'backup-data',
        creationDate: new Date('2024-01-25'),
        objectCount: 320,
        size: 1073741824, // 1GB
        policy: 'private',
        description: '备份数据存储桶'
      }
    ]
  } catch (error) {
    ElMessage.error('加载存储桶信息失败')
  } finally {
    loadingBuckets.value = false
  }
}

const createBucket = async () => {
  if (!newBucket.name.trim()) {
    ElMessage.warning('请输入存储桶名称')
    return
  }
  
  creatingBucket.value = true
  try {
    // 模拟API调用创建存储桶
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('存储桶创建成功')
    createBucketVisible.value = false
    
    // 重置表单
    Object.assign(newBucket, {
      name: '',
      policy: 'private',
      description: ''
    })
    
    // 刷新存储桶列表
    await loadBuckets()
  } catch (error) {
    ElMessage.error('存储桶创建失败')
  } finally {
    creatingBucket.value = false
  }
}

const viewBucketObjects = async (bucket: Bucket) => {
  selectedBucket.value = bucket
  objectsVisible.value = true
  await loadBucketObjects()
}

const loadBucketObjects = async () => {
  loadingObjects.value = true
  try {
    // 模拟API调用获取对象列表
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟对象数据
    objects.value = [
      {
        key: 'analysis/2024/01/stock_analysis_20240115.json',
        size: 1048576, // 1MB
        lastModified: new Date('2024-01-15 14:30:00'),
        etag: '"d41d8cd98f00b204e9800998ecf8427e"'
      },
      {
        key: 'reports/market_summary_20240115.pdf',
        size: 2097152, // 2MB
        lastModified: new Date('2024-01-15 16:45:00'),
        etag: '"098f6bcd4621d373cade4e832627b4f6"'
      },
      {
        key: 'models/lstm_model_v1.0.pkl',
        size: 52428800, // 50MB
        lastModified: new Date('2024-02-01 10:20:00'),
        etag: '"5d41402abc4b2a76b9719d911017c592"'
      }
    ]
  } catch (error) {
    ElMessage.error('加载对象列表失败')
  } finally {
    loadingObjects.value = false
  }
}

const manageBucketPolicy = (bucket: Bucket) => {
  ElMessage.info('存储桶策略管理功能开发中...')
}

const deleteBucket = async (bucket: Bucket) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除存储桶 "${bucket.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟API调用删除存储桶
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('存储桶删除成功')
    await loadBuckets()
  } catch (error) {
    // 用户取消删除
  }
}

const downloadObject = (object: MinIOObject) => {
  ElMessage.info(`开始下载: ${object.key}`)
}

const deleteObject = async (object: MinIOObject) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除对象 "${object.key}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟API调用删除对象
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('对象删除成功')
    await loadBucketObjects()
  } catch (error) {
    // 用户取消删除
  }
}

const formatNumber = (num: number) => {
  return num?.toLocaleString() || '0'
}

const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const formatDate = (date: Date | string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.minio-data-source {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 4px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  padding: 8px;
  color: #606266;
}

.back-btn:hover {
  color: #409eff;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 12px;
}

.connection-card,
.buckets-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.config-form {
  margin-top: 20px;
}

.objects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.danger-btn {
  color: #f56c6c;
}

.danger-btn:hover {
  color: #f78989;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: center;
  }
  
  .objects-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>