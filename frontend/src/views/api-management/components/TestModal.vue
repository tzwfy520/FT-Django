<template>
  <div class="modern-modal-overlay">
    <div class="modern-modal-container">
      <div class="modern-modal-content">
        <div class="modern-modal-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="fas fa-play-circle"></i>
            </div>
            <div class="header-text">
              <h3 class="modal-title">接口测试</h3>
              <p class="modal-subtitle">测试接口: {{ apiInterface?.name }}</p>
              <div v-if="apiInterface?.purposes && apiInterface.purposes.length > 0" class="interface-purposes">
                <span class="purposes-label">接口用途:</span>
                <span class="purpose-tag" v-for="purpose in formatPurposes(apiInterface.purposes)" :key="purpose">
                  {{ purpose }}
                </span>
              </div>
            </div>
          </div>
          <button type="button" class="modern-close-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modern-modal-body">
          <div class="test-layout">
            <!-- 左侧：输入区域 -->
            <div class="input-section">
              <div class="section-title">
                <i class="fas fa-edit"></i>
                <span>测试输入</span>
              </div>
              <div class="section-content">
                <form @submit.prevent="testInterface">
                  <div class="form-group">
                    <label for="testMessage" class="form-label">
                      <strong>测试消息</strong>
                      <span class="required">*</span>
                    </label>
                    <textarea
                      id="testMessage"
                      v-model="testMessage"
                      class="form-textarea"
                      rows="6"
                      placeholder="请输入要测试的消息内容..."
                      required
                    ></textarea>
                  </div>

                  <!-- 接口参数编辑 -->
                  <div class="form-group">
                    <div class="params-header">
                      <label class="form-label">
                        <strong>接口参数</strong>
                      </label>
                      <button 
                        type="button" 
                        class="btn-save-params"
                        @click="saveParameters"
                        :disabled="savingParams"
                      >
                        <span v-if="savingParams" class="loading-spinner small"></span>
                        <i v-else class="fas fa-save"></i>
                        {{ savingParams ? '保存中...' : '保存参数' }}
                      </button>
                    </div>
                    <div class="params-edit">
                      <div class="param-item">
                        <label class="param-label">模型:</label>
                        <input 
                          v-model="editableParams.model"
                          type="text"
                          class="param-input"
                          placeholder="输入模型名称"
                        />
                      </div>
                      <div class="param-item">
                        <label class="param-label">温度:</label>
                        <input 
                          v-model.number="editableParams.temperature"
                          type="number"
                          step="0.1"
                          min="0"
                          max="2"
                          class="param-input"
                          placeholder="0.0 - 2.0"
                        />
                      </div>
                      <div class="param-item">
                        <label class="param-label">最大令牌:</label>
                        <input 
                          v-model.number="editableParams.max_tokens"
                          type="number"
                          min="1"
                          class="param-input"
                          placeholder="输入最大令牌数"
                        />
                      </div>
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    class="btn-primary full-width"
                    :disabled="testing || !testMessage.trim()"
                  >
                    <span v-if="testing" class="loading-spinner"></span>
                    <i v-else class="fas fa-paper-plane"></i>
                    {{ testing ? '测试中...' : '发送测试' }}
                  </button>
                </form>
              </div>
            </div>

            <!-- 右侧：输出区域 -->
            <div class="output-section">
              <div class="section-title">
                <div class="title-left">
                  <i class="fas fa-terminal"></i>
                  <span>测试结果</span>
                </div>
                <div v-if="testResult" class="status-badge">
                  <span 
                    class="badge"
                    :class="testResult.success ? 'success' : 'error'"
                  >
                    {{ testResult.success ? '成功' : '失败' }}
                  </span>
                </div>
              </div>
              <div class="section-content">
                <!-- 加载状态 -->
                <div v-if="testing" class="loading-state">
                  <div class="loading-spinner large"></div>
                  <p>正在调用API，请稍候...</p>
                </div>

                <!-- 无结果状态 -->
                <div v-else-if="!testResult" class="empty-state">
                  <i class="fas fa-info-circle"></i>
                  <p>点击左侧"发送测试"按钮开始测试</p>
                </div>

                <!-- 测试结果 -->
                <div v-else class="result-content">
                  <!-- 成功结果 -->
                  <div v-if="testResult.success">
                    <div class="result-group">
                      <label class="result-label">
                        <strong>AI 回复</strong>
                      </label>
                      <div class="result-box success">
                        <div class="response-content">{{ testResult.data?.choices?.[0]?.message?.content || testResult.data?.data?.choices?.[0]?.message?.content || testResult.content || '无回复内容' }}</div>
                      </div>
                    </div>

                    <!-- 使用统计 -->
                    <div class="result-group" v-if="testResult.data.usage">
                      <label class="result-label">
                        <strong>使用统计</strong>
                      </label>
                      <div class="usage-stats">
                        <div class="stat-item">
                          <span class="stat-label">输入令牌:</span>
                          <span class="stat-value">{{ testResult.data.usage.prompt_tokens }}</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-label">输出令牌:</span>
                          <span class="stat-value">{{ testResult.data.usage.completion_tokens }}</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-label">总令牌:</span>
                          <span class="stat-value">{{ testResult.data.usage.total_tokens }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 响应时间 -->
                    <div class="result-group" v-if="testResult.response_time">
                      <label class="result-label">
                        <strong>响应时间</strong>
                      </label>
                      <div class="response-time">
                        {{ testResult.response_time }}ms
                      </div>
                    </div>
                  </div>

                  <!-- 错误结果 -->
                  <div v-else>
                    <div class="result-group">
                      <label class="result-label">
                        <strong>错误信息</strong>
                      </label>
                      <div class="result-box error">
                        {{ testResult.error }}
                      </div>
                    </div>

                    <!-- 详细信息 -->
                    <div class="result-group" v-if="testResult.details">
                      <label class="result-label">
                        <strong>详细信息</strong>
                      </label>
                      <div class="details-box">
                        <pre>{{ JSON.stringify(testResult.details, null, 2) }}</pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modern-modal-footer">
          <div class="footer-actions">
            <button type="button" class="btn-secondary" @click="$emit('close')">
              <i class="fas fa-times"></i>
              关闭
            </button>
            <button 
              type="button" 
              class="btn-outline"
              @click="clearResult"
              :disabled="!testResult"
            >
              <i class="fas fa-eraser"></i>
              清空结果
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { apiManagementAPI } from '@/services/api'

// Props
const props = defineProps({
  apiInterface: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'paramsSaved'])

// 响应式数据
const testMessage = ref('')
const testResult = ref<any>(null)
const testing = ref(false)
const savingParams = ref(false)

// 可编辑的参数
const editableParams = reactive({
  model: '',
  temperature: 0,
  max_tokens: 0
})

// 监听props变化，初始化可编辑参数
watch(() => props.apiInterface, (newInterface) => {
  if (newInterface) {
    editableParams.model = newInterface.model || ''
    editableParams.temperature = newInterface.temperature ?? 0  // 修复：使用??操作符避免0值被误判
    editableParams.max_tokens = newInterface.max_tokens ?? 0     // 修复：使用??操作符避免0值被误判
  }
}, { immediate: true })

// 测试接口
const testInterface = async () => {
  if (!testMessage.value.trim()) {
    return
  }

  testing.value = true
  testResult.value = null

  try {
    const startTime = Date.now()
    const response = await apiManagementAPI.testInterface(props.apiInterface.id, {
      message: testMessage.value.trim()
    })
    const endTime = Date.now()

    testResult.value = {
      success: true,
      data: response.data,
      response_time: endTime - startTime
    }
  } catch (error: any) {
    console.error('接口测试失败:', error)
    testResult.value = {
      success: false,
      error: error.response?.data?.error || error.message || '测试失败',
      details: error.response?.data
    }
  } finally {
    testing.value = false
  }
}

// 保存参数
const saveParameters = async () => {
  savingParams.value = true
  
  try {
    await apiManagementAPI.updateInterface(props.apiInterface.id, {
      model: editableParams.model,
      temperature: editableParams.temperature,
      max_tokens: editableParams.max_tokens
    })
    
    // 发出参数保存成功事件
    emit('paramsSaved')
    alert('参数保存成功')
  } catch (error: any) {
    console.error('保存参数失败:', error)
    alert('保存参数失败，请重试')
  } finally {
    savingParams.value = false
  }
}

// 清空结果
const clearResult = () => {
  testResult.value = null
  testMessage.value = ''
}

// 格式化接口用途显示
const formatPurposes = (purposes: string[]) => {
  const purposeMap: { [key: string]: string } = {
    'stock_review': '股票复盘',
    'real_time_monitoring': '实时盯盘',
    'stock_recommendation': '股票推荐'
  }
  return purposes.map(purpose => purposeMap[purpose] || purpose)
}
</script>

<style scoped>
.modern-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 20px;
}

.modern-modal-container {
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modern-modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modern-modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
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

.interface-purposes {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.purposes-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.purpose-tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.header-text .modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-text .modal-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.modern-close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}



.modern-modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.test-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  height: 100%;
  min-height: 500px;
}

.input-section,
.output-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.input-section {
  border-right: 1px solid #e5e7eb;
}

.section-title {
  padding: 20px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #374151;
}

.section-title i {
  margin-right: 8px;
  color: #6366f1;
}

.title-left {
  display: flex;
  align-items: center;
}

.status-badge .badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge .badge.success {
  background: #dcfce7;
  color: #166534;
}

.status-badge .badge.error {
  background: #fef2f2;
  color: #dc2626;
}

.section-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
  margin-left: 4px;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
}

.params-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.btn-save-params {
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-save-params:hover:not(:disabled) {
  background: #059669;
}

.btn-save-params:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.params-edit {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.param-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.param-item:last-child {
  margin-bottom: 0;
}

.param-label {
  font-weight: 500;
  color: #4a5568;
  min-width: 80px;
  margin-right: 12px;
}

.param-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.param-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.loading-spinner.small {
  width: 12px;
  height: 12px;
  border-width: 2px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.full-width {
  width: 100%;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.large {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #6b7280;
}

.empty-state i {
  font-size: 32px;
  margin-bottom: 12px;
  color: #9ca3af;
}

.result-content {
  height: 100%;
}

.result-group {
  margin-bottom: 20px;
}

.result-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.result-box {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.result-box.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.result-box.error {
  background: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}

.response-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-weight: 600;
  color: #374151;
  font-size: 16px;
}

.response-time {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  color: #0369a1;
}

.details-box {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
}

.details-box pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
  color: #374151;
}

.modern-modal-footer {
  padding: 20px 32px;
  border-top: 1px solid #e5e7eb;
  background: #f8fafc;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary,
.btn-outline {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}



.btn-outline {
  background: transparent;
  color: #6366f1;
  border: 1px solid #6366f1;
}



.btn-outline:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>