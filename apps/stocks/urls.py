from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    # 股票列表和搜索
    path('list/', views.StockListView.as_view(), name='stock_list'),
    
    # 股票概览
    path('overview/', views.StockOverviewView.as_view(), name='stock_overview'),
    
    # 实时数据
    path('realtime/', views.StockRealTimeDataView.as_view(), name='realtime_data'),
    path('realtime/<str:stock_code>/', views.StockRealTimeDataView.as_view(), name='realtime_data_detail'),
    
    # 历史数据
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