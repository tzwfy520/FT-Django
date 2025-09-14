from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .enhanced_views import (
    TaskCategoryViewSet, TaskDefinitionViewSet, TaskExecutionViewSet,
    TaskLogViewSet, TaskDependencyViewSet, TaskScheduleViewSet, TaskMetricsViewSet
)

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'categories', TaskCategoryViewSet, basename='task-category')
router.register(r'definitions', TaskDefinitionViewSet, basename='task-definition')
router.register(r'executions', TaskExecutionViewSet, basename='task-execution')
router.register(r'logs', TaskLogViewSet, basename='task-log')
router.register(r'dependencies', TaskDependencyViewSet, basename='task-dependency')
router.register(r'schedules', TaskScheduleViewSet, basename='task-schedule')
router.register(r'metrics', TaskMetricsViewSet, basename='task-metrics')

# URL配置
urlpatterns = [
    # API路由
    path('api/v1/tasks/', include(router.urls)),
    
    # 额外的自定义路由可以在这里添加
    # path('api/v1/tasks/custom-endpoint/', custom_view, name='custom-endpoint'),
]

# 为了方便调试，添加路由列表
app_name = 'tasks'

# 路由说明文档
"""
任务管理API路由说明：

1. 任务分类管理 (categories/)
   - GET /api/v1/tasks/categories/ - 获取分类列表
   - POST /api/v1/tasks/categories/ - 创建分类
   - GET /api/v1/tasks/categories/{id}/ - 获取分类详情
   - PUT /api/v1/tasks/categories/{id}/ - 更新分类
   - DELETE /api/v1/tasks/categories/{id}/ - 删除分类
   - GET /api/v1/tasks/categories/{id}/tasks/ - 获取分类下的任务

2. 任务定义管理 (definitions/)
   - GET /api/v1/tasks/definitions/ - 获取任务列表
   - POST /api/v1/tasks/definitions/ - 创建任务
   - GET /api/v1/tasks/definitions/{id}/ - 获取任务详情
   - PUT /api/v1/tasks/definitions/{id}/ - 更新任务
   - DELETE /api/v1/tasks/definitions/{id}/ - 删除任务
   - POST /api/v1/tasks/definitions/{id}/execute/ - 手动执行任务
   - POST /api/v1/tasks/definitions/{id}/toggle_status/ - 切换任务状态
   - GET /api/v1/tasks/definitions/{id}/executions/ - 获取任务执行记录
   - GET /api/v1/tasks/definitions/{id}/dependencies/ - 获取任务依赖关系
   - GET /api/v1/tasks/definitions/{id}/metrics/ - 获取任务执行指标

3. 任务执行记录管理 (executions/)
   - GET /api/v1/tasks/executions/ - 获取执行记录列表
   - GET /api/v1/tasks/executions/{id}/ - 获取执行记录详情
   - POST /api/v1/tasks/executions/{id}/retry/ - 重试任务
   - POST /api/v1/tasks/executions/{id}/cancel/ - 取消任务
   - GET /api/v1/tasks/executions/{id}/logs/ - 获取执行日志
   - GET /api/v1/tasks/executions/stats/ - 获取执行统计
   - POST /api/v1/tasks/executions/bulk_retry/ - 批量重试任务

4. 任务日志管理 (logs/)
   - GET /api/v1/tasks/logs/ - 获取日志列表
   - GET /api/v1/tasks/logs/{id}/ - 获取日志详情

5. 任务依赖关系管理 (dependencies/)
   - GET /api/v1/tasks/dependencies/ - 获取依赖关系列表
   - POST /api/v1/tasks/dependencies/ - 创建依赖关系
   - GET /api/v1/tasks/dependencies/{id}/ - 获取依赖关系详情
   - PUT /api/v1/tasks/dependencies/{id}/ - 更新依赖关系
   - DELETE /api/v1/tasks/dependencies/{id}/ - 删除依赖关系

6. 任务调度配置管理 (schedules/)
   - GET /api/v1/tasks/schedules/ - 获取调度配置列表
   - POST /api/v1/tasks/schedules/ - 创建调度配置
   - GET /api/v1/tasks/schedules/{id}/ - 获取调度配置详情
   - PUT /api/v1/tasks/schedules/{id}/ - 更新调度配置
   - DELETE /api/v1/tasks/schedules/{id}/ - 删除调度配置
   - POST /api/v1/tasks/schedules/{id}/toggle_active/ - 切换调度状态

7. 任务执行指标管理 (metrics/)
   - GET /api/v1/tasks/metrics/ - 获取指标列表
   - GET /api/v1/tasks/metrics/{id}/ - 获取指标详情

查询参数说明：
- page: 页码
- page_size: 每页数量
- search: 搜索关键词
- ordering: 排序字段
- 各种过滤参数（根据具体模型字段）

响应格式：
- 列表接口返回分页数据
- 详情接口返回单个对象数据
- 操作接口返回操作结果消息
"""