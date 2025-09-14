<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>股票分析系统</h2>
        <p>请登录您的账户</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="loginForm.username"
            type="text"
            class="form-control"
            placeholder="请输入用户名"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            class="form-control"
            placeholder="请输入密码"
            required
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button
          type="submit"
          class="btn btn-primary btn-block"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <div class="login-footer">
        <p>默认账户: admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/services/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const errorMessage = ref('')
    
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    const handleLogin = async () => {
      loading.value = true
      errorMessage.value = ''
      
      try {
        const response = await apiClient.post('/api-management/auth/login/', {
          username: loginForm.value.username,
          password: loginForm.value.password
        })
        
        if (response.data.success) {
          // 存储用户信息
          localStorage.setItem('userInfo', JSON.stringify(response.data.user))
          localStorage.setItem('isAuthenticated', 'true')
          
          // 跳转到主页面
          router.push('/')
        }
      } catch (error) {
        if (error.response?.data?.error) {
          errorMessage.value = error.response.data.error
        } else {
          errorMessage.value = '登录失败，请稍后重试'
        }
      } finally {
        loading.value = false
      }
    }
    
    return {
      loginForm,
      loading,
      errorMessage,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #333;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
  border: 1px solid #fcc;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}
</style>