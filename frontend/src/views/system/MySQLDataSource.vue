<template>
  <div class="mysql-data-source">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" type="text" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>MySQL 股票交易数据源</h2>
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

    <!-- 连接信息卡片 -->
    <el-card class="connection-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>数据库连接信息</span>
          <el-tag :type="connectionStatus === 'connected' ? 'success' : 'danger'">
            {{ connectionStatus === 'connected' ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </template>
      
      <div class="connection-info">
        <div class="info-row">
          <label>服务器地址：</label>
          <span class="info-value">{{ dbConfig.host }}</span>

        </div>
        <div class="info-row">
          <label>端口：</label>
          <span class="info-value">{{ dbConfig.port }}</span>
        </div>
        <div class="info-row">
          <label>用户名：</label>
          <span class="info-value">{{ dbConfig.username }}</span>
        </div>
        <div class="info-row">
          <label>密码：</label>
          <span class="info-value" v-if="!showPassword">••••••••••</span>
          <span class="info-value password-text" v-else>{{ dbConfig.password }}</span>
          <el-button @click="togglePassword" type="text" size="small" class="password-toggle">
            <el-icon><View v-if="!showPassword" /><Hide v-else /></el-icon>
            {{ showPassword ? '隐藏' : '查看' }}
          </el-button>
        </div>
        <div class="info-row">
          <label>数据库：</label>
          <span class="info-value">{{ dbConfig.database }}</span>
        </div>
        <div class="info-row">
          <label>字符集：</label>
          <span class="info-value">{{ dbConfig.charset }}</span>
        </div>
        <div class="info-row">
          <label>连接超时：</label>
          <span class="info-value">{{ dbConfig.connectionTimeout / 1000 }}秒</span>
        </div>
        <div class="info-row">
          <label>最大连接数：</label>
          <span class="info-value">{{ dbConfig.maxConnections }}</span>
        </div>
      </div>
    </el-card>

    <!-- 数据表信息 -->
    <el-card class="tables-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>数据表信息</span>
          <el-button @click="loadTables" :loading="loadingTables" size="small">
            <el-icon><Refresh /></el-icon>
            刷新表信息
          </el-button>
        </div>
      </template>
      
      <div v-loading="loadingTables">
        <el-collapse v-model="activeGroups" v-if="tableGroups.length > 0">
          <el-collapse-item 
            v-for="(group, index) in tableGroups" 
            :key="group.groupName"
            :title="`${group.groupName} (${group.count}个表)`"
            :name="index.toString()"
          >
            <el-table :data="group.tables" stripe>
              <el-table-column prop="name" label="表名" width="200" />
              <el-table-column prop="rows" label="行数" width="120" sortable>
                <template #default="{ row }">
                  <span>{{ formatNumber(row.rows) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="size" label="大小" width="120">
                <template #default="{ row }">
                  <span>{{ formatSize(row.size) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="engine" label="存储引擎" width="100" />
              <el-table-column prop="collation" label="字符集" width="150" />
              <el-table-column prop="callingModules" label="调用模块" show-overflow-tooltip>
                <template #default="{ row }">
                  <span v-if="row.callingModules && row.callingModules.length > 0">
                    {{ row.callingModules.join(';') }}
                  </span>
                  <span v-else class="no-modules">暂无调用</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="280">
                <template #default="{ row }">
                  <el-button @click="viewTableData(row)" type="text" size="small">
                    查看数据
                  </el-button>
                  <el-button @click="viewTableStructure(row)" type="text" size="small">
                    查看表结构
                  </el-button>
                  <el-button @click="deleteTable(row)" type="text" size="small" class="delete-btn">
                    删除表
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
        <el-empty v-else description="暂无数据表" />
      </div>
    </el-card>

    <!-- 表数据查看对话框 -->
    <el-dialog v-model="tableDataVisible" :title="`表数据 - ${selectedTable?.name}`" width="80%" top="5vh">
      <el-table :data="tableData" v-loading="loadingTableData" stripe max-height="400">
        <el-table-column 
          v-for="column in tableColumns" 
          :key="column.field"
          :prop="column.field"
          :label="column.field"
          :width="column.width"
          show-overflow-tooltip
        />
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalRows"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-dialog>

    <!-- 表结构查看对话框 -->
    <el-dialog v-model="tableStructureVisible" :title="`表结构 - ${selectedTable?.name}`" width="90%" top="3vh">
      <div v-loading="loadingTableStructure">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- DDL信息 -->
          <el-tab-pane label="DDL信息" name="ddl">
            <div class="ddl-container">
              <div class="ddl-header">
                <span>表创建语句</span>
                <el-button @click="copyDDL" size="small" type="primary">复制</el-button>
              </div>
              <pre class="ddl-content" ref="ddlContent">{{ tableStructure?.ddl_info?.create_statement }}</pre>
            </div>
          </el-tab-pane>
          
          <!-- 表结构 -->
          <el-tab-pane label="表结构" name="structure">
            <el-table :data="tableStructure?.columns_info" stripe>
              <el-table-column prop="field" label="字段名" width="150" />
              <el-table-column prop="type" label="数据类型" width="150" />
              <el-table-column prop="null" label="允许NULL" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.null === 'YES' ? 'success' : 'danger'" size="small">
                    {{ row.null === 'YES' ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="key" label="键类型" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.key" :type="getKeyType(row.key)" size="small">
                    {{ getKeyLabel(row.key) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="default" label="默认值" width="120">
                <template #default="{ row }">
                  <span v-if="row.default !== null">{{ row.default }}</span>
                  <span v-else class="null-value">NULL</span>
                </template>
              </el-table-column>
              <el-table-column prop="extra" label="额外信息" show-overflow-tooltip />
            </el-table>
          </el-tab-pane>
          
          <!-- 索引信息 -->
          <el-tab-pane label="索引信息" name="indexes">
            <el-table :data="tableStructure?.indexes_info" stripe>
              <el-table-column prop="key_name" label="索引名" width="150" />
              <el-table-column prop="column_name" label="列名" width="150" />
              <el-table-column prop="non_unique" label="唯一性" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.non_unique === 0 ? 'success' : 'info'" size="small">
                    {{ row.non_unique === 0 ? '唯一' : '非唯一' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="index_type" label="索引类型" width="100" />
              <el-table-column prop="cardinality" label="基数" width="100" />
              <el-table-column prop="comment" label="注释" show-overflow-tooltip />
            </el-table>
          </el-tab-pane>
          
          <!-- 统计信息 -->
          <el-tab-pane label="统计信息" name="stats">
            <div class="stats-container">
              <div class="stats-grid">
                <div class="stat-item">
                  <label>表行数：</label>
                  <span>{{ formatNumber(tableStructure?.stats_info?.rows) }}</span>
                </div>
                <div class="stat-item">
                  <label>数据大小：</label>
                  <span>{{ formatSize(tableStructure?.stats_info?.data_length) }}</span>
                </div>
                <div class="stat-item">
                  <label>索引大小：</label>
                  <span>{{ formatSize(tableStructure?.stats_info?.index_length) }}</span>
                </div>
                <div class="stat-item">
                  <label>存储引擎：</label>
                  <span>{{ tableStructure?.stats_info?.engine }}</span>
                </div>
                <div class="stat-item">
                  <label>字符集：</label>
                  <span>{{ tableStructure?.stats_info?.collation }}</span>
                </div>
                <div class="stat-item">
                  <label>自增值：</label>
                  <span>{{ tableStructure?.stats_info?.auto_increment || 'N/A' }}</span>
                </div>
                <div class="stat-item">
                  <label>创建时间：</label>
                  <span>{{ formatDateTime(tableStructure?.stats_info?.create_time) }}</span>
                </div>
                <div class="stat-item">
                  <label>更新时间：</label>
                  <span>{{ formatDateTime(tableStructure?.stats_info?.update_time) }}</span>
                </div>
                <div class="stat-item full-width">
                  <label>表注释：</label>
                  <span>{{ tableStructure?.stats_info?.comment || '无注释' }}</span>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, Connection, View, Hide } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const testingConnection = ref(false)
const loadingTables = ref(false)
const loadingTableData = ref(false)
const loadingTableStructure = ref(false)
const showPassword = ref(false)
const connectionStatus = ref('disconnected')
const tableDataVisible = ref(false)
const tableStructureVisible = ref(false)
const selectedTable = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const activeTab = ref('ddl')

// 数据库配置
const dbConfig = reactive({
  host: '115.190.80.219',
  port: 3306,
  username: 'root',
  password: 'Eccom@12345',
  database: 'django_stock',
  charset: 'utf8mb4',
  connectionTimeout: 30000,
  maxConnections: 10
})

// 表数据
const tables = ref([])
const tableGroups = ref([])
const activeGroups = ref([])

// 表结构数据
const tableStructure = ref(null)
const tableData = ref([])
const tableColumns = ref([])

// 返回数据源管理
const goBack = () => {
  router.push('/system-settings/data-source')
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      checkConnection(),
      loadTables()
    ])
  } finally {
    loading.value = false
  }
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    connectionStatus.value = 'connected'
    ElMessage.success('数据库连接测试成功')
  } catch (error) {
    connectionStatus.value = 'disconnected'
    ElMessage.error('数据库连接测试失败')
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

const loadTables = async () => {
  loadingTables.value = true
  try {
    // 获取MySQL数据源ID（假设是第一个MySQL数据源）
    const dataSourceResponse = await fetch('/api/v1/system/datasources/')
    if (!dataSourceResponse.ok) {
      throw new Error('获取数据源失败')
    }
    const dataSourceResult = await dataSourceResponse.json()
    
    if (!dataSourceResult.success || !dataSourceResult.data.sources.length) {
      throw new Error('未找到数据源')
    }
    
    // 找到MySQL类型的数据源
    const mysqlSource = dataSourceResult.data.sources.find(source => source.source_type === 'mysql')
    if (!mysqlSource) {
      throw new Error('未找到MySQL数据源')
    }
    
    // 调用API获取表信息
    const response = await fetch(`/api/v1/system/datasources/${mysqlSource.id}/mysql-tables/`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    if (result.success) {
      tableGroups.value = result.data.tableGroups || []
      // 初始化所有分组为展开状态
      activeGroups.value = tableGroups.value.map((group, index) => index.toString())
      // 保持向后兼容，如果返回的是旧格式
      tables.value = result.data.tables || []
    } else {
      throw new Error(result.message || '获取表信息失败')
    }
  } catch (error) {
    console.error('加载表信息失败:', error)
    ElMessage.error('加载表信息失败: ' + (error.message || error))
  } finally {
    loadingTables.value = false
  }
}

const viewTableData = async (table) => {
  selectedTable.value = table
  tableDataVisible.value = true
  currentPage.value = 1
  await loadTableData()
}

const deleteTable = async (table) => {
  try {
    // 二次确认
    await ElMessageBox.confirm(
      `确定要删除表 "${table.name}" 吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 获取MySQL数据源ID
    const dataSourceResponse = await fetch('http://localhost:8000/api/v1/system/datasources/')
    if (!dataSourceResponse.ok) {
      throw new Error('获取数据源失败')
    }
    const dataSourceResult = await dataSourceResponse.json()
    
    const mysqlSource = dataSourceResult.data.sources.find(source => source.source_type === 'mysql')
    if (!mysqlSource) {
      throw new Error('未找到MySQL数据源')
    }
    
    // 调用删除API
    const response = await fetch(`/api/v1/system/datasources/${mysqlSource.id}/mysql-tables/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ table_name: tableName })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    if (result.success) {
      ElMessage.success(result.message || '表删除成功')
      // 刷新表列表
      await loadTables()
    } else {
      throw new Error(result.message || '删除表失败')
    }
  } catch (error) {
    if (error.message !== 'cancel') {
      console.error('删除表失败:', error)
      ElMessage.error('删除表失败: ' + (error.message || error))
    }
  }
}

const loadTableData = async () => {
  loadingTableData.value = true
  try {
    // 模拟API调用获取表数据
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟表结构和数据
    if (selectedTable.value?.name === 'stock_basic_info') {
      tableColumns.value = [
        { field: 'id', width: 80 },
        { field: 'code', width: 100 },
        { field: 'name', width: 120 },
        { field: 'industry', width: 100 },
        { field: 'market', width: 80 },
        { field: 'list_date', width: 120 },
        { field: 'created_at', width: 160 }
      ]
      
      tableData.value = [
        {
          id: 1,
          code: '000001',
          name: '平安银行',
          industry: '银行',
          market: '深市',
          list_date: '1991-04-03',
          created_at: '2024-01-15 10:30:00'
        },
        {
          id: 2,
          code: '000002',
          name: '万科A',
          industry: '房地产',
          market: '深市',
          list_date: '1991-01-29',
          created_at: '2024-01-15 10:30:00'
        }
      ]
      totalRows.value = selectedTable.value.rows
    }
  } catch (error) {
    ElMessage.error('加载表数据失败')
  } finally {
    loadingTableData.value = false
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadTableData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadTableData()
}

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const formatSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  
  const units = ['B', 'K', 'M', 'G', 'T']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  // 根据大小选择合适的小数位数
  const decimals = size >= 100 ? 0 : size >= 10 ? 1 : 2
  return `${size.toFixed(decimals)} ${units[unitIndex]}`
}

// 查看表结构
const viewTableStructure = async (table) => {
  selectedTable.value = table
  tableStructureVisible.value = true
  activeTab.value = 'ddl'
  
  loadingTableStructure.value = true
  try {
    // 获取MySQL数据源ID
    const dataSourceResponse = await fetch('/api/v1/system/datasources/')
    if (!dataSourceResponse.ok) {
      throw new Error('获取数据源失败')
    }
    const dataSourceResult = await dataSourceResponse.json()
    
    if (!dataSourceResult.success || !dataSourceResult.data.sources.length) {
      throw new Error('未找到数据源')
    }
    
    const mysqlSource = dataSourceResult.data.sources.find(source => source.source_type === 'mysql')
    if (!mysqlSource) {
      throw new Error('未找到MySQL数据源')
    }
    
    // 调用表结构API
    const response = await fetch(`/api/v1/system/datasources/${mysqlSource.id}/mysql-tables/${table.name}/structure/`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    if (result.success) {
      tableStructure.value = result.data
    } else {
      throw new Error(result.message || '获取表结构失败')
    }
  } catch (error) {
    console.error('获取表结构失败:', error)
    ElMessage.error(`获取表结构失败: ${error.message}`)
    tableStructureVisible.value = false
  } finally {
    loadingTableStructure.value = false
  }
}

// 复制DDL语句
const copyDDL = async () => {
  try {
    const ddlText = tableStructure.value?.ddl_info?.create_statement
    if (ddlText) {
      await navigator.clipboard.writeText(ddlText)
      ElMessage.success('DDL语句已复制到剪贴板')
    } else {
      ElMessage.warning('没有可复制的DDL语句')
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择复制')
  }
}

// 获取键类型标签
const getKeyLabel = (key) => {
  const keyMap = {
    'PRI': '主键',
    'UNI': '唯一',
    'MUL': '索引'
  }
  return keyMap[key] || key
}

// 获取键类型颜色
const getKeyType = (key) => {
  const typeMap = {
    'PRI': 'danger',
    'UNI': 'warning', 
    'MUL': 'info'
  }
  return typeMap[key] || 'info'
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return 'N/A'
  try {
    const date = new Date(dateTimeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return dateTimeStr
  }
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.mysql-data-source {
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

.delete-btn {
  color: #f56c6c !important;
}

.delete-btn:hover {
  color: #f78989 !important;
}

.connection-card,
.tables-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.connection-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  font-weight: 500;
  color: #606266;
  min-width: 100px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  flex: 1;
}

.password-text {
  color: #e6a23c;
  font-weight: 500;
}

.password-toggle {
  margin-left: 8px;
  color: #409eff;
}

.password-toggle:hover {
  color: #66b1ff;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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
  
  .connection-info {
    grid-template-columns: 1fr;
  }
}
.no-modules {
  color: #909399;
  font-style: italic;
}

/* 表结构对话框样式 */
.ddl-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.ddl-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 500;
}

.ddl-content {
  padding: 16px;
  margin: 0;
  background-color: #fafafa;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.stats-container {
  padding: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.stat-item.full-width {
  grid-column: 1 / -1;
}

.stat-item label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
  margin-right: 8px;
}

.stat-item span {
  color: #303133;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.null-value {
  color: #909399;
  font-style: italic;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>