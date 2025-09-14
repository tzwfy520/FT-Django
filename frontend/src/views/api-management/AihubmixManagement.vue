<template>
  <div class="aihubmix-management">
    <div class="content">
      <!-- API Token 管理表格 -->
      <el-card class="token-card" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>API Token 管理</span>
            <el-button 
              type="primary"
              @click="showTokenModal = true"
              icon="Setting"
            >
              设置 Token
            </el-button>
          </div>
        </template>

        <div v-if="!apiToken" class="token-info no-token">
          <el-alert
            title="未配置 API Token"
            description="请先配置 API Token 以使用接口管理功能"
            type="warning"
            show-icon
            :closable="false"
          />
        </div>

        <div v-else class="token-info has-token">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="当前 Token">
              <div class="token-display">
                <el-input
                  v-model="maskedToken"
                  readonly
                  :type="showFullToken ? 'text' : 'password'"
                  style="width: 300px;"
                >
                  <template #append>
                    <el-button
                      @click="toggleTokenVisibility"
                      :icon="showFullToken ? 'Hide' : 'View'"
                    />
                  </template>
                </el-input>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag type="success" effect="light">
                <el-icon><Check /></el-icon>
                已配置
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="配置时间">
              {{ formatDate(new Date().toISOString()) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>



      <!-- 接口配置管理表格 -->
      <el-card class="interfaces-card">
        <template #header>
          <div class="card-header">
            <span>接口配置管理</span>
            <el-button 
              type="primary" 
              @click="createInterface"
              :disabled="!apiToken"
              icon="Plus"
            >
              新增接口
            </el-button>
          </div>
        </template>
        
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="apiInterfaces.length === 0" class="empty-state">
          <el-empty description="暂无接口配置">
            <el-button type="primary" @click="createInterface" :disabled="!apiToken">
              创建第一个接口
            </el-button>
          </el-empty>
        </div>

        <el-table v-else :data="apiInterfaces" stripe style="width: 100%">
          <el-table-column prop="name" label="接口名称" width="200" />
          <el-table-column label="接口用途" width="300">
            <el-table-column label="股票复盘" width="100" align="center">
              <template #default="{ row }">
                <el-icon v-if="hasPurpose(row, 'stock_review')" color="#67C23A" size="16">
                  <Check />
                </el-icon>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="实时盯盘" width="100" align="center">
              <template #default="{ row }">
                <el-icon v-if="hasPurpose(row, 'real_time_monitoring')" color="#67C23A" size="16">
                  <Check />
                </el-icon>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="股票推荐" width="100" align="center">
              <template #default="{ row }">
                <el-icon v-if="hasPurpose(row, 'stock_recommendation')" color="#67C23A" size="16">
                  <Check />
                </el-icon>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table-column>
          <el-table-column prop="model" label="model名称" width="150">
            <template #default="{ row }">
              <el-tag type="primary">{{ row.model }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="temperature" label="temperature" width="120">
            <template #default="{ row }">
              <span>{{ row.temperature || 0.8 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="max_tokens" label="max_tokens" width="120">
            <template #default="{ row }">
              <span>{{ row.max_tokens || 1024 }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button 
                @click="editInterface(row)" 
                type="primary" 
                size="small"
              >
                编辑
              </el-button>
              <el-button 
                @click="testInterface(row)" 
                type="success" 
                size="small"
              >
                测试
              </el-button>
              <el-button 
                @click="deleteInterface(row)" 
                type="danger" 
                size="small"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Token 设置模态框 -->
    <TokenModal 
      v-if="showTokenModal"
      :token="apiToken"
      @close="showTokenModal = false"
      @saved="onTokenSaved"
    />

    <!-- 接口配置模态框 -->
    <InterfaceModal 
      v-if="showCreateModal"
      :apiInterface="editingInterface"
      @close="closeCreateModal"
      @saved="onInterfaceSaved"
    />

    <!-- 接口测试模态框 -->
    <TestModal 
      v-if="showTestModal"
      :apiInterface="testingInterface"
      @close="showTestModal = false"
    />

    <!-- Temperature修改模态框 -->
    <div v-if="showTemperatureModal" class="modal-overlay" @click="closeTemperatureModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-thermometer-half"></i>
            修改Temperature: {{ currentInterface?.name }}
          </h5>
          <button type="button" class="btn-close" @click="closeTemperatureModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="temperatureValue" class="form-label">Temperature值 (0.0 - 2.0)</label>
            <input 
              id="temperatureValue" 
              v-model.number="temperatureValue" 
              type="number" 
              class="form-control" 
              min="0" 
              max="2" 
              step="0.1" 
              placeholder="请输入Temperature值"
            />
            <small class="form-text text-muted">
              较低的值使输出更确定，较高的值使输出更随机
            </small>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeTemperatureModal">
            取消
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="saveTemperature"
            :disabled="temperatureValue < 0 || temperatureValue > 2"
          >
            <i class="fas fa-save"></i>
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- Max Tokens修改模态框 -->
    <div v-if="showMaxTokensModal" class="modal-overlay" @click="closeMaxTokensModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-coins"></i>
            修改Max Tokens: {{ currentInterface?.name }}
          </h5>
          <button type="button" class="btn-close" @click="closeMaxTokensModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="maxTokensValue" class="form-label">Max Tokens值</label>
            <input 
              id="maxTokensValue" 
              v-model.number="maxTokensValue" 
              type="number" 
              class="form-control" 
              min="1" 
              max="4096" 
              placeholder="请输入Max Tokens值"
            />
            <small class="form-text text-muted">
              控制生成文本的最大长度，建议值：1-4096
            </small>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeMaxTokensModal">
            取消
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="saveMaxTokens"
            :disabled="maxTokensValue < 1 || maxTokensValue > 4096"
          >
            <i class="fas fa-save"></i>
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import apiClient, { apiManagementAPI } from '@/services/api'
import TokenModal from './components/TokenModal.vue'
import InterfaceModal from './components/InterfaceModal.vue'
import TestModal from './components/TestModal.vue'
import { Hide, View, Check, Plus, Setting } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const apiToken = ref<any>(null)
const apiInterfaces = ref<any[]>([])
const showTokenModal = ref(false)
const showCreateModal = ref(false)
const showInterfaceModal = ref(false)
const showTestModal = ref(false)
const showTemperatureModal = ref(false)
const showMaxTokensModal = ref(false)
const editingInterface = ref<any>(null)
const testingInterface = ref<any>(null)
const currentInterface = ref<any>(null)
const temperatureValue = ref(0)
const maxTokensValue = ref(0)
const testContent = ref('')
const testResult = ref('')
const testLoading = ref(false)
const showFullToken = ref(false)

// 生命周期
onMounted(() => {
  loadData()
})

// 方法
const hasPurpose = (row: any, purpose: string) => {
  if (!row.purposes) return false
  if (Array.isArray(row.purposes)) {
    return row.purposes.includes(purpose)
  }
  return false
}

const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadApiToken(),
      loadInterfaces()
    ])
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadApiToken = async () => {
  try {
    const response = await apiManagementAPI.getTokens()
    const tokens = response.data.results || response.data
    // 查找推理时代的token
    apiToken.value = tokens.find((token: any) => token.provider_name === '推理时代') || null
  } catch (error) {
    console.error('加载API Token失败:', error)
  }
}

const loadInterfaces = async () => {
  try {
    const response = await apiManagementAPI.getInterfaces({
      provider: 1 // 推理时代的provider_id
    })
    const loadedInterfaces = response.data.results || response.data
    
    // 如果没有数据，添加示例数据以展示表格布局
    if (!loadedInterfaces || loadedInterfaces.length === 0) {
      apiInterfaces.value = [
        {
          id: 'demo-1',
          name: 'GPT-4 智能助手',
          purpose: '通用AI对话助手，适用于各种场景',
          purposes: ['stock_review', 'real_time_monitoring'],
          model: 'gpt-4',
          temperature: 0.7,
          max_tokens: 2048,
          is_active: true,
          created_at: new Date().toISOString(),
          is_demo: true
        },
        {
          id: 'demo-2',
          name: 'Claude 代码助手',
          purpose: '专业的代码生成和调试助手',
          purposes: ['stock_recommendation'],
          model: 'claude-3-sonnet',
          temperature: 0.3,
          max_tokens: 4096,
          is_active: true,
          created_at: new Date().toISOString(),
          is_demo: true
        },
        {
          id: 'demo-3',
          name: '创意写作助手',
          purpose: '专注于创意写作和内容生成',
          purposes: ['stock_review', 'stock_recommendation'],
          model: 'gpt-3.5-turbo',
          temperature: 1.2,
          max_tokens: 1024,
          is_active: false,
          created_at: new Date().toISOString(),
          is_demo: true
        }
      ]
    } else {
      apiInterfaces.value = loadedInterfaces
    }
  } catch (error) {
    console.error('加载接口配置失败:', error)
    // 网络错误时也显示示例数据
    apiInterfaces.value = [
      {
        id: 'demo-1',
        name: 'GPT-4 智能助手',
        purpose: '通用AI对话助手，适用于各种场景',
        purposes: ['stock_review', 'real_time_monitoring'],
        model: 'gpt-4',
        temperature: 0.7,
        max_tokens: 2048,
        is_active: true,
        created_at: new Date().toISOString(),
        is_demo: true
      },
      {
        id: 'demo-2',
        name: 'Claude 代码助手',
        purpose: '专业的代码生成和调试助手',
        purposes: ['stock_recommendation'],
        model: 'claude-3-sonnet',
        temperature: 0.3,
        max_tokens: 4096,
        is_active: true,
        created_at: new Date().toISOString(),
        is_demo: true
      }
    ]
  }
}

const toggleTokenStatus = async () => {
  if (!apiToken.value) return
  
  try {
    const response = await apiManagementAPI.updateToken(apiToken.value.id, {
      is_active: !apiToken.value.is_active
    })
    apiToken.value = response.data
  } catch (error) {
    console.error('切换Token状态失败:', error)
    alert('操作失败，请重试')
  }
}

const editInterface = (interfaceItem: any) => {
  editingInterface.value = interfaceItem
  showCreateModal.value = true
}

const editTemperature = (interfaceItem: any) => {
  currentInterface.value = interfaceItem
  temperatureValue.value = interfaceItem.temperature
  showTemperatureModal.value = true
}

const editMaxTokens = (interfaceItem: any) => {
  currentInterface.value = interfaceItem
  maxTokensValue.value = interfaceItem.max_tokens
  showMaxTokensModal.value = true
}

const updateInterfaceParameter = async (interfaceId: number, params: any) => {
  try {
    await apiManagementAPI.updateInterface(interfaceId, params)
    await loadInterfaces()
    alert('参数更新成功')
  } catch (error) {
    console.error('更新接口参数失败:', error)
    alert('更新失败，请重试')
  }
}

const testInterface = (interfaceItem: any) => {
  currentInterface.value = interfaceItem
  testingInterface.value = interfaceItem  // 修复：设置testingInterface用于TestModal组件
  testContent.value = ''
  testResult.value = ''
  testLoading.value = false
  showTestModal.value = true
}

const closeTestModal = () => {
  showTestModal.value = false
  currentInterface.value = null
  testingInterface.value = null  // 修复：清空testingInterface
  testContent.value = ''
  testResult.value = ''
  testLoading.value = false
}

const runInterfaceTest = async () => {
  if (!currentInterface.value || !testContent.value.trim()) {
    return
  }
  
  testLoading.value = true
  testResult.value = ''
  
  try {
    const response = await fetch('/api/aihubmix/test/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        interface_id: currentInterface.value.id,
        content: testContent.value,
        role: 'user'
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      testResult.value = data.result || '测试完成，但未返回结果'
    } else {
      testResult.value = `测试失败: ${data.error || '未知错误'}`
    }
  } catch (error: any) {
    console.error('接口测试失败:', error)
    testResult.value = `测试失败: ${error.message || '网络错误'}`
  } finally {
    testLoading.value = false
  }
}

const deleteInterface = async (interfaceItem: any) => {
  if (!confirm(`确定要删除接口配置 "${interfaceItem.name}" 吗？`)) {
    return
  }
  
  try {
    // 如果是演示数据，直接从本地数组中删除
    if (interfaceItem.is_demo) {
      const index = apiInterfaces.value.findIndex(item => item.id === interfaceItem.id)
      if (index > -1) {
        apiInterfaces.value.splice(index, 1)
      }
      alert('演示接口删除成功')
      return
    }
    
    // 删除真实的接口数据
    await apiManagementAPI.deleteInterface(interfaceItem.id)
    await loadInterfaces()
    alert('接口删除成功')
  } catch (error) {
    console.error('删除接口配置失败:', error)
    alert('删除失败，请重试')
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingInterface.value = null
}

const createInterface = () => {
  editingInterface.value = null
  showCreateModal.value = true
}

const onTokenSaved = () => {
  showTokenModal.value = false
  loadApiToken()
}

const onInterfaceSaved = () => {
  closeCreateModal()
  loadInterfaces()
}

const closeTemperatureModal = () => {
  showTemperatureModal.value = false
  currentInterface.value = null
  temperatureValue.value = 0
}

const closeMaxTokensModal = () => {
  showMaxTokensModal.value = false
  currentInterface.value = null
  maxTokensValue.value = 0
}

const saveTemperature = async () => {
  if (!currentInterface.value || temperatureValue.value < 0 || temperatureValue.value > 2) {
    return
  }
  
  try {
    await updateInterfaceParameter(currentInterface.value.id, { temperature: temperatureValue.value })
    closeTemperatureModal()
  } catch (error) {
    console.error('更新Temperature失败:', error)
    alert('更新失败，请重试')
  }
}

const saveMaxTokens = async () => {
  if (!currentInterface.value || maxTokensValue.value < 1 || maxTokensValue.value > 4096) {
    return
  }
  
  try {
    await updateInterfaceParameter(currentInterface.value.id, { max_tokens: maxTokensValue.value })
    closeMaxTokensModal()
  } catch (error) {
    console.error('更新Max Tokens失败:', error)
    alert('更新失败，请重试')
  }
}

// 工具函数
const getCsrfToken = () => {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'csrftoken') {
      return value
    }
  }
  return ''
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// Token 显示相关
const maskedToken = computed(() => {
  if (!apiToken.value?.token_preview) return ''
  if (showFullToken.value) {
    // 对于安全考虑，后端不返回完整token，只显示预览
    return apiToken.value.token_preview + ' (完整token已隐藏)'
  }
  return apiToken.value.token_preview
})

const toggleTokenVisibility = () => {
  showFullToken.value = !showFullToken.value
}
</script>

<style scoped>
.aihubmix-management {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
}

.button-section {
  margin: 24px 0;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-modern {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-modern:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #718096;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  color: #1a202c;
  background: #edf2f7;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #1a202c;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: white;
  color: #1a202c;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-text {
  margin-top: 4px;
  font-size: 12px;
  color: #718096;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary {
  background: #edf2f7;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .aihubmix-management {
    padding: 16px;
  }
  
  .button-section {
    flex-direction: column;
    align-items: center;
  }
}
</style>