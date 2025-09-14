<template>
  <div class="modern-modal-overlay">
    <div class="modern-modal-container">
      <div class="modern-modal-content">
        <div class="modern-modal-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="fas fa-cog"></i>
            </div>
            <div class="header-text">
              <h3 class="modal-title">{{ apiInterface ? '编辑' : '新增' }}接口配置</h3>
              <p class="modal-subtitle">配置推理时代API接口参数</p>
            </div>
          </div>
          <button type="button" class="modern-close-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modern-modal-body">
          <div class="form-layout">
            <!-- 左侧表单 -->
            <div class="form-section">
              <div class="section-title">
                <i class="fas fa-edit"></i>
                <span>基础配置</span>
              </div>
              <form @submit.prevent="saveInterface" class="modern-form">
                <div class="form-group">
                  <label for="interfaceName" class="modern-label">
                    <i class="fas fa-tag label-icon"></i>
                    接口名称
                    <span class="required-mark">*</span>
                  </label>
                  <input
                    id="interfaceName"
                    v-model="form.name"
                    type="text"
                    class="modern-input"
                    placeholder="请输入接口名称，如：GPT-3.5 Turbo"
                    required
                  />
                </div>
              
                <div class="form-group">
                  <label for="model" class="modern-label">
                    <i class="fas fa-brain label-icon"></i>
                    模型名称
                    <span class="required-mark">*</span>
                  </label>
                  <input
                    id="model"
                    v-model="form.model"
                    type="text"
                    class="modern-input"
                    placeholder="请输入模型名称，如：gpt-3.5-turbo、claude-3-sonnet等"
                    required
                  />
                  <div class="model-suggestions">
                    <small class="text-muted">
                      常用模型：gpt-3.5-turbo、gpt-4、claude-3-sonnet、gemini-pro
                    </small>
                  </div>
                </div>

                <div class="form-group">
                  <label for="temperature" class="modern-label">
                    <i class="fas fa-thermometer-half label-icon"></i>
                    Temperature (0-2)
                  </label>
                  <div class="range-input-group">
                    <input
                      id="temperature"
                      v-model.number="form.temperature"
                      type="range"
                      class="modern-range"
                      min="0"
                      max="2"
                      step="0.1"
                    />
                    <input
                      v-model.number="form.temperature"
                      type="number"
                      class="range-value-input"
                      min="0"
                      max="2"
                      step="0.1"
                      placeholder="0.8"
                    />
                  </div>
                  <div class="input-help">
                    <i class="fas fa-info-circle"></i>
                    控制输出的随机性，0表示确定性输出，2表示最大随机性
                  </div>
                </div>
              
                <div class="form-group">
                  <label for="maxTokens" class="modern-label">
                    <i class="fas fa-coins label-icon"></i>
                    最大令牌数
                  </label>
                  <input
                    id="maxTokens"
                    v-model.number="form.max_tokens"
                    type="number"
                    class="modern-input"
                    min="1"
                    max="4096"
                    placeholder="1024"
                  />
                  <div class="input-help">
                    <i class="fas fa-info-circle"></i>
                    限制生成文本的最大长度，建议值：1024-2048
                  </div>
                </div>

                <div class="form-group">
                  <label for="description" class="modern-label">
                    <i class="fas fa-align-left label-icon"></i>
                    描述
                  </label>
                  <textarea
                    id="description"
                    v-model="form.description"
                    class="modern-textarea"
                    rows="4"
                    placeholder="请输入接口描述，如：用于日常对话的GPT-3.5模型配置"
                  ></textarea>
                </div>

                <div class="form-group">
                  <label class="modern-label">
                    <i class="fas fa-tags label-icon"></i>
                    接口用途
                  </label>
                  <div class="purpose-checkbox-group">
                    <label class="purpose-checkbox">
                      <input
                        v-model="form.purposes"
                        type="checkbox"
                        value="stock_review"
                        class="checkbox-input"
                      />
                      <span class="checkbox-mark"></span>
                      <span class="checkbox-label">股票复盘</span>
                    </label>
                    <label class="purpose-checkbox">
                      <input
                        v-model="form.purposes"
                        type="checkbox"
                        value="real_time_monitoring"
                        class="checkbox-input"
                      />
                      <span class="checkbox-mark"></span>
                      <span class="checkbox-label">实时盯盘</span>
                    </label>
                    <label class="purpose-checkbox">
                      <input
                        v-model="form.purposes"
                        type="checkbox"
                        value="stock_recommendation"
                        class="checkbox-input"
                      />
                      <span class="checkbox-mark"></span>
                      <span class="checkbox-label">股票推荐</span>
                    </label>
                  </div>
                </div>

                <div class="form-group">
                  <div class="modern-checkbox-group">
                    <label class="modern-checkbox">
                      <input
                        id="isActive"
                        v-model="form.is_active"
                        type="checkbox"
                        class="checkbox-input"
                      />
                      <span class="checkbox-mark"></span>
                      <span class="checkbox-label">
                        <i class="fas fa-power-off label-icon"></i>
                        启用此接口配置
                      </span>
                    </label>
                  </div>
                </div>

              </form>
            </div>
            
            <!-- 右侧预览区域 -->
            <div class="preview-section">
              <div class="section-title">
                <i class="fas fa-code"></i>
                <span>调用预览</span>
              </div>
              <div class="preview-card">
                <div class="preview-header">
                  <div class="preview-tabs">
                    <button class="preview-tab active">
                      <i class="fab fa-python"></i>
                      Python
                    </button>
                  </div>
                </div>
                <div class="preview-content">
                  <pre class="code-preview"><code>{{ previewCode }}</code></pre>
                </div>
              </div>
              
              <div class="api-info-card">
                <div class="info-header">
                  <i class="fas fa-info-circle"></i>
                  <span>API 信息</span>
                </div>
                <div class="info-content">
                  <div class="info-item">
                    <span class="info-label">Base URL:</span>
                    <span class="info-value">https://aihubmix.com/v1</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Model:</span>
                    <span class="info-value">{{ form.model || '未选择' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Temperature:</span>
                    <span class="info-value">{{ form.temperature || 0.8 }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Max Tokens:</span>
                    <span class="info-value">{{ form.max_tokens || 1024 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modern-modal-footer">
          <button type="button" class="modern-btn modern-btn-secondary" @click="$emit('close')">
            <i class="fas fa-times"></i>
            <span>取消</span>
          </button>
          <button 
            type="button" 
            class="modern-btn modern-btn-primary"
            @click="saveInterface"
            :disabled="saving || !form.name.trim() || !form.model"
          >
            <div v-if="saving" class="btn-loading">
              <div class="loading-spinner"></div>
              <span>保存中...</span>
            </div>
            <div v-else class="btn-content">
              <i class="fas fa-save"></i>
              <span>保存配置</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { apiManagementAPI } from '@/services/api'

// Props
const props = defineProps({
  apiInterface: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'saved'])

// 响应式数据
const saving = ref(false)
const form = reactive({
  name: '',
  model: '',
  temperature: 0.8,
  max_tokens: 1024,
  description: '',
  is_active: true,
  purposes: [] as string[]
})

// 可用模型列表
const availableModels = ref([
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'gpt-3.5-turbo-16k', label: 'GPT-3.5 Turbo 16K' },
  { value: 'gpt-4', label: 'GPT-4' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
  { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
  { value: 'claude-3-opus', label: 'Claude 3 Opus' },
  { value: 'claude-3-5-sonnet', label: 'Claude 3.5 Sonnet' },
  { value: 'gemini-pro', label: 'Gemini Pro' },
  { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
  { value: 'llama-3-8b', label: 'Llama 3 8B' },
  { value: 'llama-3-70b', label: 'Llama 3 70B' },
  { value: 'qwen-turbo', label: 'Qwen Turbo' },
  { value: 'qwen-plus', label: 'Qwen Plus' },
  { value: 'qwen-max', label: 'Qwen Max' }
])

// 生命周期
onMounted(() => {
  if (props.apiInterface) {
    form.name = props.apiInterface.name || ''
    form.model = props.apiInterface.model || ''
    form.temperature = props.apiInterface.temperature ?? 0.8
    form.max_tokens = props.apiInterface.max_tokens || 1024
    form.description = props.apiInterface.description || ''
    form.is_active = props.apiInterface.is_active ?? true
    form.purposes = props.apiInterface.purposes || []
  }
})

// 计算属性
const previewCode = computed(() => {
  const baseCode = `from openai import OpenAI

client = OpenAI(
    base_url="https://aihubmix.com/v1",
    api_key="AIHUBMIX_API_KEY"
)

completion = client.chat.completions.create(
    model="${form.model || 'gpt-3.5-turbo'}",
    messages=[{"role": "user", "content": "你好"}]`
  
  let additionalParams = ''
  if (form.temperature !== null && form.temperature !== 0.8) {
    additionalParams += `,\n    temperature=${form.temperature}`
  }
  if (form.max_tokens && form.max_tokens !== 1024) {
    additionalParams += `,\n    max_tokens=${form.max_tokens}`
  }
  
  return baseCode + additionalParams + `\n)\n\nprint(completion.choices[0].message)`
})

// 方法
const saveInterface = async () => {
  if (!form.name.trim()) {
    alert('请输入接口名称')
    return
  }
  
  if (!form.model) {
    alert('请选择模型')
    return
  }

  saving.value = true
  
  try {
    const data = {
      provider: '1', // 推理时代的provider_id
      name: form.name.trim(),
      model: form.model,
      temperature: form.temperature,
      max_tokens: form.max_tokens,
      description: form.description.trim(),
      is_active: form.is_active,
      purposes: form.purposes
    }

    if (props.apiInterface) {
      // 更新现有接口
      await apiManagementAPI.updateInterface(props.apiInterface.id, data)
    } else {
      // 创建新接口
      await apiManagementAPI.createInterface(data)
    }

    emit('saved')
  } catch (error: any) {
    console.error('保存接口配置失败:', error)
    
    let errorMessage = '保存失败，请重试'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.response?.data?.name) {
      errorMessage = error.response.data.name[0]
    }
    
    alert(errorMessage)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 模态框基础样式 */
.modern-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  animation: fadeIn 0.3s ease-out;
}

.modern-modal-container {
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  display: flex;
  flex-direction: column;
}

.modern-modal-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* 头部样式 */
.modern-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
  position: relative;
  z-index: 5;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.header-text h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-text p {
  margin: 4px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
}

.modern-close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
  position: relative;
}

.modern-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* 主体内容样式 */
.modern-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  min-height: 0;
}

.form-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  height: 100%;
}

.form-section, .preview-section {
  display: flex;
  flex-direction: column;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.section-title i {
  color: #667eea;
}

/* 表单样式 */
.modern-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modern-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #2d3748;
  font-size: 14px;
}

.label-icon {
  color: #667eea;
  font-size: 12px;
}

.required-mark {
  color: #e53e3e;
}

.modern-input, .modern-textarea {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
}

.modern-input:focus, .modern-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modern-select-wrapper {
  position: relative;
}

.modern-select {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s;
}

.modern-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
  pointer-events: none;
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modern-range {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  appearance: none;
}

.modern-range::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #667eea;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.model-suggestions {
  margin-top: 4px;
}

.model-suggestions .text-muted {
  color: #718096;
  font-size: 12px;
}

.purpose-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.purpose-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.purpose-checkbox:hover {
  background: #f7fafc;
}

.purpose-checkbox .checkbox-input {
  margin: 0;
}

.purpose-checkbox .checkbox-mark {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
}

.purpose-checkbox .checkbox-input:checked + .checkbox-mark {
  background: #667eea;
  border-color: #667eea;
}

.purpose-checkbox .checkbox-input:checked + .checkbox-mark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.purpose-checkbox .checkbox-label {
  font-size: 14px;
  color: #2d3748;
  font-weight: 500;
}

.range-value-input {
  width: 80px;
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
}

.input-help {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
}

.input-help i {
  color: #a0aec0;
}

.modern-checkbox-group {
  margin-top: 8px;
}

.modern-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.modern-checkbox:hover {
  background: #f7fafc;
}

.checkbox-input {
  display: none;
}

.checkbox-mark {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
}

.checkbox-input:checked + .checkbox-mark {
  background: #667eea;
  border-color: #667eea;
}

.checkbox-input:checked + .checkbox-mark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #2d3748;
}

/* 预览区域样式 */
.preview-card, .api-info-card {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.preview-header {
  background: #f7fafc;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.preview-tabs {
  display: flex;
  gap: 8px;
}

.preview-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.preview-tab.active {
  background: #667eea;
  color: white;
}

.preview-content {
  padding: 20px;
}

.code-preview {
  background: #1a202c;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 0;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  color: #2d3748;
}

.info-content {
  padding: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: #4a5568;
}

.info-value {
  font-family: 'Monaco', 'Consolas', monospace;
  color: #2d3748;
  background: #f7fafc;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
}

/* 底部按钮样式 */
.modern-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 24px 32px;
  background: #f7fafc;
  border-top: 1px solid #e2e8f0;
}

.modern-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  justify-content: center;
}

.modern-btn-secondary {
  background: white;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.modern-btn-secondary:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.modern-btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modern-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.modern-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-loading, .btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-layout {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .modern-modal-container {
    width: 95%;
    margin: 20px;
  }
  
  .modern-modal-header {
    padding: 20px;
  }
  
  .modern-modal-body {
    padding: 20px;
  }
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>