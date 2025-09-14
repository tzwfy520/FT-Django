<template>
  <div class="modern-modal-overlay">
    <div class="modern-modal-container">
      <div class="modern-modal-content">
        <div class="modern-modal-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="fas fa-key"></i>
            </div>
            <div class="header-text">
              <h3 class="modal-title">{{ token ? '编辑' : '设置' }} API Token</h3>
              <p class="modal-subtitle">配置推理时代接口访问凭证</p>
            </div>
          </div>
          <button type="button" class="modern-close-btn" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modern-modal-body">
          <form @submit.prevent="saveToken" class="modern-form">
            <div class="form-group">
              <label for="tokenInput" class="modern-label">
                <i class="fas fa-key label-icon"></i>
                推理时代 API Token
                <span class="required-mark">*</span>
              </label>
              <div class="modern-input-group">
                <input
                  id="tokenInput"
                  v-model="form.token"
                  :type="showToken ? 'text' : 'password'"
                  class="modern-input"
                  placeholder="请输入您的推理时代API Token"
                  required
                />
                <button 
                  type="button" 
                  class="input-action-btn"
                  @click="showToken = !showToken"
                >
                  <i :class="showToken ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div class="input-help">
                <i class="fas fa-info-circle"></i>
                请从 <a href="https://aihubmix.com" target="_blank" class="help-link">推理时代官网</a> 获取您的API Token
              </div>
            </div>

            <div class="form-group">
              <label for="baseUrl" class="modern-label">
                <i class="fas fa-link label-icon"></i>
                API 基础地址
              </label>
              <input
                id="baseUrl"
                v-model="form.base_url"
                type="url"
                class="modern-input"
                placeholder="https://aihubmix.com/v1"
              />
              <div class="input-help">
                <i class="fas fa-info-circle"></i>
                默认为推理时代官方API地址，通常无需修改
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
                    <i class="fas fa-toggle-on label-icon"></i>
                    启用此Token
                  </span>
                </label>
              </div>
              <div class="input-help">
                <i class="fas fa-info-circle"></i>
                只有启用的Token才能用于API调用
              </div>
            </div>

            <div class="info-card">
              <div class="info-header">
                <i class="fas fa-lightbulb"></i>
                <span>使用说明</span>
              </div>
              <ul class="info-list">
                <li><i class="fas fa-shield-alt"></i>API Token用于验证您对推理时代服务的访问权限</li>
                <li><i class="fas fa-lock"></i>请妥善保管您的Token，不要泄露给他人</li>
                <li><i class="fas fa-sync-alt"></i>如果Token泄露，请及时到官网重新生成</li>
                <li><i class="fas fa-eye-slash"></i>Token设置后将加密存储，页面显示时会隐藏部分字符</li>
              </ul>
            </div>
          </form>
        </div>
        
        <div class="modern-modal-footer">
          <button type="button" class="modern-btn modern-btn-secondary" @click="$emit('close')">
            <i class="fas fa-times"></i>
            <span>取消</span>
          </button>
          <button 
            type="button" 
            class="modern-btn modern-btn-primary"
            @click="saveToken"
            :disabled="saving || !form.token.trim()"
          >
            <div v-if="saving" class="btn-loading">
              <div class="loading-spinner"></div>
              <span>保存中...</span>
            </div>
            <div v-else class="btn-content">
              <i class="fas fa-save"></i>
              <span>保存</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { apiManagementAPI } from '@/services/api'

// Props
const props = defineProps({
  token: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'saved'])

// 响应式数据
const saving = ref(false)
const showToken = ref(false)
const form = reactive({
  token: '',
  base_url: 'https://aihubmix.com/v1',
  is_active: true
})

// 生命周期
onMounted(() => {
  if (props.token) {
    form.token = props.token.token || ''
    form.base_url = props.token.base_url || 'https://aihubmix.com/v1'
    form.is_active = props.token.is_active ?? true
  }
})

// 方法
const saveToken = async () => {
  if (!form.token.trim()) {
    alert('请输入API Token')
    return
  }

  saving.value = true
  
  try {
    const data = {
      provider: 1, // 推理时代的provider_id
      token: form.token.trim(),
      base_url: form.base_url.trim() || 'https://aihubmix.com/v1',
      is_active: form.is_active
    }

    if (props.token) {
      // 更新现有token
      await apiManagementAPI.updateToken(props.token.id, data)
    } else {
      // 创建新token
      await apiManagementAPI.createToken(data)
    }

    emit('saved')
  } catch (error: any) {
    console.error('保存Token失败:', error)
    
    let errorMessage = '保存失败，请重试'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.response?.data?.token) {
      errorMessage = error.response.data.token[0]
    }
    
    alert(errorMessage)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* 现代化模态框样式 */
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
  width: 100%;
  max-width: 600px;
  margin: 20px;
  animation: slideUp 0.3s ease-out;
}

.modern-modal-content {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 模态框头部 */
.modern-modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.header-text .modal-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.header-text .modal-subtitle {
  margin: 5px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

.modern-close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modern-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* 模态框主体 */
.modern-modal-body {
  padding: 40px;
}

.modern-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modern-label {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

.label-icon {
  color: #667eea;
  font-size: 14px;
}

.required-mark {
  color: #e53e3e;
  font-weight: 700;
}

.modern-input-group {
  position: relative;
  display: flex;
}

.modern-input {
  flex: 1;
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.modern-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-action-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: #f1f5f9;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-action-btn:hover {
  background: #e2e8f0;
  color: #475569;
}

.input-help {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.help-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.help-link:hover {
  color: #5a67d8;
  text-decoration: underline;
}

/* 现代化复选框 */
.modern-checkbox-group {
  display: flex;
  align-items: center;
}

.modern-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #2d3748;
}

.checkbox-input {
  display: none;
}

.checkbox-mark {
  width: 24px;
  height: 24px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  position: relative;
  transition: all 0.3s ease;
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
  font-size: 14px;
  font-weight: bold;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 信息卡片 */
.info-card {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 16px;
  padding: 24px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #0369a1;
  margin-bottom: 16px;
}

.info-header i {
  font-size: 18px;
}

.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-list li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  font-size: 14px;
  color: #0369a1;
  line-height: 1.5;
}

.info-list li i {
  margin-top: 2px;
  font-size: 12px;
  opacity: 0.8;
}

/* 模态框底部 */
.modern-modal-footer {
  background: #f8fafc;
  padding: 30px 40px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  border-top: 1px solid #e2e8f0;
}

.modern-btn {
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.modern-btn-secondary {
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e2e8f0;
}

.modern-btn-secondary:hover {
  background: #e2e8f0;
  color: #475569;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.modern-btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.modern-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.modern-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-loading,
.btn-content {
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

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-modal-container {
    margin: 10px;
  }
  
  .modern-modal-header {
    padding: 20px;
  }
  
  .header-content {
    gap: 15px;
  }
  
  .header-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .header-text .modal-title {
    font-size: 20px;
  }
  
  .modern-modal-body {
    padding: 30px 20px;
  }
  
  .modern-modal-footer {
    padding: 20px;
    flex-direction: column;
  }
  
  .modern-btn {
    width: 100%;
  }
}
</style>