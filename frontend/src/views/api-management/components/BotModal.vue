<template>
  <div class="modal fade show" style="display: block;" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-robot me-2"></i>
            {{ bot ? '编辑Bot配置' : '新增Bot配置' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="botName" class="form-label">Bot名称 <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="botName"
                    v-model="formData.name"
                    placeholder="请输入Bot名称"
                    required
                  >
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="botId" class="form-label">Bot ID <span class="text-danger">*</span></label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="botId"
                    v-model="formData.bot_id"
                    placeholder="请输入Coze Bot ID"
                    required
                  >
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="botDescription" class="form-label">Bot描述</label>
              <textarea 
                class="form-control" 
                id="botDescription"
                v-model="formData.description"
                rows="3"
                placeholder="请输入Bot功能描述"
              ></textarea>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="botModel" class="form-label">使用模型</label>
                  <select class="form-select" id="botModel" v-model="formData.model">
                    <option value="">请选择模型</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gemini-pro">Gemini Pro</option>
                  </select>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="botVersion" class="form-label">Bot版本</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="botVersion"
                    v-model="formData.version"
                    placeholder="如：v1.0.0"
                  >
                </div>
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="maxTokens" class="form-label">最大Token数</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="maxTokens"
                    v-model.number="formData.max_tokens"
                    placeholder="如：4000"
                    min="1"
                    max="32000"
                  >
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="temperature" class="form-label">温度参数</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="temperature"
                    v-model.number="formData.temperature"
                    placeholder="0.0 - 1.0"
                    min="0"
                    max="1"
                    step="0.1"
                  >
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="systemPrompt" class="form-label">系统提示词</label>
              <textarea 
                class="form-control" 
                id="systemPrompt"
                v-model="formData.system_prompt"
                rows="4"
                placeholder="请输入系统提示词，用于定义Bot的行为和角色"
              ></textarea>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="isActive"
                      v-model="formData.is_active"
                    >
                    <label class="form-check-label" for="isActive">
                      启用此Bot
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="mb-3">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      id="enableStream"
                      v-model="formData.enable_stream"
                    >
                    <label class="form-check-label" for="enableStream">
                      启用流式输出
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 测试区域 -->
            <div class="card mt-4">
              <div class="card-header">
                <h6 class="mb-0">
                  <i class="fas fa-vial me-2"></i>
                  Bot测试
                </h6>
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label for="testMessage" class="form-label">测试消息</label>
                  <textarea 
                    class="form-control" 
                    id="testMessage"
                    v-model="testMessage"
                    rows="2"
                    placeholder="输入测试消息，点击测试按钮验证Bot配置"
                  ></textarea>
                </div>
                <button 
                  type="button" 
                  class="btn btn-outline-primary btn-sm"
                  @click="testBot"
                  :disabled="!formData.bot_id || testing"
                >
                  <span v-if="testing" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="fas fa-play me-1"></i>
                  {{ testing ? '测试中...' : '测试Bot' }}
                </button>
                
                <div v-if="testResult" class="mt-3">
                  <div class="alert" :class="testResult.success ? 'alert-success' : 'alert-danger'">
                    <strong>{{ testResult.success ? '测试成功' : '测试失败' }}:</strong>
                    {{ testResult.message }}
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            取消
          </button>
          <button 
            type="button" 
            class="btn btn-primary"
            @click="handleSubmit"
            :disabled="!isFormValid || saving"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show"></div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps<{
  show: boolean
  bot?: any
}>()

// Emits
const emit = defineEmits<{
  close: []
  save: [botData: any]
}>()

// 响应式数据
const saving = ref(false)
const testing = ref(false)
const testMessage = ref('你好，请介绍一下自己')
const testResult = ref<any>(null)

const formData = ref({
  name: '',
  bot_id: '',
  description: '',
  model: '',
  version: '',
  max_tokens: 4000,
  temperature: 0.7,
  system_prompt: '',
  is_active: true,
  enable_stream: false
})

// 计算属性
const isFormValid = computed(() => {
  return formData.value.name.trim() && formData.value.bot_id.trim()
})

// 监听器
watch(() => props.bot, (newBot) => {
  if (newBot) {
    formData.value = { ...newBot }
  } else {
    resetForm()
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  if (props.bot) {
    formData.value = { ...props.bot }
  }
})

// 方法
const resetForm = () => {
  formData.value = {
    name: '',
    bot_id: '',
    description: '',
    model: '',
    version: '',
    max_tokens: 4000,
    temperature: 0.7,
    system_prompt: '',
    is_active: true,
    enable_stream: false
  }
  testResult.value = null
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    ElMessage.warning('请填写必填字段')
    return
  }
  
  try {
    saving.value = true
    emit('save', { ...formData.value })
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const testBot = async () => {
  if (!testMessage.value.trim()) {
    ElMessage.warning('请输入测试消息')
    return
  }
  
  try {
    testing.value = true
    testResult.value = null
    
    // TODO: 调用实际的Bot测试API
    // const response = await cozeAPI.testBot({
    //   bot_id: formData.value.bot_id,
    //   message: testMessage.value,
    //   ...formData.value
    // })
    
    // 模拟测试结果
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const success = Math.random() > 0.3 // 70% 成功率
    testResult.value = {
      success,
      message: success 
        ? `Bot响应: 你好！我是${formData.value.name}，很高兴为您服务。` 
        : 'Bot配置有误，请检查Bot ID和相关参数设置。'
    }
  } catch (error) {
    testResult.value = {
      success: false,
      message: '测试请求失败，请检查网络连接和配置。'
    }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.modal {
  z-index: 1050;
}

.modal-backdrop {
  z-index: 1040;
}

.modal-dialog {
  margin: 1.75rem auto;
}

.modal-content {
  border: none;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  border-bottom: none;
}

.modal-title {
  font-weight: 600;
}

.btn-close {
  filter: invert(1);
}

.form-label {
  font-weight: 500;
  color: #2c3e50;
}

.form-control, .form-select {
  border-radius: 6px;
  border: 1px solid #e1e5e9;
}

.form-control:focus, .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.card {
  border: 1px solid #e1e5e9;
  border-radius: 8px;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e1e5e9;
}

.btn {
  border-radius: 6px;
  font-weight: 500;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.text-danger {
  color: #dc3545 !important;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.alert {
  border-radius: 6px;
  border: none;
}

.form-check-input:checked {
  background-color: #667eea;
  border-color: #667eea;
}
</style>