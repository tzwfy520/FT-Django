from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # AI模型管理
    path('models/', views.AIModelListView.as_view(), name='model_list'),
    
    # AI分析
    path('analysis/', views.AIAnalysisView.as_view(), name='analysis'),
    
    # AI对话
    path('conversation/', views.AIConversationView.as_view(), name='conversation'),
    
    # 分析模板
    path('templates/', views.AITemplateView.as_view(), name='templates'),
    
    # AI统计
    path('stats/', views.ai_stats, name='ai_stats'),
]