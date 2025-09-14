<template>
  <div class="api-management">
    <div class="page-header">
      <h1>接口管理</h1>
      <p class="text-muted">管理AI推理接口配置和调用</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 子路由内容 -->
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// 不再需要直接导入组件，使用路由来处理
</script>

<style scoped>
.api-management {
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

.card {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  border-radius: 12px 12px 0 0 !important;
  font-weight: 600;
}



/* 响应式设计 */
@media (max-width: 768px) {
  .api-management {
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