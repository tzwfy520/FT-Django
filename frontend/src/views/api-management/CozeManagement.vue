<template>
  <div class="coze-management">
    <div class="page-header">
      <h2>Coze接口管理</h2>
      <div class="header-actions">
        <el-button @click="loadBots" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- API Token配置 -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-key me-2"></i>
          API Token配置
        </h5>
        <button 
          class="btn btn-primary btn-sm"
          @click="showTokenModal = true"
        >
          <i class="fas fa-edit me-1"></i>
          {{ apiToken ? '更新Token' : '设置Token' }}
        </button>
      </div>
      <div class="card-body">
        <div v-if="apiToken" class="d-flex align-items-center">
          <div class="flex-grow-1">
            <div class="d-flex align-items-center">
              <strong class="me-3">Token状态:</strong>
              <span class="badge" :class="apiToken.is_active ? 'bg-success' : 'bg-danger'">
                {{ apiToken.is_active ? '已激活' : '未激活' }}
              </span>
              <button 
                class="btn btn-sm ms-2"
                :class="apiToken.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                @click="toggleTokenStatus"
                :disabled="loading"
              >
                {{ apiToken.is_active ? '停用' : '启用' }}
              </button>
            </div>
          </div>
          <small class="text-muted d-block mt-2">
            创建时间: {{ formatDate(apiToken.created_at) }}
          </small>
        </div>
        <div v-else class="text-center text-muted">
          <i class="fas fa-info-circle me-2"></i>
          尚未设置API Token，请点击上方按钮进行设置
        </div>
      </div>
    </div>

    <!-- Bot配置列表 -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-robot me-2"></i>
          Bot配置管理
        </h5>
        <button 
          class="btn btn-success btn-sm"
          @click="showBotModal = true"
          :disabled="!apiToken || !apiToken.is_active"
        >
          <i class="fas fa-plus me-1"></i>
          新增Bot
        </button>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="bots.length === 0" class="text-center text-muted">
          <i class="fas fa-robot fa-3x mb-3"></i>
          <p>暂无Bot配置</p>
          <button 
            class="btn btn-primary"
            @click="showBotModal = true"
            :disabled="!apiToken || !apiToken.is_active"
          >
            <i class="fas fa-plus me-1"></i>
            创建第一个Bot
          </button>
        </div>

        <div v-else class="row">
          <div v-for="bot in bots" :key="bot.id" class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ bot.name }}</h6>
                  <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                            type="button" 
                            :id="'dropdown-' + bot.id" 
                            data-bs-toggle="dropdown">
                      操作
                    </button>
                    <ul class="dropdown-menu" :aria-labelledby="'dropdown-' + bot.id">
                      <li><a class="dropdown-item" href="#" @click="editBot(bot)">编辑</a></li>
                      <li><a class="dropdown-item" href="#" @click="testBot(bot)">测试</a></li>
                      <li><hr class="dropdown-divider"></li>
                      <li><a class="dropdown-item text-danger" href="#" @click="deleteBot(bot)">删除</a></li>
                    </ul>
                  </div>
                </div>
                <p class="card-text text-muted small">{{ bot.description || '暂无描述' }}</p>
                <div class="mb-2">
                  <small class="text-muted">Bot ID:</small>
                  <code class="ms-1">{{ bot.bot_id }}</code>
                </div>
                <div class="mb-2">
                  <small class="text-muted">状态:</small>
                  <span class="badge ms-1" :class="bot.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ bot.is_active ? '启用' : '禁用' }}
                  </span>
                </div>
                <small class="text-muted">创建时间: {{ formatDate(bot.created_at) }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Token设置模态框 -->
    <TokenModal 
      v-if="showTokenModal"
      :show="showTokenModal"
      :token="apiToken"
      @close="showTokenModal = false"
      @save="handleTokenSave"
      title="Coze API Token配置"
      placeholder="请输入Coze API Token"
    />

    <!-- Bot配置模态框 -->
    <BotModal 
      v-if="showBotModal"
      :show="showBotModal"
      :bot="selectedBot"
      @close="closeBotModal"
      @save="handleBotSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import TokenModal from './components/TokenModal.vue'
import BotModal from './components/BotModal.vue'

// 响应式数据
const loading = ref(false)
const apiToken = ref<any>(null)
const bots = ref<any[]>([])
const showTokenModal = ref(false)
const showBotModal = ref(false)
const selectedBot = ref<any>(null)

// 生命周期
onMounted(() => {
  loadApiToken()
  loadBots()
})

// 方法
const loadApiToken = async () => {
  try {
    loading.value = true
    // TODO: 调用API获取Coze Token
    // const response = await cozeAPI.getToken()
    // apiToken.value = response.data
    
    // 模拟数据
    apiToken.value = {
      id: 1,
      token: 'coze_****************************',
      is_active: true,
      created_at: new Date().toISOString()
    }
  } catch (error) {
    console.error('获取API Token失败:', error)
  } finally {
    loading.value = false
  }
}

const loadBots = async () => {
  try {
    loading.value = true
    // TODO: 调用API获取Bot列表
    // const response = await cozeAPI.getBots()
    // bots.value = response.data
    
    // 模拟数据
    bots.value = [
      {
        id: 1,
        name: '智能客服助手',
        description: '专业的客服问答机器人',
        bot_id: 'bot_123456789',
        is_active: true,
        created_at: new Date().toISOString()
      },
      {
        id: 2,
        name: '代码助手',
        description: '帮助编写和优化代码',
        bot_id: 'bot_987654321',
        is_active: false,
        created_at: new Date().toISOString()
      }
    ]
  } catch (error) {
    console.error('获取Bot列表失败:', error)
  } finally {
    loading.value = false
  }
}

const toggleTokenStatus = async () => {
  try {
    loading.value = true
    // TODO: 调用API切换Token状态
    apiToken.value.is_active = !apiToken.value.is_active
    ElMessage.success(`Token已${apiToken.value.is_active ? '启用' : '停用'}`)
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

const handleTokenSave = async (tokenData: any) => {
  try {
    loading.value = true
    // TODO: 调用API保存Token
    apiToken.value = { ...tokenData, created_at: new Date().toISOString() }
    showTokenModal.value = false
    ElMessage.success('Token保存成功')
  } catch (error) {
    ElMessage.error('Token保存失败')
  } finally {
    loading.value = false
  }
}

const editBot = (bot: any) => {
  selectedBot.value = { ...bot }
  showBotModal.value = true
}

const testBot = async (bot: any) => {
  try {
    // TODO: 调用API测试Bot
    ElMessage.success(`Bot "${bot.name}" 测试成功`)
  } catch (error) {
    ElMessage.error('Bot测试失败')
  }
}

const deleteBot = async (bot: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Bot "${bot.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除Bot
    bots.value = bots.value.filter(b => b.id !== bot.id)
    ElMessage.success('Bot删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Bot删除失败')
    }
  }
}

const closeBotModal = () => {
  showBotModal.value = false
  selectedBot.value = null
}

const handleBotSave = async (botData: any) => {
  try {
    loading.value = true
    
    if (selectedBot.value) {
      // 更新Bot
      const index = bots.value.findIndex(b => b.id === selectedBot.value.id)
      if (index !== -1) {
        bots.value[index] = { ...botData, id: selectedBot.value.id }
      }
      ElMessage.success('Bot更新成功')
    } else {
      // 新增Bot
      const newBot = {
        ...botData,
        id: Date.now(),
        created_at: new Date().toISOString()
      }
      bots.value.push(newBot)
      ElMessage.success('Bot创建成功')
    }
    
    closeBotModal()
  } catch (error) {
    ElMessage.error('Bot保存失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.coze-management {
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

.card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0 !important;
}

.card-header h5 {
  margin: 0;
}

.btn {
  border-radius: 6px;
}

.badge {
  font-size: 0.75em;
}

code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
}

.dropdown-toggle::after {
  margin-left: 0.5em;
}

.card-title {
  color: #2c3e50;
  font-weight: 600;
}

.text-muted {
  color: #6c757d !important;
}

.h-100 {
  height: 100% !important;
}
</style>