<template>
  <div class="stock-calendar">
    <div class="page-header">
      <h2>股票日历</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="selectedMonth"
          type="month"
          placeholder="选择月份"
          format="YYYY-MM"
          value-format="YYYY-MM"
          @change="loadCalendarData"
        />
        <el-select v-model="eventType" placeholder="事件类型" @change="filterEvents">
          <el-option label="全部事件" value="all" />
          <el-option label="财报发布" value="earnings" />
          <el-option label="股东大会" value="meeting" />
          <el-option label="分红派息" value="dividend" />
          <el-option label="新股上市" value="ipo" />
          <el-option label="停复牌" value="suspension" />
          <el-option label="重要公告" value="announcement" />
        </el-select>
        <el-button type="primary" @click="loadCalendarData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="calendar-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">本月财报</div>
              <div class="card-value">{{ overviewData.earningsCount }}</div>
              <div class="card-subtitle">家公司发布</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">分红派息</div>
              <div class="card-value">{{ overviewData.dividendCount }}</div>
              <div class="card-subtitle">只股票除权</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">新股上市</div>
              <div class="card-value">{{ overviewData.ipoCount }}</div>
              <div class="card-subtitle">只新股</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-title">股东大会</div>
              <div class="card-value">{{ overviewData.meetingCount }}</div>
              <div class="card-subtitle">场会议</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="calendar-container">
      <el-card>
        <template #header>
          <div class="calendar-header">
            <span>{{ currentMonthText }}</span>
            <div class="view-controls">
              <el-radio-group v-model="viewMode" @change="changeViewMode">
                <el-radio-button label="calendar">日历视图</el-radio-button>
                <el-radio-button label="list">列表视图</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        
        <div v-if="viewMode === 'calendar'" class="calendar-view">
          <el-calendar v-model="calendarDate" @panel-change="handlePanelChange">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <div class="date-number">{{ data.day.split('-').slice(-1)[0] }}</div>
                <div class="events-container">
                  <div 
                    v-for="event in getEventsForDate(data.day)" 
                    :key="event.id"
                    :class="['event-item', `event-${event.type}`]"
                    @click="showEventDetail(event)"
                  >
                    {{ event.title }}
                  </div>
                </div>
              </div>
            </template>
          </el-calendar>
        </div>
        
        <div v-else class="list-view">
          <div class="date-group" v-for="dateGroup in groupedEvents" :key="dateGroup.date">
            <div class="date-header">
              <h3>{{ formatDate(dateGroup.date) }}</h3>
              <span class="event-count">{{ dateGroup.events.length }}个事件</span>
            </div>
            <div class="events-list">
              <div 
                v-for="event in dateGroup.events"
                :key="event.id"
                :class="['event-card', `event-${event.type}`]"
                @click="showEventDetail(event)"
              >
                <div class="event-header">
                  <span class="event-type-badge">{{ getEventTypeName(event.type) }}</span>
                  <span class="event-time">{{ event.time }}</span>
                </div>
                <div class="event-title">{{ event.title }}</div>
                <div class="event-description">{{ event.description }}</div>
                <div class="event-stocks">
                  <el-tag 
                    v-for="stock in event.stocks" 
                    :key="stock.code"
                    size="small"
                    @click.stop="viewStockDetail(stock.code)"
                  >
                    {{ stock.code }} {{ stock.name }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="upcoming-events">
      <el-card>
        <template #header>
          <div class="section-header">
            <span>即将到来的重要事件</span>
            <el-button size="small" @click="exportUpcomingEvents">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="event in upcomingEvents"
            :key="event.id"
            :timestamp="event.date"
            :type="getTimelineType(event.type)"
            placement="top"
          >
            <el-card class="timeline-card" @click="showEventDetail(event)">
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="event-type-badge">{{ getEventTypeName(event.type) }}</span>
                  <span class="event-importance" v-if="event.importance === 'high'">
                    <el-icon color="#f56c6c"><Warning /></el-icon>
                    重要
                  </span>
                </div>
                <div class="timeline-title">{{ event.title }}</div>
                <div class="timeline-description">{{ event.description }}</div>
                <div class="timeline-stocks">
                  <el-tag 
                    v-for="stock in event.stocks.slice(0, 3)" 
                    :key="stock.code"
                    size="small"
                    @click.stop="viewStockDetail(stock.code)"
                  >
                    {{ stock.code }} {{ stock.name }}
                  </el-tag>
                  <span v-if="event.stocks.length > 3" class="more-stocks">
                    等{{ event.stocks.length }}只股票
                  </span>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <div class="statistics-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>事件类型分布</span>
            </template>
            <div ref="pieChartContainer" class="chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>月度事件趋势</span>
            </template>
            <div ref="lineChartContainer" class="chart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 事件详情对话框 -->
    <el-dialog v-model="eventDetailVisible" title="事件详情" width="600px">
      <div v-if="selectedEvent" class="event-detail">
        <div class="detail-header">
          <span class="event-type-badge large">{{ getEventTypeName(selectedEvent.type) }}</span>
          <span class="event-date">{{ selectedEvent.date }} {{ selectedEvent.time }}</span>
        </div>
        <h3>{{ selectedEvent.title }}</h3>
        <p class="event-description">{{ selectedEvent.description }}</p>
        
        <div class="related-stocks">
          <h4>相关股票</h4>
          <div class="stocks-grid">
            <div 
              v-for="stock in selectedEvent.stocks"
              :key="stock.code"
              class="stock-item"
              @click="viewStockDetail(stock.code)"
            >
              <div class="stock-code">{{ stock.code }}</div>
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-price" :class="getChangeClass(stock.changePercent)">
                ¥{{ stock.price }} ({{ formatChange(stock.changePercent) }})
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedEvent.details" class="event-details">
          <h4>详细信息</h4>
          <div class="details-content">
            <div v-for="(value, key) in selectedEvent.details" :key="key" class="detail-item">
              <span class="detail-label">{{ key }}:</span>
              <span class="detail-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="eventDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="addToReminder">添加提醒</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

interface StockInfo {
  code: string
  name: string
  price: number
  changePercent: number
}

interface CalendarEvent {
  id: string
  type: 'earnings' | 'meeting' | 'dividend' | 'ipo' | 'suspension' | 'announcement'
  title: string
  description: string
  date: string
  time: string
  stocks: StockInfo[]
  importance: 'high' | 'medium' | 'low'
  details?: Record<string, string>
}

interface DateGroup {
  date: string
  events: CalendarEvent[]
}

const loading = ref(false)
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const eventType = ref('all')
const viewMode = ref('calendar')
const calendarDate = ref(new Date())
const eventDetailVisible = ref(false)
const selectedEvent = ref<CalendarEvent | null>(null)

const pieChartContainer = ref<HTMLElement>()
const lineChartContainer = ref<HTMLElement>()
const pieChartInstance = ref<echarts.ECharts>()
const lineChartInstance = ref<echarts.ECharts>()

const overviewData = ref({
  earningsCount: 156,
  dividendCount: 89,
  ipoCount: 12,
  meetingCount: 234
})

const allEvents = ref<CalendarEvent[]>([])
const filteredEvents = ref<CalendarEvent[]>([])

const currentMonthText = computed(() => {
  const date = new Date(selectedMonth.value + '-01')
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })
})

const groupedEvents = computed(() => {
  const groups: Record<string, CalendarEvent[]> = {}
  
  filteredEvents.value.forEach(event => {
    if (!groups[event.date]) {
      groups[event.date] = []
    }
    groups[event.date].push(event)
  })
  
  return Object.keys(groups)
    .sort()
    .map(date => ({
      date,
      events: groups[date].sort((a, b) => a.time.localeCompare(b.time))
    }))
})

const upcomingEvents = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return allEvents.value
    .filter(event => event.date >= today)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 10)
})

const loadCalendarData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 生成模拟事件数据
    const mockEvents: CalendarEvent[] = []
    const eventTypes: CalendarEvent['type'][] = ['earnings', 'meeting', 'dividend', 'ipo', 'suspension', 'announcement']
    const importanceLevels: CalendarEvent['importance'][] = ['high', 'medium', 'low']
    
    for (let i = 0; i < 100; i++) {
      const date = new Date(selectedMonth.value + '-01')
      date.setDate(Math.floor(Math.random() * 28) + 1)
      const dateStr = date.toISOString().split('T')[0]
      
      const type = eventTypes[Math.floor(Math.random() * eventTypes.length)]
      const importance = importanceLevels[Math.floor(Math.random() * importanceLevels.length)]
      
      const stocks: StockInfo[] = []
      const stockCount = Math.floor(Math.random() * 5) + 1
      for (let j = 0; j < stockCount; j++) {
        stocks.push({
          code: `${String(Math.floor(Math.random() * 999999)).padStart(6, '0')}`,
          name: `股票${j + 1}`,
          price: Number((Math.random() * 100 + 10).toFixed(2)),
          changePercent: Number(((Math.random() - 0.5) * 20).toFixed(2))
        })
      }
      
      mockEvents.push({
        id: `event_${i}`,
        type,
        title: getEventTitle(type, i),
        description: getEventDescription(type),
        date: dateStr,
        time: `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
        stocks,
        importance,
        details: getEventDetails(type)
      })
    }
    
    allEvents.value = mockEvents
    filterEvents()
    
    await nextTick()
    updateCharts()
    
    ElMessage.success('日历数据加载成功')
  } catch (error) {
    ElMessage.error('加载日历数据失败')
  } finally {
    loading.value = false
  }
}

const getEventTitle = (type: CalendarEvent['type'], index: number): string => {
  const titles = {
    earnings: `公司${index + 1}发布季度财报`,
    meeting: `公司${index + 1}股东大会`,
    dividend: `股票${index + 1}分红派息`,
    ipo: `新股${index + 1}上市交易`,
    suspension: `股票${index + 1}停牌公告`,
    announcement: `重要公告${index + 1}`
  }
  return titles[type]
}

const getEventDescription = (type: CalendarEvent['type']): string => {
  const descriptions = {
    earnings: '公司将发布最新季度财务报告，包括营收、利润等关键财务指标',
    meeting: '公司召开年度股东大会，审议重要议案和选举董事会成员',
    dividend: '股票进行分红派息，股东将获得现金分红或股票股利',
    ipo: '新股正式在交易所挂牌上市，开始公开交易',
    suspension: '股票因重大事项停牌，暂停交易直至相关事项明确',
    announcement: '公司发布重要公告，可能涉及重大资产重组、收购等事项'
  }
  return descriptions[type]
}

const getEventDetails = (type: CalendarEvent['type']): Record<string, string> => {
  const details = {
    earnings: {
      '报告期': '2024年第一季度',
      '发布时间': '盘后',
      '预期EPS': '0.85元',
      '分析师关注度': '高'
    },
    meeting: {
      '会议地点': '公司总部',
      '参会方式': '现场+网络',
      '主要议题': '年度报告审议',
      '投票截止': '会议当日'
    },
    dividend: {
      '分红方案': '每10股派2元',
      '除权日': '2024-03-15',
      '登记日': '2024-03-14',
      '派息日': '2024-03-20'
    },
    ipo: {
      '发行价格': '18.50元',
      '发行数量': '5000万股',
      '上市地点': '深圳证券交易所',
      '主承销商': 'XX证券'
    },
    suspension: {
      '停牌原因': '重大资产重组',
      '预计复牌': '待定',
      '联系方式': '投资者热线',
      '公告编号': '2024-001'
    },
    announcement: {
      '公告类型': '重大合同',
      '影响程度': '重大',
      '生效日期': '2024-03-01',
      '相关部门': '董事会'
    }
  }
  return details[type] || {}
}

const filterEvents = () => {
  if (eventType.value === 'all') {
    filteredEvents.value = allEvents.value
  } else {
    filteredEvents.value = allEvents.value.filter(event => event.type === eventType.value)
  }
}

const getEventsForDate = (date: string): CalendarEvent[] => {
  return filteredEvents.value.filter(event => event.date === date).slice(0, 3)
}

const handlePanelChange = (date: Date) => {
  const monthStr = date.toISOString().slice(0, 7)
  if (monthStr !== selectedMonth.value) {
    selectedMonth.value = monthStr
    loadCalendarData()
  }
}

const changeViewMode = () => {
  // 视图模式切换逻辑
}

const showEventDetail = (event: CalendarEvent) => {
  selectedEvent.value = event
  eventDetailVisible.value = true
}

const viewStockDetail = (stockCode: string) => {
  ElMessage.info(`查看股票 ${stockCode} 详情`)
}

const addToReminder = () => {
  ElMessage.success('提醒添加成功')
  eventDetailVisible.value = false
}

const exportUpcomingEvents = () => {
  ElMessage.success('即将到来事件导出功能开发中...')
}

const updateCharts = () => {
  updatePieChart()
  updateLineChart()
}

const updatePieChart = () => {
  if (!pieChartContainer.value) return
  
  if (!pieChartInstance.value) {
    pieChartInstance.value = echarts.init(pieChartContainer.value)
  }
  
  const typeCount = allEvents.value.reduce((acc, event) => {
    acc[event.type] = (acc[event.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const data = Object.entries(typeCount).map(([type, count]) => ({
    name: getEventTypeName(type as CalendarEvent['type']),
    value: count
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '事件类型',
        type: 'pie',
        radius: '50%',
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  pieChartInstance.value.setOption(option)
}

const updateLineChart = () => {
  if (!lineChartContainer.value) return
  
  if (!lineChartInstance.value) {
    lineChartInstance.value = echarts.init(lineChartContainer.value)
  }
  
  // 生成最近6个月的数据
  const months: string[] = []
  const eventCounts: number[] = []
  
  for (let i = 5; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    months.push(date.toLocaleDateString('zh-CN', { month: 'short' }))
    eventCounts.push(Math.floor(Math.random() * 50) + 20)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      name: '事件数量'
    },
    series: [
      {
        name: '月度事件',
        type: 'line',
        data: eventCounts,
        smooth: true,
        areaStyle: { opacity: 0.3 }
      }
    ]
  }
  
  lineChartInstance.value.setOption(option)
}

const getEventTypeName = (type: CalendarEvent['type']): string => {
  const names = {
    earnings: '财报发布',
    meeting: '股东大会',
    dividend: '分红派息',
    ipo: '新股上市',
    suspension: '停复牌',
    announcement: '重要公告'
  }
  return names[type]
}

const getTimelineType = (type: CalendarEvent['type']): string => {
  const types = {
    earnings: 'primary',
    meeting: 'success',
    dividend: 'warning',
    ipo: 'danger',
    suspension: 'info',
    announcement: 'primary'
  }
  return types[type]
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  })
}

const formatChange = (change: number): string => {
  const sign = change >= 0 ? '+' : ''
  return sign + change.toFixed(2) + '%'
}

const getChangeClass = (change: number): string => {
  return change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
}

onMounted(() => {
  loadCalendarData()
})
</script>

<style scoped>
.stock-calendar {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.calendar-overview {
  margin-bottom: 20px;
}

.overview-card {
  text-align: center;
}

.card-content {
  padding: 10px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.card-subtitle {
  font-size: 12px;
  color: #909399;
}

.calendar-container {
  margin-bottom: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-controls {
  display: flex;
  gap: 10px;
}

.calendar-cell {
  height: 100px;
  padding: 4px;
}

.date-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.events-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-item {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-earnings { background-color: #e1f3ff; color: #1890ff; }
.event-meeting { background-color: #f6ffed; color: #52c41a; }
.event-dividend { background-color: #fff7e6; color: #fa8c16; }
.event-ipo { background-color: #fff1f0; color: #f5222d; }
.event-suspension { background-color: #f0f0f0; color: #595959; }
.event-announcement { background-color: #f9f0ff; color: #722ed1; }

.list-view {
  max-height: 600px;
  overflow-y: auto;
}

.date-group {
  margin-bottom: 20px;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #e8e8e8;
}

.date-header h3 {
  margin: 0;
  color: #303133;
}

.event-count {
  color: #909399;
  font-size: 14px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.event-card {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.event-type-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.event-type-badge.large {
  padding: 4px 12px;
  font-size: 14px;
}

.event-time {
  color: #909399;
  font-size: 12px;
}

.event-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
}

.event-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.event-stocks {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.upcoming-events {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-card {
  cursor: pointer;
  transition: all 0.3s;
}

.timeline-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-content {
  padding: 8px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.event-importance {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f56c6c;
  font-size: 12px;
}

.timeline-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.timeline-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.timeline-stocks {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  align-items: center;
}

.more-stocks {
  color: #909399;
  font-size: 12px;
}

.statistics-section {
  margin-bottom: 20px;
}

.event-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.event-date {
  color: #909399;
  font-size: 14px;
}

.related-stocks h4,
.event-details h4 {
  margin: 20px 0 10px 0;
  color: #303133;
}

.stocks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.stock-item {
  padding: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.stock-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.stock-code {
  font-weight: bold;
  color: #303133;
}

.stock-name {
  color: #606266;
  font-size: 14px;
  margin: 4px 0;
}

.stock-price {
  font-weight: bold;
}

.details-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.detail-label {
  font-weight: bold;
  color: #303133;
}

.detail-value {
  color: #606266;
}

.positive {
  color: #f56c6c;
}

.negative {
  color: #67c23a;
}

.neutral {
  color: #909399;
}

.dialog-footer {
  text-align: right;
}
</style>