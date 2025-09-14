<template>
  <div class="stock-review">
    <div class="page-title">
      <h2>股票复盘</h2>
      <p class="subtitle">定义股票复盘的提示词内容和提示词格式</p>
    </div>

    <div class="content-grid">
      <!-- 第一行：自动任务设置和数据源设置 -->
      <div class="settings-row">
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
              <label>定时触发时间</label>
              <el-time-picker
                v-model="autoTaskSettings.triggerTime"
                format="HH:mm"
                placeholder="选择触发时间"
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
              <p class="source-desc">包含股票的历史价格、成交量等数据</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.intraday"
                @change="saveDataSources"
              >
              分时数据
              </el-checkbox>
              <p class="source-desc">包含当日的分时价格和成交量数据</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.realtime"
                @change="saveDataSources"
              >
                实时数据
              </el-checkbox>
              <p class="source-desc">包含最新的实时行情数据</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：分析任务要求 -->
      <div class="task-row">
        <div class="setting-card full-width">
          <div class="card-header">
            <h3>分析任务要求</h3>
            <el-button type="primary" size="small" @click="editTaskRequirements">
              修改
            </el-button>
          </div>
          <div class="card-body">
            <div class="readonly-content">
              <pre class="content-display">{{ taskRequirements }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- 第三行：分析结果要求 -->
      <div class="result-row">
        <div class="setting-card full-width">
          <div class="card-header">
            <h3>分析结果要求</h3>
            <el-button type="primary" size="small" @click="editResultRequirements">
              修改
            </el-button>
          </div>
          <div class="card-body">
            <div class="readonly-content">
              <pre class="content-display">{{ resultRequirements }}</pre>
            </div>
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
      <el-button type="warning" @click="testAnalysis">
        <el-icon><VideoPlay /></el-icon>
        测试分析
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
      title="测试分析结果"
      width="80%"
    >
      <div class="test-result">
        <el-input
          v-model="testStockCode"
          placeholder="请输入测试股票代码"
          style="margin-bottom: 20px;"
        />
        <el-button
          type="primary"
          @click="runTest"
          :loading="testLoading"
          style="margin-bottom: 20px;"
        >
          开始测试
        </el-button>
        <div v-if="testResult" class="result-content">
          <h4>分析结果：</h4>
          <div v-html="formatTestResult(testResult)"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑任务要求弹窗 -->
    <el-dialog
      v-model="taskRequirementsDialogVisible"
      title="编辑分析任务要求"
      width="70%"
    >
      <el-input
        v-model="tempTaskRequirements"
        type="textarea"
        :rows="12"
        placeholder="请定义AI分析的任务要求"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskRequirementsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTaskRequirements">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑结果要求弹窗 -->
    <el-dialog
      v-model="resultRequirementsDialogVisible"
      title="编辑分析结果要求"
      width="70%"
    >
      <el-input
        v-model="tempResultRequirements"
        type="textarea"
        :rows="12"
        placeholder="请定义AI分析的输出格式"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resultRequirementsDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveResultRequirements">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { View, VideoPlay } from '@element-plus/icons-vue'

// 响应式数据
const autoTaskEnabled = ref(false)
const autoTaskSettings = ref({
  triggerTime: null,
  tradingDaysOnly: true
})

const taskRequirements = ref(`请对指定股票进行全面的复盘分析，包括：
1. 技术指标分析（RSI、MACD、KDJ、布林带等）
2. 价格走势分析（支撑位、阻力位、趋势线）
3. 成交量分析
4. 市场情绪分析
5. 基本面因素影响
6. 风险评估
7. 后市展望和操作建议`)

const resultRequirements = ref(`# 股票复盘分析报告

## 基本信息
- 股票代码：{stock_code}
- 股票名称：{stock_name}
- 分析日期：{analysis_date}
- 当前价格：{current_price}

## 技术分析
### 技术指标
- RSI(14)：{rsi_value} - {rsi_signal}
- MACD：{macd_value} - {macd_signal}
- KDJ：{kdj_value} - {kdj_signal}
- 布林带：{bollinger_position}

### 价格走势
- 主要趋势：{main_trend}
- 支撑位：{support_level}
- 阻力位：{resistance_level}

## 成交量分析
- 成交量趋势：{volume_trend}
- 量价关系：{price_volume_relation}

## 风险评估
- 风险等级：{risk_level}
- 主要风险：{main_risks}

## 投资建议
- 操作建议：{operation_advice}
- 目标价位：{target_price}
- 止损位：{stop_loss}`)

const dataSources = ref({
  historical: true,
  intraday: true,
  realtime: false
})

const previewVisible = ref(false)
const testVisible = ref(false)
const testLoading = ref(false)
const testStockCode = ref('')
const testResult = ref('')

// 弹窗相关
const taskRequirementsDialogVisible = ref(false)
const resultRequirementsDialogVisible = ref(false)
const tempTaskRequirements = ref('')
const tempResultRequirements = ref('')

// 计算属性
const generatedPrompt = computed(() => {
  let prompt = '# 股票复盘分析任务\n\n'
  prompt += '## 任务要求\n' + taskRequirements.value + '\n\n'
  prompt += '## 输出格式\n' + resultRequirements.value + '\n\n'
  prompt += '## 数据来源\n'
  
  const sources = []
  if (dataSources.value.historical) sources.push('历史数据')
  if (dataSources.value.intraday) sources.push('分时数据')
  if (dataSources.value.realtime) sources.push('实时数据')
  
  prompt += sources.join('、') + '\n\n'
  prompt += '请基于以上要求和数据来源，对股票进行详细的复盘分析。'
  
  return prompt
})

// 方法
const saveAutoTaskSettings = () => {
  // 保存自动任务设置到后端
  localStorage.setItem('stockReview_autoTaskSettings', JSON.stringify({
    enabled: autoTaskEnabled.value,
    settings: autoTaskSettings.value
  }))
  ElMessage.success('自动任务设置已保存')
}

const editTaskRequirements = () => {
  tempTaskRequirements.value = taskRequirements.value
  taskRequirementsDialogVisible.value = true
}

const editResultRequirements = () => {
  tempResultRequirements.value = resultRequirements.value
  resultRequirementsDialogVisible.value = true
}

const saveTaskRequirements = () => {
  taskRequirements.value = tempTaskRequirements.value
  localStorage.setItem('stockReview_taskRequirements', taskRequirements.value)
  taskRequirementsDialogVisible.value = false
  ElMessage.success('分析任务要求已保存')
}

const saveResultRequirements = () => {
  resultRequirements.value = tempResultRequirements.value
  localStorage.setItem('stockReview_resultRequirements', resultRequirements.value)
  resultRequirementsDialogVisible.value = false
  ElMessage.success('分析结果要求已保存')
}

const saveDataSources = () => {
  localStorage.setItem('stockReview_dataSources', JSON.stringify(dataSources.value))
  ElMessage.success('数据来源设置已保存')
}

const previewPrompt = () => {
  previewVisible.value = true
}

const testAnalysis = () => {
  testVisible.value = true
  testStockCode.value = '000001' // 默认测试股票
}

const runTest = async () => {
  if (!testStockCode.value) {
    ElMessage.warning('请输入股票代码')
    return
  }
  
  testLoading.value = true
  try {
    // 模拟测试分析
    await new Promise(resolve => setTimeout(resolve, 2000))
    testResult.value = `# 股票复盘分析报告

## 基本信息
- 股票代码：${testStockCode.value}
- 股票名称：平安银行
- 分析日期：${new Date().toLocaleDateString()}
- 当前价格：12.45元

## 技术分析
### 技术指标
- RSI(14)：65.2 - 偏强势
- MACD：0.15 - 金叉向上
- KDJ：K=72, D=68, J=80 - 超买区间
- 布林带：价格位于中轨上方

### 价格走势
- 主要趋势：短期上涨趋势
- 支撑位：11.80元
- 阻力位：13.20元

## 成交量分析
- 成交量趋势：放量上涨
- 量价关系：量价配合良好

## 风险评估
- 风险等级：中等
- 主要风险：技术指标进入超买区间

## 投资建议
- 操作建议：短期持有，关注回调机会
- 目标价位：13.00元
- 止损位：11.50元`
  } catch (error) {
    ElMessage.error('测试分析失败')
  } finally {
    testLoading.value = false
  }
}

const formatTestResult = (result: string) => {
  return result.replace(/\n/g, '<br>').replace(/# (.*)/g, '<h3>$1</h3>').replace(/## (.*)/g, '<h4>$1</h4>')
}

const loadSettings = () => {
  // 加载保存的设置
  const autoTaskData = localStorage.getItem('stockReview_autoTaskSettings')
  if (autoTaskData) {
    const data = JSON.parse(autoTaskData)
    autoTaskEnabled.value = data.enabled
    autoTaskSettings.value = data.settings
  }
  
  const taskReq = localStorage.getItem('stockReview_taskRequirements')
  if (taskReq) {
    taskRequirements.value = taskReq
  }
  
  const resultReq = localStorage.getItem('stockReview_resultRequirements')
  if (resultReq) {
    resultRequirements.value = resultReq
  }
  
  const dataSourcesData = localStorage.getItem('stockReview_dataSources')
  if (dataSourcesData) {
    dataSources.value = JSON.parse(dataSourcesData)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.stock-review {
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
  gap: 24px;
  margin-bottom: 24px;
}

.settings-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.task-row,
.result-row {
  display: flex;
  width: 100%;
}

.task-row .setting-card,
.result-row .setting-card {
  width: 100%;
}

.setting-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.readonly-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  min-height: 120px;
}

.content-display {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-row {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>