<template>
  <div class="stock-recommendation">
    <div class="page-title">
      <h2>股票推荐</h2>
      <p class="subtitle">定义股票推荐的提示词内容和提示词格式</p>
    </div>

    <div class="content-grid">
      <!-- 主要设置行 -->
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
              <label>定时触发时间</label>
              <el-time-picker
                v-model="autoTaskSettings.triggerTime"
                format="HH:mm"
                placeholder="选择触发时间"
                @change="saveAutoTaskSettings"
              />
            </div>
            <div class="form-group">
              <label>推荐频率</label>
              <el-select
                v-model="autoTaskSettings.frequency"
                @change="saveAutoTaskSettings"
              >
                <el-option label="每日" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
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
              <label>推荐数量</label>
              <el-input-number
                v-model="autoTaskSettings.recommendCount"
                :min="1"
                :max="20"
                @change="saveAutoTaskSettings"
              />
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
              <p class="source-desc">股票历史价格和成交量数据</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.financial"
                @change="saveDataSources"
              >
                财务数据
              </el-checkbox>
              <p class="source-desc">财务报表、业绩指标等基本面数据</p>
            </div>
            
            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.realtime"
                @change="saveDataSources"
              >
                实时数据
              </el-checkbox>
              <p class="source-desc">最新的市场行情和交易数据</p>
            </div>

            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.news"
                @change="saveDataSources"
              >
                新闻资讯
              </el-checkbox>
              <p class="source-desc">相关新闻、公告和市场资讯</p>
            </div>

            <div class="data-source-group">
              <el-checkbox
                v-model="dataSources.analyst"
                @change="saveDataSources"
              >
                分析师报告
              </el-checkbox>
              <p class="source-desc">券商研报和分析师评级</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 推荐策略设置 -->
      <div class="setting-card">
        <div class="card-header">
          <h3>推荐策略设置</h3>
          <el-button type="primary" size="small" @click="saveStrategy">
            保存
          </el-button>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label>投资风格</label>
            <el-checkbox-group v-model="strategy.investmentStyle">
              <el-checkbox label="value">价值投资</el-checkbox>
              <el-checkbox label="growth">成长投资</el-checkbox>
              <el-checkbox label="momentum">动量投资</el-checkbox>
              <el-checkbox label="dividend">股息投资</el-checkbox>
            </el-checkbox-group>
          </div>
          
          <div class="form-group">
            <label>市值偏好</label>
            <el-checkbox-group v-model="strategy.marketCap">
              <el-checkbox label="large">大盘股</el-checkbox>
              <el-checkbox label="mid">中盘股</el-checkbox>
              <el-checkbox label="small">小盘股</el-checkbox>
            </el-checkbox-group>
          </div>
          
          <div class="form-group">
            <label>行业偏好</label>
            <el-select
              v-model="strategy.industries"
              multiple
              placeholder="选择关注行业"
            >
              <el-option label="科技" value="technology" />
              <el-option label="金融" value="finance" />
              <el-option label="医药" value="healthcare" />
              <el-option label="消费" value="consumer" />
              <el-option label="制造" value="manufacturing" />
              <el-option label="能源" value="energy" />
              <el-option label="房地产" value="realestate" />
            </el-select>
          </div>
          
          <div class="form-group">
            <label>风险偏好</label>
            <el-radio-group v-model="strategy.riskLevel">
              <el-radio label="conservative">保守型</el-radio>
              <el-radio label="moderate">稳健型</el-radio>
              <el-radio label="aggressive">激进型</el-radio>
            </el-radio-group>
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
            <pre class="content-preview">{{ taskRequirements }}</pre>
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
            <pre class="content-preview">{{ resultRequirements }}</pre>
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
      <el-button type="warning" @click="testRecommendation">
        <el-icon><VideoPlay /></el-icon>
        测试推荐
      </el-button>
      <el-button type="info" @click="viewRecommendationHistory">
        <el-icon><Document /></el-icon>
        推荐历史
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
      title="股票推荐测试"
      width="80%"
    >
      <div class="test-result">
        <div class="test-controls">
          <el-button
            type="primary"
            @click="runTest"
            :loading="testLoading"
            style="margin-bottom: 20px;"
          >
            生成推荐
          </el-button>
        </div>
        <div v-if="testResult" class="result-content">
          <h4>推荐结果：</h4>
          <div v-html="formatTestResult(testResult)"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 推荐历史弹窗 -->
    <el-dialog
      v-model="historyVisible"
      title="推荐历史记录"
      width="80%"
    >
      <div class="recommendation-history">
        <div class="history-filters">
          <el-date-picker
            v-model="historyDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="margin-bottom: 20px;"
          />
        </div>
        
        <div class="history-list">
          <div
            v-for="record in recommendationHistory"
            :key="record.id"
            class="history-item"
          >
            <div class="history-header">
              <span class="date">{{ record.date }}</span>
              <el-tag :type="getPerformanceType(record.performance)">
                {{ record.performance }}%
              </el-tag>
            </div>
            <div class="recommended-stocks">
              <el-tag
                v-for="stock in record.stocks"
                :key="stock.code"
                class="stock-tag"
              >
                {{ stock.code }} {{ stock.name }}
              </el-tag>
            </div>
            <div class="recommendation-summary">
              {{ record.summary }}
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
        v-model="tempTaskRequirements"
        type="textarea"
        :rows="12"
        placeholder="请输入分析任务的具体要求..."
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
        v-model="tempResultRequirements"
        type="textarea"
        :rows="15"
        placeholder="请输入分析结果的格式要求..."
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
import { View, VideoPlay, Document } from '@element-plus/icons-vue'

interface Stock {
  code: string
  name: string
}

interface RecommendationRecord {
  id: string
  date: string
  stocks: Stock[]
  performance: number
  summary: string
}

// 响应式数据
const autoTaskEnabled = ref(false)
const autoTaskSettings = ref({
  triggerTime: null,
  frequency: 'daily',
  tradingDaysOnly: true,
  recommendCount: 5
})

const editTaskVisible = ref(false)
const editResultVisible = ref(false)
const tempTaskRequirements = ref('')
const tempResultRequirements = ref('')

const strategy = ref({
  investmentStyle: ['value', 'growth'],
  marketCap: ['large', 'mid'],
  industries: ['technology', 'finance'],
  riskLevel: 'moderate'
})

const taskRequirements = ref(`请基于以下要求进行股票推荐分析：
1. 财务指标筛选：
   - ROE > 15%，ROA > 8%
   - 净利润增长率 > 20%
   - 负债率 < 60%
   - 流动比率 > 1.5

2. 技术指标分析：
   - 股价处于上升趋势
   - RSI在30-70之间
   - MACD呈现金叉信号

3. 基本面分析：
   - 行业景气度较高
   - 公司竞争优势明显
   - 管理层稳定且执行力强

4. 估值分析：
   - PE低于行业平均水平
   - PB < 3
   - 股息率 > 2%

5. 风险评估：
   - 避免ST股票
   - 排除重大诉讼风险
   - 关注政策风险影响`)

const resultRequirements = ref(`# 股票推荐报告

## 推荐概述
- 推荐日期：{recommendation_date}
- 推荐策略：{strategy_type}
- 推荐数量：{stock_count}只
- 预期收益：{expected_return}

## 推荐股票列表

### 1. {stock_code_1} - {stock_name_1}
- 当前价格：{current_price_1}
- 目标价格：{target_price_1}
- 预期涨幅：{expected_gain_1}
- 推荐理由：{reason_1}
- 风险提示：{risk_1}

### 2. {stock_code_2} - {stock_name_2}
- 当前价格：{current_price_2}
- 目标价格：{target_price_2}
- 预期涨幅：{expected_gain_2}
- 推荐理由：{reason_2}
- 风险提示：{risk_2}

## 投资逻辑
### 宏观环境
{macro_environment}

### 行业分析
{industry_analysis}

### 选股逻辑
{stock_selection_logic}

## 风险提示
- 市场风险：{market_risk}
- 个股风险：{individual_risk}
- 政策风险：{policy_risk}

## 操作建议
- 建仓时机：{entry_timing}
- 仓位配置：{position_allocation}
- 止盈止损：{profit_loss_strategy}`)

const dataSources = ref({
  historical: true,
  financial: true,
  realtime: true,
  news: true,
  analyst: false
})

const previewVisible = ref(false)
const testVisible = ref(false)
const historyVisible = ref(false)
const testLoading = ref(false)
const testResult = ref('')
const historyDateRange = ref<[Date, Date] | null>(null)

const recommendationHistory = ref<RecommendationRecord[]>([
  {
    id: '1',
    date: '2024-01-15',
    stocks: [
      { code: '000001', name: '平安银行' },
      { code: '600036', name: '招商银行' },
      { code: '000858', name: '五粮液' }
    ],
    performance: 12.5,
    summary: '金融板块表现优异，消费股稳健增长'
  },
  {
    id: '2',
    date: '2024-01-08',
    stocks: [
      { code: '000002', name: '万科A' },
      { code: '600519', name: '贵州茅台' }
    ],
    performance: -3.2,
    summary: '地产调控影响，白酒股承压'
  }
])

// 计算属性
const generatedPrompt = computed(() => {
  let prompt = '# 股票推荐分析任务\n\n'
  
  prompt += '## 推荐策略\n'
  prompt += `- 投资风格：${strategy.value.investmentStyle.join('、')}\n`
  prompt += `- 市值偏好：${strategy.value.marketCap.join('、')}\n`
  prompt += `- 行业偏好：${strategy.value.industries.join('、')}\n`
  prompt += `- 风险偏好：${strategy.value.riskLevel}\n`
  prompt += `- 推荐数量：${autoTaskSettings.value.recommendCount}只\n\n`
  
  prompt += '## 任务要求\n' + taskRequirements.value + '\n\n'
  prompt += '## 输出格式\n' + resultRequirements.value + '\n\n'
  prompt += '## 数据来源\n'
  
  const sources = []
  if (dataSources.value.historical) sources.push('历史数据')
  if (dataSources.value.financial) sources.push('财务数据')
  if (dataSources.value.realtime) sources.push('实时数据')
  if (dataSources.value.news) sources.push('新闻资讯')
  if (dataSources.value.analyst) sources.push('分析师报告')
  
  prompt += sources.join('、') + '\n\n'
  prompt += '请基于以上策略和要求，生成股票推荐报告。'
  
  return prompt
})

// 方法
const saveAutoTaskSettings = () => {
  localStorage.setItem('stockRecommendation_autoTaskSettings', JSON.stringify({
    enabled: autoTaskEnabled.value,
    settings: autoTaskSettings.value
  }))
  ElMessage.success('自动任务设置已保存')
}

const saveStrategy = () => {
  localStorage.setItem('stockRecommendation_strategy', JSON.stringify(strategy.value))
  ElMessage.success('推荐策略已保存')
}

const editTaskRequirements = () => {
  tempTaskRequirements.value = taskRequirements.value
  editTaskVisible.value = true
}

const editResultRequirements = () => {
  tempResultRequirements.value = resultRequirements.value
  editResultVisible.value = true
}

const saveTaskRequirements = () => {
  taskRequirements.value = tempTaskRequirements.value
  localStorage.setItem('stockRecommendation_taskRequirements', taskRequirements.value)
  editTaskVisible.value = false
  ElMessage.success('分析任务要求已保存')
}

const saveResultRequirements = () => {
  resultRequirements.value = tempResultRequirements.value
  localStorage.setItem('stockRecommendation_resultRequirements', resultRequirements.value)
  editResultVisible.value = false
  ElMessage.success('分析结果要求已保存')
}

const saveDataSources = () => {
  localStorage.setItem('stockRecommendation_dataSources', JSON.stringify(dataSources.value))
  ElMessage.success('数据来源设置已保存')
}

const previewPrompt = () => {
  previewVisible.value = true
}

const testRecommendation = () => {
  testVisible.value = true
}

const viewRecommendationHistory = () => {
  historyVisible.value = true
}

const runTest = async () => {
  testLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 3000))
    testResult.value = `# 股票推荐报告

## 推荐概述
- 推荐日期：${new Date().toLocaleDateString()}
- 推荐策略：价值成长混合策略
- 推荐数量：5只
- 预期收益：15-25%

## 推荐股票列表

### 1. 000001 - 平安银行
- 当前价格：12.45元
- 目标价格：15.00元
- 预期涨幅：20.5%
- 推荐理由：ROE达18%，净利润增长22%，估值合理
- 风险提示：利率政策变化风险

### 2. 600036 - 招商银行
- 当前价格：42.80元
- 目标价格：50.00元
- 预期涨幅：16.8%
- 推荐理由：零售银行龙头，资产质量优秀
- 风险提示：经济下行影响资产质量

### 3. 000858 - 五粮液
- 当前价格：168.50元
- 目标价格：200.00元
- 预期涨幅：18.7%
- 推荐理由：品牌价值突出，渠道改革成效显著
- 风险提示：消费降级影响高端白酒需求

### 4. 002415 - 海康威视
- 当前价格：35.20元
- 目标价格：42.00元
- 预期涨幅：19.3%
- 推荐理由：AI+安防龙头，技术护城河深厚
- 风险提示：国际贸易摩擦影响海外业务

### 5. 300750 - 宁德时代
- 当前价格：185.60元
- 目标价格：220.00元
- 预期涨幅：18.5%
- 推荐理由：新能源汽车产业链核心，全球竞争力强
- 风险提示：原材料价格波动，竞争加剧

## 投资逻辑
### 宏观环境
经济复苏趋势明确，政策支持力度加大，流动性保持合理充裕

### 行业分析
金融、消费、科技板块估值合理，具备配置价值

### 选股逻辑
选择基本面扎实、估值合理、成长性良好的优质公司

## 风险提示
- 市场风险：系统性风险导致整体下跌
- 个股风险：公司经营不及预期
- 政策风险：相关政策变化影响

## 操作建议
- 建仓时机：分批建仓，逢低加仓
- 仓位配置：单只股票不超过20%
- 止盈止损：止盈25%，止损-10%`
  } catch (error) {
    ElMessage.error('测试推荐失败')
  } finally {
    testLoading.value = false
  }
}

const formatTestResult = (result: string) => {
  return result.replace(/\n/g, '<br>').replace(/# (.*)/g, '<h3>$1</h3>').replace(/## (.*)/g, '<h4>$1</h4>').replace(/### (.*)/g, '<h5>$1</h5>')
}

const getPerformanceType = (performance: number) => {
  if (performance > 10) return 'success'
  if (performance > 0) return 'warning'
  return 'danger'
}

const loadSettings = () => {
  const autoTaskData = localStorage.getItem('stockRecommendation_autoTaskSettings')
  if (autoTaskData) {
    const data = JSON.parse(autoTaskData)
    autoTaskEnabled.value = data.enabled
    autoTaskSettings.value = data.settings
  }
  
  const strategyData = localStorage.getItem('stockRecommendation_strategy')
  if (strategyData) {
    strategy.value = JSON.parse(strategyData)
  }
  
  const taskReq = localStorage.getItem('stockRecommendation_taskRequirements')
  if (taskReq) {
    taskRequirements.value = taskReq
  }
  
  const resultReq = localStorage.getItem('stockRecommendation_resultRequirements')
  if (resultReq) {
    resultRequirements.value = resultReq
  }
  
  const dataSourcesData = localStorage.getItem('stockRecommendation_dataSources')
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
.stock-recommendation {
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
  grid-template-columns: 1fr 1fr;
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

.readonly-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  min-height: 120px;
}

.content-preview {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #2c3e50;
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

.recommendation-history {
  max-height: 60vh;
  overflow-y: auto;
}

.history-filters {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.history-item {
  padding: 15px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 15px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.history-header .date {
  font-weight: bold;
  color: #2c3e50;
}

.recommended-stocks {
  margin-bottom: 10px;
}

.stock-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.recommendation-summary {
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-settings-row {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
  
  .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>