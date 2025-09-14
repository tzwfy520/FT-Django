from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    # 系统配置管理
    path('config/', views.SystemConfigView.as_view(), name='system_config'),
    
    # 数据源管理
    path('datasources/', views.DataSourceView.as_view(), name='data_sources'),
    path('datasources/<int:source_id>/password/', views.DataSourcePasswordView.as_view(), name='datasource_password'),
    path('datasources/<int:source_id>/mysql-tables/', views.MySQLTablesView.as_view(), name='mysql_tables'),
    path('datasources/<int:source_id>/mysql-tables/<str:table_name>/structure/', views.MySQLTableStructureView.as_view(), name='mysql_table_structure'),
    
    # 系统日志
    path('logs/', views.SystemLogView.as_view(), name='system_logs'),
    
    # 系统监控
    path('monitor/', views.system_monitor, name='system_monitor'),
    
    # 系统统计
    path('stats/', views.system_stats, name='system_stats'),
    
    # 系统测试
    path('test/', views.SystemTestView.as_view(), name='system_test'),
]