<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">📊</span>
          <span v-if="!sidebarCollapsed" class="logo-text">股票分析系统</span>
        </div>
        <button @click="toggleSidebar" class="toggle-btn">
          {{ sidebarCollapsed ? '→' : '←' }}
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <div 
          v-for="menuItem in menuItems" 
          :key="menuItem.path"
          class="menu-group"
        >
          <!-- 一级菜单 -->
          <div 
            class="nav-item parent-item"
            :class="{ 
              active: isMenuActive(menuItem),
              expanded: menuItem.expanded
            }"
            :data-tooltip="menuItem.title"
            @click="toggleMenu(menuItem)"
          >
            <span class="nav-icon">{{ menuItem.icon }}</span>
            <span v-if="!sidebarCollapsed" class="nav-text">{{ menuItem.title }}</span>
            <span 
              v-if="!sidebarCollapsed && menuItem.children" 
              class="expand-icon"
              :class="{ rotated: menuItem.expanded }"
            >
              ▶
            </span>
          </div>
          
          <!-- 二级菜单 -->
          <div 
            v-if="menuItem.children && menuItem.expanded && !sidebarCollapsed"
            class="submenu"
          >
            <router-link
              v-for="child in menuItem.children"
              :key="child.path"
              :to="child.path"
              class="nav-item child-item"
              :class="{ active: $route.path === child.path }"
            >
              <span class="nav-icon">{{ child.icon }}</span>
              <span class="nav-text">{{ child.title }}</span>
            </router-link>
          </div>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div v-if="!sidebarCollapsed" class="user-info">
          <div class="user-avatar">👤</div>
          <div class="user-details">
            <div class="user-name">{{ userInfo?.username || '未登录' }}</div>
            <div class="user-role">{{ userInfo?.is_superuser ? '超级管理员' : '普通用户' }}</div>
          </div>
          <button @click="handleLogout" class="logout-btn" title="退出登录">
            🚪
          </button>
        </div>
        <button v-else class="user-avatar-collapsed" @click="handleLogout" title="退出登录">👤</button>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="breadcrumb">
          <span class="breadcrumb-item">{{ currentPageTitle }}</span>
        </div>
        
        <div class="top-bar-actions">
          <div class="system-status">
            <span class="status-indicator" :class="systemStatus.class"></span>
            <span class="status-text">{{ systemStatus.text }}</span>
          </div>
          
          <div class="current-time">
            {{ currentTime }}
          </div>
          
          <button class="refresh-btn" @click="refreshData" :disabled="refreshing">
            <span class="refresh-icon" :class="{ spinning: refreshing }">🔄</span>
          </button>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// 响应式数据
const sidebarCollapsed = ref(false)
const refreshing = ref(false)
const currentTime = ref('')
const userInfo = ref<any>(null)
const systemStatus = ref({
  class: 'online',
  text: '系统正常'
})

// 菜单数据
const menuItems = ref([
  {
    path: '/dashboard',
    title: '仪表盘',
    icon: '📊',
    expanded: false
  },
  {
    path: '/market-info',
    title: '大盘信息',
    icon: '📈',
    expanded: false,
    children: [
      { path: '/market-info/realtime-data', title: '大盘实时数据', icon: '⚡' },
      { path: '/market-info/historical-data', title: '大盘历史数据', icon: '📋' },
      { path: '/market-info/realtime-flow', title: '实时资金流向', icon: '💰' },
      { path: '/market-info/historical-flow', title: '历史资金流向', icon: '💹' },
      { path: '/market-info/dragon-tiger', title: '龙虎榜', icon: '🐉' },
      { path: '/market-info/margin-trading', title: '两融数据', icon: '📊' },
      { path: '/market-info/stock-calendar', title: '股票日历', icon: '📅' }
    ]
  },
  {
    path: '/industry-sector',
    title: '行业板块',
    icon: '🏭',
    expanded: false,
    children: [
      { path: '/industry-sector/components', title: '行业板块成份', icon: '📦' },
      { path: '/industry-sector/realtime-data', title: '行业实时数据', icon: '⚡' },
      { path: '/industry-sector/intraday-data', title: '行业分时数据', icon: '📊' },
      { path: '/industry-sector/historical-data', title: '行业历史数据', icon: '📋' }
    ]
  },
  {
    path: '/concept-sector',
    title: '概念板块',
    icon: '💡',
    expanded: false,
    children: [
      { path: '/concept-sector/components', title: '概念板块成份', icon: '📦' },
      { path: '/concept-sector/realtime-data', title: '概念实时数据', icon: '⚡' },
      { path: '/concept-sector/intraday-data', title: '概念分时数据', icon: '📊' },
      { path: '/concept-sector/historical-data', title: '概念历史数据', icon: '📋' }
    ]
  },
  {    path: '/stock',    title: '股票数据',    icon: '📈',    expanded: false,    children: [      { path: '/stock/overview', title: '股票概览', icon: '👁️' },      { path: '/stock/my-stocks', title: '自选股票', icon: '⭐' },      { path: '/stock/realtime-trading', title: '实时交易数据', icon: '⚡' },      { path: '/stock/historical-trading', title: '历史交易数据', icon: '📋' }    ]  },
  {
    path: '/realtime-monitor',
    title: '实时盯盘',
    icon: '👁️',
    expanded: false,
    children: [
      { path: '/realtime-monitor/watchlist-stocks', title: '自选股票', icon: '⭐' },
      { path: '/realtime-monitor/custom-query', title: '自助查询', icon: '🔍' }
    ]
  },
  {
    path: '/stock-review',
    title: '股票复盘',
    icon: '🔄',
    expanded: false,
    children: [
      { path: '/stock-review/watchlist-review', title: '自选股票', icon: '⭐' },
      { path: '/stock-review/custom-review', title: '自助查询', icon: '🔍' }
    ]
  },
  {
    path: '/task-management',
    title: '任务管理',
    icon: '⚙️',
    expanded: false,
    children: [
      { path: '/task-management/settings', title: '任务设置', icon: '⚙️' },
      { path: '/task-management/records', title: '任务记录', icon: '📋' }
    ]
  },
  {
    path: '/ai-analysis',
    title: 'AI分析',
    icon: '🤖',
    expanded: false,
    children: [
      { path: '/ai-analysis/task-overview', title: '任务概览', icon: '📊' },
      { path: '/ai-analysis/stock-review', title: '股票复盘', icon: '📋' },
      { path: '/ai-analysis/realtime-monitoring', title: '实时盯盘', icon: '👁️' },
      { path: '/ai-analysis/stock-recommendation', title: '股票推荐', icon: '💡' }
    ]
  },
  {
    path: '/data-source',
    title: '数据源管理',
    icon: '🗄️',
    expanded: false
  },
  {
    path: '/api-management',
    title: '接口管理',
    icon: '🔌',
    expanded: false,
    children: [
      { path: '/api-management/aihubmix', title: '推理时代', icon: '🧠' },
      { path: '/api-management/coze', title: 'Coze', icon: '🤖' }
    ]
  },
  {
    path: '/system-settings',
    title: '系统设置',
    icon: '⚙️',
    expanded: false,
    children: [
      { path: '/system-settings/overview', title: '系统概览', icon: '📊' }
    ]
  }
])

// 计算属性
const navigationRoutes = computed(() => {
  return router.getRoutes().filter(route => 
    route.meta?.title && route.path !== '/'
  )
})

const currentPageTitle = computed(() => {
  // 先尝试从路由meta获取标题
  if (route.meta?.title) {
    return route.meta.title as string
  }
  
  // 如果没有，从菜单数据中查找
  for (const menuItem of menuItems.value) {
    if (menuItem.path === route.path) {
      return menuItem.title
    }
    if (menuItem.children) {
      for (const child of menuItem.children) {
        if (child.path === route.path) {
          return child.title
        }
      }
    }
  }
  
  return '未知页面'
})

// 定时器
let timeInterval: number

// 生命周期
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  checkSystemStatus()
  loadUserInfo()
  
  // 从本地存储恢复侧边栏状态
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    sidebarCollapsed.value = JSON.parse(savedState)
  }
  
  // 根据当前路由自动展开对应的菜单
  autoExpandCurrentMenu()
})

const autoExpandCurrentMenu = () => {
  menuItems.value.forEach(menuItem => {
    if (menuItem.children) {
      const hasActiveChild = menuItem.children.some((child: any) => 
        route.path === child.path
      )
      if (hasActiveChild && !sidebarCollapsed.value) {
        menuItem.expanded = true
      }
    }
  })
}

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', JSON.stringify(sidebarCollapsed.value))
  
  // 如果收起侧边栏，关闭所有展开的菜单
  if (sidebarCollapsed.value) {
    menuItems.value.forEach(item => {
      item.expanded = false
    })
  }
}

const toggleMenu = (menuItem: any) => {
  // 如果侧边栏收起状态，直接跳转到第一个子菜单或菜单本身
  if (sidebarCollapsed.value) {
    if (menuItem.children && menuItem.children.length > 0) {
      router.push(menuItem.children[0].path)
    } else {
      router.push(menuItem.path)
    }
    return
  }
  
  // 如果有子菜单，切换展开状态
  if (menuItem.children) {
    menuItem.expanded = !menuItem.expanded
    
    // 关闭其他展开的菜单（可选：实现手风琴效果）
    menuItems.value.forEach(item => {
      if (item !== menuItem) {
        item.expanded = false
      }
    })
  } else {
    // 没有子菜单，直接跳转
    router.push(menuItem.path)
  }
}

const handleLogout = async () => {
  try {
    await axios.post('/api/v1/api-management/auth/logout/')
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    // 清除本地存储
    localStorage.removeItem('isAuthenticated')
    localStorage.removeItem('userInfo')
    userInfo.value = null
    // 跳转到登录页
    router.push('/login')
  }
}

const loadUserInfo = () => {
  const storedUserInfo = localStorage.getItem('userInfo')
  if (storedUserInfo) {
    try {
      userInfo.value = JSON.parse(storedUserInfo)
    } catch (error) {
      console.error('解析用户信息失败:', error)
      localStorage.removeItem('userInfo')
    }
  }
}

const isMenuActive = (menuItem: any): boolean => {
  // 检查当前路径是否匹配菜单项或其子菜单
  if (route.path === menuItem.path) {
    return true
  }
  
  if (menuItem.children) {
    return menuItem.children.some((child: any) => route.path === child.path)
  }
  
  return false
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const refreshData = async () => {
  refreshing.value = true
  try {
    // 这里可以添加刷新当前页面数据的逻辑
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟刷新
    
    // 触发当前页面的数据刷新
    window.dispatchEvent(new CustomEvent('refresh-data'))
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    refreshing.value = false
  }
}

const checkSystemStatus = async () => {
  // 移除在线检测功能，固定显示系统正常
  systemStatus.value = {
    class: 'online',
    text: '系统正常'
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.menu-group {
  margin: 4px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  cursor: pointer;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left-color: #3498db;
}

.parent-item {
  font-weight: 500;
}

.parent-item.expanded {
  background: rgba(255, 255, 255, 0.1);
}

.child-item {
  padding: 8px 20px 8px 40px;
  font-size: 14px;
  margin: 1px 0;
}

.child-item .nav-icon {
  font-size: 14px;
}

.expand-icon {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.2s ease;
  color: rgba(255, 255, 255, 0.6);
}

.expand-icon.rotated {
  transform: rotate(90deg);
}

.submenu {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin: 4px 0;
  padding: 4px 0;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    padding: 0;
  }
  to {
    opacity: 1;
    max-height: 300px;
    padding: 4px 0;
  }
}

.nav-icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.nav-text {
  font-weight: 500;
  white-space: nowrap;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logout-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: auto;
  font-size: 16px;
  transition: all 0.2s ease;
  opacity: 0.7;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  opacity: 1;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.user-avatar-collapsed {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  font-size: 18px;
  margin: 0 auto;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.online {
  background-color: #27ae60;
}

.status-indicator.offline {
  background-color: #e74c3c;
}

.status-indicator.error {
  background-color: #f39c12;
}

.status-text {
  font-size: 14px;
  color: #7f8c8d;
}

.current-time {
  font-size: 14px;
  color: #7f8c8d;
  font-family: 'Courier New', monospace;
}

.refresh-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background-color: #f8f9fa;
  border-color: #3498db;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  font-size: 16px;
  display: inline-block;
  transition: transform 0.3s ease;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f5f5;
}

/* 动画 */
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    height: 100vh;
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .top-bar-actions {
    gap: 10px;
  }
  
  .current-time {
    display: none;
  }
  
  .submenu {
    margin: 2px 0;
  }
  
  .child-item {
    padding: 8px 20px 8px 32px;
    font-size: 13px;
  }
}

/* 收起状态下的样式调整 */
.sidebar.collapsed .expand-icon {
  display: none;
}

.sidebar.collapsed .parent-item:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background-color: #2c3e50;
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-left: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (max-width: 480px) {
  .breadcrumb-item {
    font-size: 16px;
  }
  
  .system-status {
    display: none;
  }
}
</style>