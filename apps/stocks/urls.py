from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    # 股票列表和搜索
    path('list/', views.StockListView.as_view(), name='stock_list'),
    
    # 股票基本信息
    path('basic-info/', views.StockBasicInfoView.as_view(), name='stock_basic_info'),
    
    # 股票概览
    path('overview/', views.StockOverviewView.as_view(), name='stock_overview'),
    
    # 实时数据
    path('realtime/', views.StockRealTimeDataView.as_view(), name='realtime_data'),
    path('realtime/<str:stock_code>/', views.StockRealTimeDataView.as_view(), name='realtime_data_detail'),
    
    # 历史交易数据（前复权）- 必须放在通用历史数据路由之前
    path('history/daily/', views.StockDailyHistoryView.as_view(), name='daily_history'),
    path('history/weekly/', views.StockWeeklyHistoryView.as_view(), name='weekly_history'),
    path('history/monthly/', views.StockMonthlyHistoryView.as_view(), name='monthly_history'),
    
    # 历史数据（通用）
    path('history/', views.StockHistoryDataView.as_view(), name='history_data'),
    path('history/<str:stock_code>/', views.StockHistoryDataView.as_view(), name='history_data_detail'),
    
    # 市场指数
    path('market/', views.MarketIndexView.as_view(), name='market_index'),
    
    # 股票搜索
    path('search/', views.StockSearchView.as_view(), name='stock_search'),
    
    # 统计信息
    path('stats/', views.stock_stats, name='stock_stats'),
    
    # 自选股
    path('watchlist/', views.WatchListView.as_view(), name='watchlist'),
    
    # 行业板块
    path('industries/', views.IndustryListView.as_view(), name='industry_list'),
    path('industries/stocks/', views.IndustryStocksView.as_view(), name='industry_stocks'),
    
    # 概念板块
    path('concepts/', views.ConceptListView.as_view(), name='concept_list'),
    path('concepts/stocks/', views.ConceptStocksView.as_view(), name='concept_stocks'),
    
    # 历史数据采集任务管理
    path('tasks/history/', views.HistoryDataTaskView.as_view(), name='history_task'),
    
    # 以下视图暂未实现，先注释
    # path('minute/', views.StockMinuteDataView.as_view(), name='minute_data'),
    # path('minute/<str:stock_code>/', views.StockMinuteDataView.as_view(), name='minute_data_detail'),
    # path('financial/', views.StockFinancialDataView.as_view(), name='financial_data'),
    # path('financial/<str:stock_code>/', views.StockFinancialDataView.as_view(), name='financial_data_detail'),
    
    # 以下视图暂未实现，先注释
    # path('indicators/', views.StockIndicatorView.as_view(), name='indicators'),
    # path('indicators/<str:stock_code>/', views.StockIndicatorView.as_view(), name='indicators_detail'),
    # path('sync/', views.DataSyncView.as_view(), name='data_sync'),
    # path('<str:stock_code>/', views.StockDetailView.as_view(), name='stock_detail'),
]