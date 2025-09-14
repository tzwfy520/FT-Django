import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  // 1. 仪表盘
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: {
      title: '仪表盘',
      icon: '📊',
      order: 1
    }
  },
  // 2. 大盘信息
  {
    path: '/market-info',
    name: 'MarketInfo',
    meta: {
      title: '大盘信息',
      icon: '📈',
      order: 2
    },
    children: [
      {
        path: 'realtime-data',
        name: 'MarketRealtimeData',
        component: () => import('../views/market/MarketRealtimeData.vue'),
        meta: {
          title: '大盘实时数据',
          parent: '大盘信息'
        }
      },
      {
        path: 'historical-data',
        name: 'MarketHistoricalData',
        component: () => import('../views/market/MarketHistoricalData.vue'),
        meta: {
          title: '大盘历史数据',
          parent: '大盘信息'
        }
      },
      {
        path: 'realtime-flow',
        name: 'RealtimeMoneyFlow',
        component: () => import('../views/market/MarketCapitalFlow.vue'),
        meta: {
          title: '实时资金流向',
          parent: '大盘信息'
        }
      },
      {
        path: 'historical-flow',
        name: 'HistoricalMoneyFlow',
        component: () => import('../views/market/MarketHistoricalCapitalFlow.vue'),
        meta: {
          title: '历史资金流向',
          parent: '大盘信息'
        }
      },
      {
        path: 'dragon-tiger',
        name: 'DragonTigerList',
        component: () => import('../views/market/DragonTigerList.vue'),
        meta: {
          title: '龙虎榜',
          parent: '大盘信息'
        }
      },
      {
        path: 'margin-trading',
        name: 'MarginTradingData',
        component: () => import('../views/market/MarginTradingData.vue'),
        meta: {
          title: '两融数据',
          parent: '大盘信息'
        }
      },
      {
        path: 'stock-calendar',
        name: 'StockCalendar',
        component: () => import('../views/market/StockCalendar.vue'),
        meta: {
          title: '股票日历',
          parent: '大盘信息'
        }
      }
    ]
  },
  // 3. 行业板块
  {
    path: '/industry-sector',
    name: 'IndustrySector',
    meta: {
      title: '行业板块',
      icon: '🏭',
      order: 3
    },
    children: [
      {
        path: 'components',
        name: 'IndustryComponents',
        component: () => import('../views/industry/IndustryComponents.vue'),
        meta: {
          title: '行业板块成份',
          parent: '行业板块'
        }
      },
      {
        path: 'realtime-data',
        name: 'IndustryRealtimeData',
        component: () => import('../views/industry/IndustryRealtimeData.vue'),
        meta: {
          title: '行业实时数据',
          parent: '行业板块'
        }
      },
      {
        path: 'intraday-data',
        name: 'IndustryIntradayData',
        component: () => import('../views/industry/IndustryIntradayData.vue'),
        meta: {
          title: '行业分时数据',
          parent: '行业板块'
        }
      },
      {
        path: 'historical-data',
        name: 'IndustryHistoricalData',
        component: () => import('../views/industry/IndustryHistoricalData.vue'),
        meta: {
          title: '行业历史数据',
          parent: '行业板块'
        }
      }
    ]
  },
  // 4. 概念板块
  {
    path: '/concept-sector',
    name: 'ConceptSector',
    meta: {
      title: '概念板块',
      icon: '💡',
      order: 4
    },
    children: [
      {
        path: 'components',
        name: 'ConceptComponents',
        component: () => import('../views/concept/ConceptComponents.vue'),
        meta: {
          title: '概念板块成份',
          parent: '概念板块'
        }
      },
      {
        path: 'realtime-data',
        name: 'ConceptRealtimeData',
        component: () => import('../views/concept/ConceptRealtimeData.vue'),
        meta: {
          title: '概念实时数据',
          parent: '概念板块'
        }
      },
      {
        path: 'intraday-data',
        name: 'ConceptIntradayData',
        component: () => import('../views/concept/ConceptIntradayData.vue'),
        meta: {
          title: '概念分时数据',
          parent: '概念板块'
        }
      },
      {
        path: 'historical-data',
        name: 'ConceptHistoricalData',
        component: () => import('../views/concept/ConceptHistoricalData.vue'),
        meta: {
          title: '概念历史数据',
          parent: '概念板块'
        }
      }
    ]
  },
  // 5. 股票数据
  {
    path: '/stock',
    name: 'StockData',
    meta: {
      title: '股票数据',
      icon: '📊',
      order: 5
    },
    children: [
      {
        path: 'overview',
        name: 'StockOverview',
        component: () => import('../views/stock/StockOverview.vue'),
        meta: {
          title: '股票概览',
          parent: '股票数据'
        }
      },
      {
        path: 'my-stocks',
        name: 'MyStocks',
        component: () => import('../views/stock/MyStocks.vue'),
        meta: {
          title: '自选股票',
          parent: '股票数据'
        }
      },
      {
        path: 'realtime-trading',
        name: 'RealtimeTradingData',
        component: () => import('../views/stock/RealtimeTrading.vue'),
        meta: {
          title: '实时交易数据',
          parent: '股票数据'
        }
      },
      {
        path: 'historical-trading',
        name: 'HistoricalTradingData',
        component: () => import('../views/stock/HistoricalTrading.vue'),
        meta: {
          title: '历史交易数据',
          parent: '股票数据'
        }
      }
    ]
  },
  // 6. 实时盯盘
  {
    path: '/realtime-monitor',
    name: 'RealtimeMonitor',
    meta: {
      title: '实时盯盘',
      icon: '👁️',
      order: 6
    },
    children: [
      {
        path: 'watchlist-stocks',
        name: 'WatchlistStocksMonitor',
        component: () => import('../views/realtime/WatchlistMonitor.vue'),
        meta: {
          title: '自选股票',
          parent: '实时盯盘'
        }
      },
      {
        path: 'custom-query',
        name: 'CustomStockQuery',
        component: () => import('../views/realtime/StockQuery.vue'),
        meta: {
          title: '自助查询',
          parent: '实时盯盘'
        }
      }
    ]
  },
  // 7. 股票复盘
  {
    path: '/stock-review',
    name: 'StockReview',
    meta: {
      title: '股票复盘',
      icon: '📋',
      order: 7
    },
    children: [
      {
        path: 'watchlist-review',
        name: 'WatchlistStockReview',
        component: () => import('../views/review/StockReview.vue'),
        meta: {
          title: '自选股票',
          parent: '股票复盘'
        }
      },
      {
        path: 'custom-review',
        name: 'CustomStockReview',
        component: () => import('../views/review/CustomQuery.vue'),
        meta: {
          title: '自助查询',
          parent: '股票复盘'
        }
      }
    ]
  },
  // 8. 任务管理
  {
    path: '/task-management',
    name: 'TaskManagement',
    meta: {
      title: '任务管理',
      icon: '⚙️',
      order: 8
    },
    redirect: '/task-management/settings',
    children: [
      {
        path: 'settings',
        name: 'TaskSettings',
        component: () => import('../views/task-management/TaskSettings.vue'),
        meta: {
          title: '任务设置',
          parent: '任务管理'
        }
      },
      {
        path: 'records',
        name: 'TaskRecords',
        component: () => import('../views/task-management/TaskRecords.vue'),
        meta: {
          title: '任务记录',
          parent: '任务管理'
        }
      }
    ]
  },
  // 9. AI分析
  {
    path: '/ai-analysis',
    name: 'AIAnalysis',
    component: () => import('../views/AIAnalysis.vue'),
    meta: {
      title: 'AI分析',
      icon: '🤖',
      order: 9
    },
    redirect: '/ai-analysis/task-overview',
    children: [
      {
        path: 'task-overview',
        name: 'TaskOverview',
        component: () => import('../views/ai-analysis/TaskOverview.vue'),
        meta: {
          title: '任务概览',
          parent: 'AI分析'
        }
      },
      {
        path: 'stock-review',
        name: 'StockReviewConfig',
        component: () => import('../views/ai-analysis/StockReview.vue'),
        meta: {
          title: '股票复盘',
          parent: 'AI分析'
        }
      },
      {
        path: 'realtime-monitoring',
        name: 'RealtimeMonitoringConfig',
        component: () => import('../views/ai-analysis/RealTimeMonitoring.vue'),
        meta: {
          title: '实时盯盘',
          parent: 'AI分析'
        }
      },
      {
        path: 'stock-recommendation',
        name: 'StockRecommendationConfig',
        component: () => import('../views/ai-analysis/StockRecommendation.vue'),
        meta: {
          title: '股票推荐',
          parent: 'AI分析'
        }
      }
    ]
  },
  // 10. 数据源管理
  {
    path: '/data-source',
    name: 'DataSourceManagement',
    component: () => import('../views/system/DataSourceManagement.vue'),
    meta: {
      title: '数据源管理',
      icon: '🗄️',
      order: 10
    }
  },
  // 11. 接口管理
  {
    path: '/api-management',
    name: 'ApiManagement',
    component: () => import('../views/api-management/ApiManagement.vue'),
    meta: {
      title: '接口管理',
      icon: '🔌',
      order: 11
    },
    redirect: '/api-management/aihubmix',
    children: [
      {
        path: 'aihubmix',
        name: 'AihubmixManagement',
        component: () => import('../views/api-management/AihubmixManagement.vue'),
        meta: {
          title: '推理时代',
          parent: '接口管理'
        }
      },
      {
        path: 'coze',
        name: 'CozeManagement',
        component: () => import('../views/api-management/CozeManagement.vue'),
        meta: {
          title: 'Coze',
          parent: '接口管理'
        }
      }
    ]
  },
  // 12. 系统设置
  {
    path: '/system-settings',
    name: 'SystemSettings',
    component: () => import('../views/system/SystemSettings.vue'),
    meta: {
      title: '系统设置',
      icon: '🔧',
      order: 12
    },
    children: [
      {
        path: 'overview',
        name: 'SystemOverview',
        component: () => import('../views/system/SystemOverview.vue'),
        meta: {
          title: '系统概览',
          parent: '系统设置'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  
  // 如果访问登录页面且已登录，重定向到首页
  if (to.path === '/login' && isAuthenticated) {
    next('/')
    return
  }
  
  // 如果访问需要认证的页面但未登录，重定向到登录页
  if (to.path !== '/login' && !isAuthenticated) {
    next('/login')
    return
  }
  
  next()
})

export default router
