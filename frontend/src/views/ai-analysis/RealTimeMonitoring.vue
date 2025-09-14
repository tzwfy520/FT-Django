<template>
  <div class="real-time-monitoring">
    <div class="page-title">
      <h2>实时盯盘</h2>
      <p class="subtitle">定义实时盯盘的提示词内容和提示词格式</p>
    </div>

    <div class="content-grid">
      <!-- 主要设置区域 -->
      <div class="main-settings-row">
        <!-- 自动任务设置 -->
        <div class="setting-card">
          <div class="card-header">
            <h3>自动任务设置</h3>
            <el-switch
              v-model="autoTaskEnabled"
              @change="saveAutoTaskSettings"
              active-text="启用"
              inactive-text="禁用"
            />
          </div>
          <div class="card-body">
            <div class="form-group">
              <label>触发间隔（分钟）</label>
              <el-input-number
                v-model="autoTaskSettings.interval"
                :min="1"
                :max="60"
                @change="saveAutoTaskSettings"
              />
            </div>
            <div class="form-group">
              <el-checkbox
                v-model="autoTaskSettings.tradingDaysOnly"
                @change="saveAutoTaskSettings"
              >
                仅交易日触发
              </el-checkbox>
            </div>
            <div class="form-group">
              <el-checkbox
                v-model="autoTaskSettings.tradingHoursOnly"
                @change="saveAutoTaskSettings"
              >
                仅交易时间触发
              </el-checkbox>
            </div>
          </div>
        </div>

        <!-- 数据来源设置 -->
        <div class="setting-card">
          <div class="card-header">
            <h3>数据来源设置</h3>
            <el-button type="primary" size="small" @click="saveDataSources">
              保存
            </el-button>
          </div>
          <div class="card-body">
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.historical"
                @change="saveDataSources"
              >
                历史数据
              </el-checkbox>
              <p class="source-desc">用于对比分析和趋势判断</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.intraday"
                @change="saveDataSources"
              >
                分时数据
              </el-checkbox>
              <p class="source-desc">当日分时走势和成交量数据</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.realtime"
                @change="saveDataSources"
              >
                实时数据
              </el-checkbox>
              <p class="source-desc">最新的实时行情和交易数据</p>
            </div>

            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.orderBook"
                @change="saveDataSources"
              >
                委托数据
              </el-checkbox>
              <p class="source-desc">买卖委托队列和深度数据</p>
            </div>
          </div>
        </div>

        <!-- 监控股票设置 -->
        <div class="setting-card">
          <div class="card-header">
            <h3>监控股票设置</h3>
            <el-button type="primary" size="small" @click="saveWatchList">
              保存
            </el-button>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label>添加监控股票</label>
              <div class="add-stock-input">
                <el-input
                  v-model="newStockCode"
                  placeholder="输入股票代码"
                  @keyup.enter="addStock"
                />
                <el-button type="primary" @click="addStock">
                  添加
                </el-button>
              </div>
            </div>
            
            <div class="stock-list">
              <div
                v-for="stock in watchList"
                :key="stock.code"
                class="stock-item"
              >
                <span class="stock-code">{{ stock.code }}</span>
                <span class="stock-name">{{ stock.name }}</span>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeStock(stock.code)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分析任务要求 -->
      <div class="setting-card full-width">
        <div class="card-header">
          <h3>分析任务要求</h3>
          <el-button type="primary" size="small" @click="editTaskRequirements">
            修改
          </el-button>
        </div>
        <div class="card-body">
          <div class="readonly-content">
            <pre>{{ taskRequirements }}</pre>
          </div>
        </div>
      </div>

      <!-- 分析结果要求 -->
      <div class="setting-card full-width">
        <div class="card-header">
          <h3>分析结果要求</h3>
          <el-button type="primary" size="small" @click="editResultRequirements">
            修改
          </el-button>
        </div>
        <div class="card-body">
          <div class="readonly-content">
            <pre>{{ resultRequirements }}</pre>
          </div>
        </div>
      </div>


    </div>

    <!-- 预览和测试 -->
    <div class="action-section">
      <el-button type="success" @click="previewPrompt">
        <el-icon><View /></el-icon>
        预览提示词
      </el-button>
      <el-button type="warning" @click="testMonitoring">
        <el-icon><VideoPlay /></el-icon>
        测试监控
      </el-button>
      <el-button type="info" @click="viewMonitoringStatus">
        <el-icon><Monitor /></el-icon>
        监控状态
      </el-button>
    </div>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="提示词预览"
      width="70%"
    >
      <div class="prompt-preview">
        <h4>完整提示词内容：</h4>
        <pre class="prompt-content">{{ generatedPrompt }}</pre>
      </div>
    </el-dialog>

    <!-- 测试结果弹窗 -->
    <el-dialog
      v-model="testVisible"
      title="实时监控测试"
      width="80%"
    >
      <div class="test-result">
        <el-select
          v-model="testStockCode"
          placeholder="选择测试股票"
          style="margin-bottom: 20px; width: 200px;"
        >
          <el-option
            v-for="stock in watchList"
            :key="stock.code"
            :label="`${stock.code} ${stock.name}`"
            :value="stock.code"
          />
        </el-select>
        <el-button
          type="primary"
          @click="runTest"
          :loading="testLoading"
          style="margin-bottom: 20px; margin-left: 10px;"
        >
          开始测试
        </el-button>
        <div v-if="testResult" class="result-content">
          <h4>监控结果：</h4>
          <div v-html="formatTestResult(testResult)"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 监控状态弹窗 -->
    <el-dialog
      v-model="statusVisible"
      title="实时监控状态"
      width="70%"
    >
      <div class="monitoring-status">
        <div class="status-header">
          <el-tag :type="monitoringActive ? 'success' : 'danger'">
            {{ monitoringActive ? '监控中' : '已停止' }}
          </el-tag>
          <span class="last-update">最后更新：{{ lastUpdateTime }}</span>
        </div>
        
        <div class="stock-status-list">
          <div
            v-for="stock in monitoringStocks"
            :key="stock.code"
            class="stock-status-item"
          >
            <div class="stock-info">
              <span class="code">{{ stock.code }}</span>
              <span class="name">{{ stock.name }}</span>
              <span class="price">{{ stock.price }}</span>
              <span :class="['change', (stock.change || 0) >= 0 ? 'positive' : 'negative']">
                {{ (stock.change || 0) >= 0 ? '+' : '' }}{{ stock.change || 0 }}%
              </span>
            </div>
            <div class="alerts">
              <el-tag
                v-for="alert in stock.alerts"
                :key="alert"
                type="warning"
                size="small"
              >
                {{ alert }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑任务要求弹窗 -->
    <el-dialog
      v-model="editTaskVisible"
      title="编辑分析任务要求"
      width="70%"
    >
      <el-input
        v-model="editingTaskRequirements"
        type="textarea"
        :rows="10"
        placeholder="请输入分析任务要求..."
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editTaskVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTaskRequirements">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑结果要求弹窗 -->
    <el-dialog
      v-model="editResultVisible"
      title="编辑分析结果要求"
      width="70%"
    >
      <el-input
        v-model="editingResultRequirements"
        type="textarea"
        :rows="15"
        placeholder="请输入分析结果要求..."
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editResultVisible = false">取消</el-button>
          <el-button type="primary" @click="saveResultRequirements">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { View, VideoPlay, Monitor } from '@element-plus/icons-vue'

interface Stock {
  code: string
  name: string
  price?: number
  change?: number
  alerts?: string[]
}

// 响应式数据
const autoTaskEnabled = ref(false)
const autoTaskSettings = ref({
  interval: 5,
  tradingDaysOnly: true,
  tradingHoursOnly: true
})

const taskRequirements = ref(`请对监控股票进行实时盯盘分析，包括：
1. 实时价格监控和异常波动识别
2. 成交量异常分析
3. 大单交易监控
4. 技术指标实时计算（RSI、MACD等）
5. 支撑阻力位突破监控
6. 市场情绪和资金流向分析
7. 风险预警和交易机会识别
8. 关联股票和板块联动分析`)

const resultRequirements = ref(`# 实时盯盘监控报告

## 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_name}
- 监控时间：{monitor_time}
- 当前价格：{current_price}
- 涨跌幅：{price_change}

## 价格监控
- 价格变动：{price_movement}
- 异常波动：{abnormal_movement}
- 成交量变化：{volume_change}

## 技术信号
- RSI信号：{rsi_signal}
- MACD信号：{macd_signal}
- 突破信号：{breakout_signal}

## 大单监控
- 大买单：{large_buy_orders}
- 大卖单：{large_sell_orders}
- 资金流向：{money_flow}

## 风险提示
- 风险等级：{risk_level}
- 预警信号：{warning_signals}

## 操作建议
- 即时建议：{immediate_advice}
- 关注要点：{key_points}`)

const dataSources = ref({
  historical: true,
  intraday: true,
  realtime: true,
  orderBook: true
})

const watchList = ref<Stock[]>([
  { code: '000001', name: '平安银行' },
  { code: '000002', name: '万科A' },
  { code: '600036', name: '招商银行' }
])

const newStockCode = ref('')
const previewVisible = ref(false)
const testVisible = ref(false)
const statusVisible = ref(false)
const testLoading = ref(false)
const testStockCode = ref('')
const testResult = ref('')
const editTaskVisible = ref(false)
const editResultVisible = ref(false)
const editingTaskRequirements = ref('')
const editingResultRequirements = ref('')

const monitoringActive = ref(true)
const lastUpdateTime = ref(new Date().toLocaleString())
const monitoringStocks = ref<Stock[]>([
  {
    code: '000001',
    name: '平安银行',
    price: 12.45,
    change: 2.3,
    alerts: ['价格突破阻力位', '成交量放大']
  },
  {
    code: '000002',
    name: '万科A',
    price: 18.76,
    change: -1.2,
    alerts: ['RSI超卖']
  }
])

// 计算属性
const generatedPrompt = computed(() => {
  let prompt = '# 实时盯盘监控任务\n\n'
  prompt += '## 监控股票列表\n'
  watchList.value.forEach(stock => {
    prompt += `- ${stock.code} ${stock.name}\n`
  })
  prompt += '\n## 任务要求\n' + taskRequirements.value + '\n\n'
  prompt += '## 输出格式\n' + resultRequirements.value + '\n\n'
  prompt += '## 数据来源\n'
  
  const sources = []
  if (dataSources.value.historical) sources.push('历史数据')
  if (dataSources.value.intraday) sources.push('分时数据')
  if (dataSources.value.realtime) sources.push('实时数据')
  if (dataSources.value.orderBook) sources.push('委托数据')
  
  prompt += sources.join('、') + '\n\n'
  prompt += `## 监控设置\n- 监控间隔：${autoTaskSettings.value.interval}分钟\n`
  prompt += `- 仅交易日：${autoTaskSettings.value.tradingDaysOnly ? '是' : '否'}\n`
  prompt += `- 仅交易时间：${autoTaskSettings.value.tradingHoursOnly ? '是' : '否'}\n\n`
  prompt += '请基于以上设置进行实时盯盘监控分析。'
  
  return prompt
})

// 方法
const saveAutoTaskSettings = () => {
  localStorage.setItem('realTimeMonitoring_autoTaskSettings', JSON.stringify({
    enabled: autoTaskEnabled.value,
    settings: autoTaskSettings.value
  }))
  ElMessage.success('自动任务设置已保存')
}

const editTaskRequirements = () => {
  editingTaskRequirements.value = taskRequirements.value
  editTaskVisible.value = true
}

const editResultRequirements = () => {
  editingResultRequirements.value = resultRequirements.value
  editResultVisible.value = true
}

const saveTaskRequirements = () => {
  taskRequirements.value = editingTaskRequirements.value
  localStorage.setItem('realTimeMonitoring_taskRequirements', taskRequirements.value)
  editTaskVisible.value = false
  ElMessage.success('分析任务要求已保存')
}

const saveResultRequirements = () => {
  resultRequirements.value = editingResultRequirements.value
  localStorage.setItem('realTimeMonitoring_resultRequirements', resultRequirements.value)
  editResultVisible.value = false
  ElMessage.success('分析结果要求已保存')
}

const saveDataSources = () => {
  localStorage.setItem('realTimeMonitoring_dataSources', JSON.stringify(dataSources.value))
  ElMessage.success('数据来源设置已保存')
}

const saveWatchList = () => {
  localStorage.setItem('realTimeMonitoring_watchList', JSON.stringify(watchList.value))
  ElMessage.success('监控股票列表已保存')
}

const addStock = () => {
  if (!newStockCode.value) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  if (watchList.value.some(stock => stock.code === newStockCode.value)) {
    ElMessage.warning('股票已在监控列表中')
    return
  }
  
  // 模拟获取股票名称
  const stockNames: Record<string, string> = {
    '000001': '平安银行',
    '000002': '万科A',
    '600036': '招商银行',
    '600519': '贵州茅台',
    '000858': '五粮液'
  }
  
  watchList.value.push({
    code: newStockCode.value,
    name: stockNames[newStockCode.value] || '未知股票'
  })
  
  newStockCode.value = ''
  ElMessage.success('股票已添加到监控列表')
}

const removeStock = (code: string) => {
  const index = watchList.value.findIndex(stock => stock.code === code)
  if (index > -1) {
    watchList.value.splice(index, 1)
    ElMessage.success('股票已从监控列表移除')
  }
}

const previewPrompt = () => {
  previewVisible.value = true
}

const testMonitoring = () => {
  testVisible.value = true
  if (watchList.value.length > 0) {
    testStockCode.value = watchList.value[0].code
  }
}

const viewMonitoringStatus = () => {
  statusVisible.value = true
  // 更新监控状态
  lastUpdateTime.value = new Date().toLocaleString()
}

const runTest = async () => {
  if (!testStockCode.value) {
    ElMessage.warning('请选择测试股票')
    return
  }
  
  testLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    const stock = watchList.value.find(s => s.code === testStockCode.value)
    testResult.value = `# 实时盯盘监控报告

## 基本信息
- 股票代码：${testStockCode.value}
- 股票名称：${stock?.name || '未知'}
- 监控时间：${new Date().toLocaleString()}
- 当前价格：12.45元
- 涨跌幅：+2.3%

## 价格监控
- 价格变动：快速上涨
- 异常波动：检测到异常放量上涨
- 成交量变化：成交量较昨日同期增长150%

## 技术信号
- RSI信号：RSI(14)=72，进入超买区间
- MACD信号：MACD金叉，动能增强
- 突破信号：突破前期阻力位12.20元

## 大单监控
- 大买单：检测到多笔100万以上买单
- 大卖单：卖单相对较少
- 资金流向：净流入2000万元

## 风险提示
- 风险等级：中等
- 预警信号：技术指标进入超买区间，注意回调风险

## 操作建议
- 即时建议：可考虑适量减仓，等待回调机会
- 关注要点：关注12.20元支撑位，成交量是否持续放大`
  } catch (error) {
    ElMessage.error('测试监控失败')
  } finally {
    testLoading.value = false
  }
}

const formatTestResult = (result: string) => {
  return result.replace(/\n/g, '<br>').replace(/# (.*)/g, '<h3>$1</h3>').replace(/## (.*)/g, '<h4>$1</h4>')
}

const loadSettings = () => {
  const autoTaskData = localStorage.getItem('realTimeMonitoring_autoTaskSettings')
  if (autoTaskData) {
    const data = JSON.parse(autoTaskData)
    autoTaskEnabled.value = data.enabled
    autoTaskSettings.value = data.settings
  }
  
  const taskReq = localStorage.getItem('realTimeMonitoring_taskRequirements')
  if (taskReq) {
    taskRequirements.value = taskReq
  }
  
  const resultReq = localStorage.getItem('realTimeMonitoring_resultRequirements')
  if (resultReq) {
    resultRequirements.value = resultReq
  }
  
  const dataSourcesData = localStorage.getItem('realTimeMonitoring_dataSources')
  if (dataSourcesData) {
    dataSources.value = JSON.parse(dataSourcesData)
  }
  
  const watchListData = localStorage.getItem('realTimeMonitoring_watchList')
  if (watchListData) {
    watchList.value = JSON.parse(watchListData)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.real-time-monitoring {
  padding: 20px;
}

.page-title {
  margin-bottom: 30px;
}

.page-title h2 {
  color: #2c3e50;
  margin-bottom: 8px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.main-settings-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.setting-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.setting-card.full-width {
  width: 100%;
}

.readonly-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  min-height: 120px;
}

.readonly-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: #495057;
}

.card-header {
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.card-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.data-source-group {
  margin-bottom: 16px;
}

.source-desc {
  margin: 4px 0 0 24px;
  color: #7f8c8d;
  font-size: 12px;
}

.add-stock-input {
  display: flex;
  gap: 10px;
}

.stock-list {
  max-height: 200px;
  overflow-y: auto;
}

.stock-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stock-code {
  font-weight: bold;
  color: #2c3e50;
  min-width: 80px;
}

.stock-name {
  flex: 1;
  margin-left: 10px;
  color: #7f8c8d;
}

.action-section {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.prompt-preview {
  max-height: 60vh;
  overflow-y: auto;
}

.prompt-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.test-result {
  max-height: 60vh;
  overflow-y: auto;
}

.result-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
}

.monitoring-status {
  max-height: 60vh;
  overflow-y: auto;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.last-update {
  color: #7f8c8d;
  font-size: 14px;
}

.stock-status-item {
  padding: 15px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 10px;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.stock-info .code {
  font-weight: bold;
  color: #2c3e50;
}

.stock-info .name {
  color: #7f8c8d;
}

.stock-info .price {
  font-weight: bold;
  font-size: 16px;
}

.stock-info .change.positive {
  color: #e74c3c;
}

.stock-info .change.negative {
  color: #27ae60;
}

.alerts {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-settings-row {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
  
  .add-stock-input {
    flex-direction: column;
  }
  
  .stock-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>