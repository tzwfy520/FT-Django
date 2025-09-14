<template>
  <div class="ai-analysis">
    <div class="page-header">
      <h1>AI分析</h1>
      <p class="text-muted">智能股票分析与任务管理</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 子路由内容 -->
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// AI分析主页面，包含子路由
</script>

<style scoped>
.ai-analysis {
  padding: 24px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.page-header h1 {
  color: white;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 2rem;
}

.page-header p {
  margin-bottom: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.main-content {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-analysis {
    padding: 16px;
  }
  
  .page-header {
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
}
</style>