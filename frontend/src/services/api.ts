import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10分钟超时
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 确保发送cookies
})

// 初始化CSRF token
export const initializeCSRF = async (): Promise<void> => {
  try {
    await apiClient.get('/api-management/csrf-token/')
  } catch (error) {
    console.warn('Failed to initialize CSRF token:', error)
  }
}

// 获取CSRF token的函数
function getCSRFToken(): string | null {
  const name = 'csrftoken'
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// 请求拦截器
apiClient.interceptors.request.use(
  (config: any) => {
    // 添加认证token（如果有）
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加CSRF token
    const csrfToken = getCSRFToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    
    return config
  },
  (error: any) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: any) => {
    if (error.response?.status === 401) {
      // 处理未授权错误
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API接口定义
export const stocksAPI = {
  // 获取股票列表
  getStockList: (params?: any) => apiClient.get('/stocks/list/', { params }),
  
  // 获取实时数据
  getRealTimeData: (stockCode?: string) => {
    const url = stockCode ? `/stocks/realtime/${stockCode}/` : '/stocks/realtime/'
    return apiClient.get(url)
  },
  
  // 获取历史数据
  getHistoryData: (stockCode: string, params?: any) => 
    apiClient.get('/stocks/history/', { params: { code: stockCode, ...params } }),
  
  // 获取每日历史数据（前复权）
  getDailyHistoryData: (stockCode: string, params?: any) => 
    apiClient.get('/stocks/history/daily/', { params: { stock_code: stockCode, ...params } }),
  
  // 获取每周历史数据（前复权）
  getWeeklyHistoryData: (stockCode: string, params?: any) => 
    apiClient.get('/stocks/history/weekly/', { params: { stock_code: stockCode, ...params } }),
  
  // 获取每月历史数据（前复权）
  getMonthlyHistoryData: (stockCode: string, params?: any) => 
    apiClient.get('/stocks/history/monthly/', { params: { stock_code: stockCode, ...params } }),
  
  // 历史数据采集任务管理
  getHistoryTaskStatus: (taskId?: string) => {
    const url = taskId ? `/stocks/tasks/history/${taskId}/` : '/stocks/tasks/history/'
    return apiClient.get(url)
  },
  
  createHistoryTask: (data: any) => 
    apiClient.post('/stocks/tasks/history/', data),
  
  // 获取分钟数据
  getMinuteData: (stockCode: string, params?: any) => 
    apiClient.get(`/stocks/minute/${stockCode}/`, { params }),
  
  // 获取财务数据
  getFinancialData: (stockCode: string) => 
    apiClient.get(`/stocks/financial/${stockCode}/`),
  
  // 获取技术指标
  getIndicators: (stockCode: string, params?: any) => 
    apiClient.get(`/stocks/indicators/${stockCode}/`, { params }),
  
  // 数据同步
  syncData: (data: any) => apiClient.post('/stocks/sync/', data),
  
  // 获取统计信息
  getStats: () => apiClient.get('/stocks/stats/'),
  
  // 获取股票概览
  getOverview: (params?: any) => apiClient.get('/stocks/overview/', { params }),
  
  // 搜索股票
  searchStocks: (params?: any) => apiClient.get('/stocks/search/', { params }),
  
  // 自选股相关
  getWatchlist: (params?: any) => apiClient.get('/stocks/watchlist/', { params }),
  addToWatchlist: (data: any) => apiClient.post('/stocks/watchlist/', data),
  removeFromWatchlist: (data: any) => apiClient.delete('/stocks/watchlist/', { data }),
  
  // 行业板块相关
  getIndustryList: (params?: any) => apiClient.get('/stocks/industries/', { params }),
  getIndustryStocks: (params?: any) => apiClient.get('/stocks/industries/stocks/', { params }),
  
  // 概念板块相关
  getConceptList: (params?: any) => apiClient.get('/stocks/concepts/', { params }),
  getConceptStocks: (params?: any) => apiClient.get('/stocks/concepts/stocks/', { params }),
}

export const tasksAPI = {
  // 获取任务定义列表
  getTaskDefinitions: (params?: any) => apiClient.get('/tasks/definitions/', { params }),
  
  // 创建任务定义
  createTaskDefinition: (data: any) => apiClient.post('/tasks/definitions/', data),
  
  // 更新任务定义
  updateTaskDefinition: (id: number, data: any) => 
    apiClient.put(`/tasks/definitions/${id}/`, data),
  
  // 删除任务定义
  deleteTaskDefinition: (id: number) => apiClient.delete(`/tasks/definitions/${id}/`),
  
  // 获取任务目标详情
  getTaskTargetDetails: (id: number) => apiClient.get(`/tasks/definitions/${id}/target_details/`),
  
  // 获取任务执行记录
  getTaskExecutions: (params?: any) => apiClient.get('/tasks/executions/', { params }),
  
  // 获取任务调度
  getTaskSchedules: (params?: any) => apiClient.get('/tasks/schedules/', { params }),
  
  // 任务控制
  controlTask: (data: any) => apiClient.post('/tasks/control/', data),
  
  // 获取任务统计
  getTaskStats: () => apiClient.get('/tasks/stats/'),
}

export const aiAPI = {
  // 获取AI模型列表
  getModels: (params?: any) => apiClient.get('/ai/models/', { params }),
  
  // 获取AI分析列表
  getAnalyses: (params?: any) => apiClient.get('/ai/analyses/', { params }),
  
  // 创建AI分析
  createAnalysis: (data: any) => apiClient.post('/ai/analyses/', data),
  
  // 获取分析详情
  getAnalysisDetail: (id: string) => apiClient.get(`/ai/analyses/${id}/`),
  
  // 删除分析
  deleteAnalysis: (id: string) => apiClient.delete(`/ai/analyses/${id}/`),
  
  // 下载分析报告
  downloadReport: (id: string) => apiClient.get(`/ai/analyses/${id}/report/`, { responseType: 'blob' }),
  
  // AI对话
  chat: (data: any) => apiClient.post('/ai/conversation/', data),
  
  // 获取分析模板
  getTemplates: () => apiClient.get('/ai/templates/'),
  
  // 获取AI统计
  getAIStats: () => apiClient.get('/ai/stats/'),
}

export const systemAPI = {
  // 获取系统配置
  getConfig: () => apiClient.get('/system/config/'),
  
  // 更新系统配置
  updateConfig: (data: any) => apiClient.put('/system/config/', data),
  
  // 获取系统设置
  getSettings: () => apiClient.get('/system/config/'),
  
  // 更新系统设置
  updateSettings: (data: any) => apiClient.put('/system/config/', data),
  
  // 测试数据库连接
  testDatabaseConnection: (data: any) => apiClient.post('/system/test/', { test_type: 'database', ...data }),
  
  // 获取数据源
  getDataSources: () => apiClient.get('/system/datasources/'),
  
  // 测试数据源
  testDataSource: (data: any) => apiClient.post('/system/test/', data),
  
  // 获取系统日志
  getLogs: (params?: any) => apiClient.get('/system/logs/', { params }),
  
  // 获取系统监控
  getMonitor: () => apiClient.get('/system/monitor/'),
  
  // 获取系统统计
  getStats: () => apiClient.get('/system/stats/'),
}

export const apiManagementAPI = {
  // API提供商管理
  getProviders: (params?: any) => apiClient.get('/api-management/providers/', { params }),
  createProvider: (data: any) => apiClient.post('/api-management/providers/', data),
  updateProvider: (id: number, data: any) => apiClient.patch(`/api-management/providers/${id}/`, data),
  deleteProvider: (id: number) => apiClient.delete(`/api-management/providers/${id}/`),
  
  // API Token管理
  getTokens: (params?: any) => apiClient.get('/api-management/tokens/', { params }),
  createToken: (data: any) => apiClient.post('/api-management/tokens/', data),
  updateToken: (id: number, data: any) => apiClient.patch(`/api-management/tokens/${id}/`, data),
  deleteToken: (id: number) => apiClient.delete(`/api-management/tokens/${id}/`),
  
  // API接口配置管理
  getInterfaces: (params?: any) => apiClient.get('/api-management/interfaces/', { params }),
  createInterface: (data: any) => apiClient.post('/api-management/interfaces/', data),
  updateInterface: (id: number, data: any) => apiClient.patch(`/api-management/interfaces/${id}/`, data),
  deleteInterface: (id: number) => apiClient.delete(`/api-management/interfaces/${id}/`),
  testInterface: (id: number, data: any) => apiClient.post(`/api-management/interfaces/${id}/test_interface/`, data),
  
  // API调用
  callApi: (data: any) => apiClient.post('/api-management/call/', data),
  
  // API调用日志
  getCallLogs: (params?: any) => apiClient.get('/api-management/logs/', { params }),
  getCallLogDetail: (id: number) => apiClient.get(`/api-management/logs/${id}/`),
}

// 导出默认实例
export default apiClient