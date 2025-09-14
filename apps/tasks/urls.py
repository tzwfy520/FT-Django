from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # 任务定义管理
    path('definitions/', views.TaskDefinitionView.as_view(), name='task_definitions'),
    
    # 任务执行记录
    path('executions/', views.TaskExecutionView.as_view(), name='task_executions'),
    
    # 任务调度管理
    path('schedules/', views.TaskScheduleView.as_view(), name='task_schedules'),
    
    # 任务控制（停止、重启等）
    path('control/', views.TaskControlView.as_view(), name='task_control'),
    
    # 任务统计
    path('stats/', views.task_stats, name='task_stats'),
]