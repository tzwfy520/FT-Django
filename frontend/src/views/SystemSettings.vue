<template>
  <div class="system-settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>系统设置</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="saveAllSettings" :disabled="saving">
          <i class="icon-save"></i>
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
        <button class="btn btn-secondary" @click="refreshSettings">
          <i class="icon-refresh"></i>
          刷新
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <Loading v-if="loading" message="正在加载系统设置..." />
    
    <!-- 错误提示 -->
    <ErrorMessage 
      v-if="error" 
      :message="error" 
      type="error"
      :actions="[{ label: '重试', handler: refreshSettings }, { label: '清除', handler: clearError }]"
    />

    <div class="settings-container">
      <div class="settings-sidebar">
        <nav class="settings-nav">
          <button 
            v-for="section in sections" 
            :key="section.key"
            :class="['nav-item', { active: activeSection === section.key }]"
            @click="activeSection = section.key"
          >
            <span class="nav-icon">{{ section.icon }}</span>
            <span class="nav-label">{{ section.label }}</span>
          </button>
        </nav>
      </div>

      <div class="settings-content">
        <!-- 数据源配置 -->
        <div v-if="activeSection === 'datasource'" class="settings-section">
          <div class="section-header">
            <h2>数据源配置</h2>
            <p>配置股票数据获取的相关参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>AKShare 配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>API 超时时间 (秒)</label>
                  <input 
                    v-model.number="settings.datasource.akshare.timeout" 
                    type="number" 
                    min="1" 
                    max="300"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>请求重试次数</label>
                  <input 
                    v-model.number="settings.datasource.akshare.retries" 
                    type="number" 
                    min="0" 
                    max="10"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>请求间隔 (毫秒)</label>
                  <input 
                    v-model.number="settings.datasource.akshare.interval" 
                    type="number" 
                    min="100" 
                    max="10000"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>启用缓存</label>
                  <input 
                    v-model="settings.datasource.akshare.enableCache" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>数据更新频率</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>实时数据更新间隔 (秒)</label>
                  <select v-model="settings.datasource.updateFrequency.realtime" class="form-select">
                    <option value="5">5秒</option>
                    <option value="10">10秒</option>
                    <option value="30">30秒</option>
                    <option value="60">1分钟</option>
                  </select>
                </div>
                <div class="form-item">
                  <label>历史数据更新时间</label>
                  <input 
                    v-model="settings.datasource.updateFrequency.history" 
                    type="time"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>自动更新</label>
                  <input 
                    v-model="settings.datasource.updateFrequency.autoUpdate" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据库配置 -->
        <div v-if="activeSection === 'database'" class="settings-section">
          <div class="section-header">
            <h2>数据库配置</h2>
            <p>配置数据库连接和存储参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>MySQL 配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>主机地址</label>
                  <input 
                    v-model="settings.database.mysql.host" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>端口</label>
                  <input 
                    v-model.number="settings.database.mysql.port" 
                    type="number"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>数据库名</label>
                  <input 
                    v-model="settings.database.mysql.database" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>用户名</label>
                  <input 
                    v-model="settings.database.mysql.username" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>连接池大小</label>
                  <input 
                    v-model.number="settings.database.mysql.poolSize" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
              </div>
              <div class="form-actions">
                <button @click="testDatabaseConnection" class="test-btn" :disabled="testingSource === 'database'">
                  {{ testingSource === 'database' ? '测试中...' : '测试连接' }}
                </button>
              </div>
            </div>

            <div class="setting-group">
              <h3>Redis 配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>主机地址</label>
                  <input 
                    v-model="settings.database.redis.host" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>端口</label>
                  <input 
                    v-model.number="settings.database.redis.port" 
                    type="number"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>数据库索引</label>
                  <input 
                    v-model.number="settings.database.redis.db" 
                    type="number"
                    min="0"
                    max="15"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>缓存过期时间 (秒)</label>
                  <input 
                    v-model.number="settings.database.redis.expireTime" 
                    type="number"
                    class="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI配置 -->
        <div v-if="activeSection === 'ai'" class="settings-section">
          <div class="section-header">
            <h2>AI配置</h2>
            <p>配置AI模型和分析相关参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>模型配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>默认模型</label>
                  <select v-model="settings.ai.models.defaultModel" class="form-select">
                    <option value="">请选择模型</option>
                    <option v-for="model in availableModels" :key="model.id" :value="model.id">
                      {{ model.name }}
                    </option>
                  </select>
                </div>
                <div class="form-item">
                  <label>最大Token数</label>
                  <input 
                    v-model.number="settings.ai.models.maxTokens" 
                    type="number"
                    min="1"
                    max="32768"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>温度参数</label>
                  <input 
                    v-model.number="settings.ai.models.temperature" 
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>请求超时 (秒)</label>
                  <input 
                    v-model.number="settings.ai.models.timeout" 
                    type="number"
                    min="1"
                    max="300"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>API配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>API基础URL</label>
                  <input 
                    v-model="settings.ai.api.baseUrl" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>API密钥</label>
                  <input 
                    v-model="settings.ai.api.apiKey" 
                    type="password"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>重试次数</label>
                  <input 
                    v-model.number="settings.ai.api.retries" 
                    type="number"
                    min="0"
                    max="10"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>启用缓存</label>
                  <input 
                    v-model="settings.ai.api.enableCache" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
              </div>
              <div class="form-actions">
                <button @click="testAIConnection" class="test-btn" :disabled="testingSource === 'ai'">
                  {{ testingSource === 'ai' ? '测试中...' : '测试连接' }}
                </button>
              </div>
            </div>

            <div class="setting-group">
              <h3>分析配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>批处理大小</label>
                  <input 
                    v-model.number="settings.ai.analysis.batchSize" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>最大并发数</label>
                  <input 
                    v-model.number="settings.ai.analysis.maxConcurrency" 
                    type="number"
                    min="1"
                    max="10"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>自动重试</label>
                  <input 
                    v-model="settings.ai.analysis.autoRetry" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
                <div class="form-item">
                  <label>结果保留天数</label>
                  <input 
                    v-model.number="settings.ai.analysis.resultRetentionDays" 
                    type="number"
                    min="1"
                    max="365"
                    class="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 任务调度配置 -->
        <div v-if="activeSection === 'scheduler'" class="settings-section">
          <div class="section-header">
            <h2>任务调度配置</h2>
            <p>配置 Celery 任务调度相关参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>Celery 配置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>Broker URL</label>
                  <input 
                    v-model="settings.scheduler.celery.brokerUrl" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>Result Backend</label>
                  <input 
                    v-model="settings.scheduler.celery.resultBackend" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>最大并发数</label>
                  <input 
                    v-model.number="settings.scheduler.celery.concurrency" 
                    type="number"
                    min="1"
                    max="50"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>任务超时时间 (秒)</label>
                  <input 
                    v-model.number="settings.scheduler.celery.taskTimeout" 
                    type="number"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>定时任务</h3>
              <div class="task-schedule-list">
                <div v-for="(task, index) in settings.scheduler.scheduledTasks" :key="index" class="task-schedule-item">
                  <div class="task-info">
                    <input v-model="task.name" placeholder="任务名称" class="task-name-input" />
                    <input v-model="task.cron" placeholder="Cron 表达式" class="task-cron-input" />
                    <input v-model="task.enabled" type="checkbox" class="task-enabled-checkbox" />
                  </div>
                  <button @click="removeScheduledTask(index)" class="remove-task-btn">删除</button>
                </div>
                <button @click="addScheduledTask" class="add-task-btn">添加定时任务</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统监控配置 -->
        <div v-if="activeSection === 'monitoring'" class="settings-section">
          <div class="section-header">
            <h2>系统监控配置</h2>
            <p>配置系统性能监控和告警参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>性能监控</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>CPU 使用率告警阈值 (%)</label>
                  <input 
                    v-model.number="settings.monitoring.performance.cpuThreshold" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>内存使用率告警阈值 (%)</label>
                  <input 
                    v-model.number="settings.monitoring.performance.memoryThreshold" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>磁盘使用率告警阈值 (%)</label>
                  <input 
                    v-model.number="settings.monitoring.performance.diskThreshold" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>监控数据保留天数</label>
                  <input 
                    v-model.number="settings.monitoring.performance.retentionDays" 
                    type="number"
                    min="1"
                    max="365"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>告警设置</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>启用邮件告警</label>
                  <input 
                    v-model="settings.monitoring.alerts.emailEnabled" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
                <div class="form-item">
                  <label>告警邮箱</label>
                  <input 
                    v-model="settings.monitoring.alerts.emailAddress" 
                    type="email"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>告警间隔 (分钟)</label>
                  <input 
                    v-model.number="settings.monitoring.alerts.interval" 
                    type="number"
                    min="1"
                    max="1440"
                    class="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 日志配置 -->
        <div v-if="activeSection === 'logging'" class="settings-section">
          <div class="section-header">
            <h2>日志配置</h2>
            <p>配置系统日志记录和存储参数</p>
          </div>
          
          <div class="setting-groups">
            <div class="setting-group">
              <h3>日志级别</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>应用日志级别</label>
                  <select v-model="settings.logging.levels.application" class="form-select">
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
                <div class="form-item">
                  <label>数据库日志级别</label>
                  <select v-model="settings.logging.levels.database" class="form-select">
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
                <div class="form-item">
                  <label>任务日志级别</label>
                  <select v-model="settings.logging.levels.task" class="form-select">
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>日志存储</h3>
              <div class="form-grid">
                <div class="form-item">
                  <label>日志文件路径</label>
                  <input 
                    v-model="settings.logging.storage.filePath" 
                    type="text"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>单个文件最大大小 (MB)</label>
                  <input 
                    v-model.number="settings.logging.storage.maxFileSize" 
                    type="number"
                    min="1"
                    max="1000"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>保留文件数量</label>
                  <input 
                    v-model.number="settings.logging.storage.backupCount" 
                    type="number"
                    min="1"
                    max="100"
                    class="form-input"
                  />
                </div>
                <div class="form-item">
                  <label>启用日志压缩</label>
                  <input 
                    v-model="settings.logging.storage.compress" 
                    type="checkbox"
                    class="form-checkbox"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemAPI, aiAPI } from '@/services/api'
import Loading from '@/components/Loading.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

// 接口定义
interface ScheduledTask {
  name: string
  cron: string
  enabled: boolean
}

interface Settings {
  datasource: {
    akshare: {
      timeout: number
      retries: number
      interval: number
      enableCache: boolean
    }
    updateFrequency: {
      realtime: string
      history: string
      autoUpdate: boolean
    }
  }
  database: {
    mysql: {
      host: string
      port: number
      database: string
      username: string
      poolSize: number
    }
    redis: {
      host: string
      port: number
      db: number
      expireTime: number
    }
  }
  ai: {
    models: {
      defaultModel: string
      maxTokens: number
      temperature: number
      timeout: number
    }
    api: {
      baseUrl: string
      apiKey: string
      retries: number
      enableCache: boolean
    }
    analysis: {
      batchSize: number
      maxConcurrency: number
      autoRetry: boolean
      resultRetentionDays: number
    }
  }
  scheduler: {
    celery: {
      brokerUrl: string
      resultBackend: string
      concurrency: number
      taskTimeout: number
    }
    scheduledTasks: ScheduledTask[]
  }
  monitoring: {
    performance: {
      cpuThreshold: number
      memoryThreshold: number
      diskThreshold: number
      retentionDays: number
    }
    alerts: {
      emailEnabled: boolean
      emailAddress: string
      interval: number
    }
  }
  logging: {
    levels: {
      application: string
      database: string
      task: string
    }
    storage: {
      filePath: string
      maxFileSize: number
      backupCount: number
      compress: boolean
    }
  }
}

// 响应式数据
const activeSection = ref('datasource')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const testingSource = ref('')
const availableModels = ref<any[]>([])

// 设置项配置
const sections = [
  { key: 'datasource', label: '数据源配置', icon: '📊' },
  { key: 'database', label: '数据库配置', icon: '🗄️' },
  { key: 'ai', label: 'AI配置', icon: '🤖' },
  { key: 'scheduler', label: '任务调度', icon: '⏰' },
  { key: 'monitoring', label: '系统监控', icon: '📈' },
  { key: 'logging', label: '日志配置', icon: '📝' }
]

// 默认设置
const settings = ref<Settings>({
  datasource: {
    akshare: {
      timeout: 30,
      retries: 3,
      interval: 1000,
      enableCache: true
    },
    updateFrequency: {
      realtime: '30',
      history: '18:00',
      autoUpdate: true
    }
  },
  database: {
    mysql: {
      host: '115.190.80.219',
      port: 3306,
      database: 'stock_analysis',
      username: 'root',
      poolSize: 10
    },
    redis: {
      host: 'localhost',
      port: 6379,
      db: 0,
      expireTime: 3600
    }
  },
  ai: {
    models: {
      defaultModel: '',
      maxTokens: 4096,
      temperature: 0.7,
      timeout: 30
    },
    api: {
      baseUrl: 'http://localhost:8000/api/ai',
      apiKey: '',
      retries: 3,
      enableCache: true
    },
    analysis: {
      batchSize: 10,
      maxConcurrency: 3,
      autoRetry: true,
      resultRetentionDays: 30
    }
  },
  scheduler: {
    celery: {
      brokerUrl: 'redis://localhost:6379/1',
      resultBackend: 'redis://localhost:6379/2',
      concurrency: 4,
      taskTimeout: 300
    },
    scheduledTasks: [
      { name: '实时数据更新', cron: '*/30 * * * *', enabled: true },
      { name: '历史数据更新', cron: '0 18 * * *', enabled: true }
    ]
  },
  monitoring: {
    performance: {
      cpuThreshold: 80,
      memoryThreshold: 85,
      diskThreshold: 90,
      retentionDays: 30
    },
    alerts: {
      emailEnabled: false,
      emailAddress: '',
      interval: 30
    }
  },
  logging: {
    levels: {
      application: 'INFO',
      database: 'WARNING',
      task: 'INFO'
    },
    storage: {
      filePath: '/var/log/stock_analysis/',
      maxFileSize: 100,
      backupCount: 10,
      compress: true
    }
  }
})

// 方法
const loadSettings = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await systemAPI.getSettings()
    settings.value = { ...settings.value, ...response.data }
  } catch (err) {
    console.error('加载设置失败:', err)
    error.value = '加载系统设置失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

const refreshSettings = () => {
  loadSettings()
}

const clearError = () => {
  error.value = ''
}

const saveAllSettings = async () => {
  saving.value = true
  error.value = ''
  try {
    await systemAPI.updateSettings(settings.value)
    ElMessage.success('设置保存成功')
  } catch (err) {
    console.error('保存设置失败:', err)
    error.value = '保存设置失败，请检查输入内容或稍后重试'
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

const testDatabaseConnection = async () => {
  testingSource.value = 'database'
  try {
    const response = await systemAPI.testDatabaseConnection(settings.value.database.mysql)
    if (response.data?.status === 'success') {
      ElMessage.success('数据库连接测试成功')
    } else {
      ElMessage.error(`数据库连接测试失败: ${response.data?.message || '未知错误'}`)
    }
  } catch (err) {
    console.error('数据库连接测试失败:', err)
    ElMessage.error('数据库连接测试失败，请检查配置参数')
  } finally {
    testingSource.value = ''
  }
}

const testAIConnection = async () => {
  testingSource.value = 'ai'
  try {
    const response = await aiAPI.getModels()
    availableModels.value = response.data || []
    ElMessage.success(`AI服务连接成功，发现 ${response.data?.length || 0} 个可用模型`)
  } catch (err) {
    console.error('AI服务连接测试失败:', err)
    ElMessage.error('AI服务连接测试失败，请检查配置参数')
  } finally {
    testingSource.value = ''
  }
}

const addScheduledTask = () => {
  settings.value.scheduler.scheduledTasks.push({
    name: '',
    cron: '',
    enabled: true
  })
}

const removeScheduledTask = (index: number) => {
  settings.value.scheduler.scheduledTasks.splice(index, 1)
}

const loadAIModels = async () => {
  try {
    const response = await aiAPI.getModels()
    availableModels.value = response.data
  } catch (err) {
    console.error('加载AI模型失败:', err)
  }
}

// 生命周期钩子
onMounted(() => {
  loadSettings()
  loadAIModels()
})
</script>

<style scoped>
.system-settings {
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

.page-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2.5em;
  font-weight: 300;
}

.save-btn {
  padding: 10px 20px;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:hover {
  background-color: #229954;
}

.save-btn:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.settings-container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}

.settings-sidebar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px 0;
}

.settings-nav {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  color: #7f8c8d;
  font-size: 14px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: #f8f9fa;
  color: #2c3e50;
}

.nav-item.active {
  background-color: #3498db;
  color: white;
  border-right: 3px solid #2980b9;
}

.nav-icon {
  font-size: 16px;
}

.nav-label {
  font-weight: 500;
}

.settings-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
  overflow-y: auto;
}

.settings-section {
  max-width: 800px;
}

.section-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #ecf0f1;
}

.section-header h2 {
  color: #2c3e50;
  margin: 0 0 8px 0;
  font-size: 1.8em;
  font-weight: 400;
}

.section-header p {
  color: #7f8c8d;
  margin: 0;
  font-size: 14px;
}

.setting-groups {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.setting-group {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 20px;
}

.setting-group h3 {
  color: #34495e;
  margin: 0 0 20px 0;
  font-size: 1.2em;
  font-weight: 500;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

.form-input, .form-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.test-btn {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.test-btn:hover {
  background-color: #2980b9;
}

.task-schedule-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-schedule-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.task-info {
  display: flex;
  gap: 10px;
  flex: 1;
  align-items: center;
}

.task-name-input, .task-cron-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.task-name-input {
  flex: 2;
}

.task-cron-input {
  flex: 3;
}

.task-enabled-checkbox {
  width: 16px;
  height: 16px;
}

.remove-task-btn {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.remove-task-btn:hover {
  background-color: #c0392b;
}

.add-task-btn {
  padding: 10px 20px;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  align-self: flex-start;
}

.add-task-btn:hover {
  background-color: #229954;
}

@media (max-width: 1024px) {
  .settings-container {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .settings-sidebar {
    order: 2;
  }
  
  .settings-content {
    order: 1;
  }
  
  .settings-nav {
    flex-direction: row;
    overflow-x: auto;
    padding: 0 10px;
  }
  
  .nav-item {
    white-space: nowrap;
    min-width: 120px;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .task-info {
    flex-direction: column;
    align-items: stretch;
  }
  
  .task-schedule-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>