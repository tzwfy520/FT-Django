from rest_framework import serializers
from .models import StockBasicInfo, StockRealtimeData, StockHistoryData, StockMinuteData


class StockSerializer(serializers.ModelSerializer):
    """股票基本信息序列化器"""
    
    class Meta:
        model = StockBasicInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockDataSerializer(serializers.ModelSerializer):
    """股票数据序列化器"""
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    
    class Meta:
        model = StockRealtimeData
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockHistoryDataSerializer(serializers.ModelSerializer):
    """股票历史数据序列化器"""
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    
    class Meta:
        model = StockHistoryData
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockMinuteDataSerializer(serializers.ModelSerializer):
    """股票分钟数据序列化器"""
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    
    class Meta:
        model = StockMinuteData
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class StockListSerializer(serializers.ModelSerializer):
    """股票列表序列化器（简化版）"""
    latest_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_change = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    change_percent = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = StockBasicInfo
        fields = ('stock_code', 'stock_name', 'market', 'industry', 'latest_price', 'price_change', 'change_percent')


class StockRealTimeSerializer(serializers.Serializer):
    """实时股票数据序列化器"""
    code = serializers.CharField()
    name = serializers.CharField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    open_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    high_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    low_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    volume = serializers.IntegerField()
    turnover = serializers.DecimalField(max_digits=15, decimal_places=2)
    change_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    change_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    timestamp = serializers.DateTimeField()


class StockHistorySerializer(serializers.Serializer):
    """历史股票数据序列化器"""
    date = serializers.DateField()
    open = serializers.DecimalField(max_digits=10, decimal_places=2)
    high = serializers.DecimalField(max_digits=10, decimal_places=2)
    low = serializers.DecimalField(max_digits=10, decimal_places=2)
    close = serializers.DecimalField(max_digits=10, decimal_places=2)
    volume = serializers.IntegerField()
    turnover = serializers.DecimalField(max_digits=15, decimal_places=2)
    change_percent = serializers.DecimalField(max_digits=5, decimal_places=2)


class StockMinuteSerializer(serializers.Serializer):
    """分钟级股票数据序列化器"""
    datetime = serializers.DateTimeField()
    open = serializers.DecimalField(max_digits=10, decimal_places=2)
    high = serializers.DecimalField(max_digits=10, decimal_places=2)
    low = serializers.DecimalField(max_digits=10, decimal_places=2)
    close = serializers.DecimalField(max_digits=10, decimal_places=2)
    volume = serializers.IntegerField()
    turnover = serializers.DecimalField(max_digits=15, decimal_places=2)


class DataSyncSerializer(serializers.Serializer):
    """数据同步请求序列化器"""
    stock_codes = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False,
        help_text="股票代码列表，为空则同步所有股票"
    )
    data_type = serializers.ChoiceField(
        choices=['realtime', 'history', 'minute', 'financial', 'all'],
        default='all',
        help_text="数据类型"
    )
    start_date = serializers.DateField(required=False, help_text="开始日期")
    end_date = serializers.DateField(required=False, help_text="结束日期")
    force_update = serializers.BooleanField(default=False, help_text="是否强制更新")