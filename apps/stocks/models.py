from django.db import models
from django.utils import timezone
from decimal import Decimal


class StockBasicInfo(models.Model):
    """股票基础信息表"""
    stock_code = models.CharField(max_length=10, unique=True, verbose_name='股票代码')
    stock_name = models.CharField(max_length=50, verbose_name='股票名称')
    market = models.CharField(max_length=10, choices=[
        ('SH', '上海证券交易所'),
        ('SZ', '深圳证券交易所'),
        ('BJ', '北京证券交易所')
    ], verbose_name='交易所')
    industry = models.CharField(max_length=50, blank=True, verbose_name='所属行业')
    concept = models.TextField(blank=True, verbose_name='概念板块')
    list_date = models.DateField(null=True, blank=True, verbose_name='上市日期')
    total_share = models.BigIntegerField(null=True, blank=True, verbose_name='总股本')
    float_share = models.BigIntegerField(null=True, blank=True, verbose_name='流通股本')
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='总市值')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'stock_basic_info'
        verbose_name = '股票基础信息'
        verbose_name_plural = '股票基础信息'
        ordering = ['stock_code']
    
    def __str__(self):
        return f'{self.stock_code} - {self.stock_name}'


class StockRealtimeData(models.Model):
    """股票实时数据表"""
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    current_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='当前价格')
    open_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='开盘价')
    high_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='最高价')
    low_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='最低价')
    pre_close = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='昨收价')
    change = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='涨跌额')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    volume = models.BigIntegerField(verbose_name='成交量(手)')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='成交额(元)')
    turnover_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='换手率(%)')
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市盈率')
    pb_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市净率')
    timestamp = models.DateTimeField(verbose_name='数据时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_realtime_data'
        verbose_name = '股票实时数据'
        verbose_name_plural = '股票实时数据'
        ordering = ['-timestamp']
        unique_together = ['stock', 'timestamp']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.timestamp}'


class StockHistoryData(models.Model):
    """股票历史数据表"""
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    trade_date = models.DateField(verbose_name='交易日期')
    open_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='开盘价')
    high_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='最高价')
    low_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='最低价')
    close_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='收盘价')
    pre_close = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='昨收价')
    change = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='涨跌额')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    volume = models.BigIntegerField(verbose_name='成交量(手)')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='成交额(元)')
    turnover_rate = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='换手率(%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_history_data'
        verbose_name = '股票历史数据'
        verbose_name_plural = '股票历史数据'
        ordering = ['-trade_date']
        unique_together = ['stock', 'trade_date']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.trade_date}'


class StockMinuteData(models.Model):
    """股票分时数据表"""
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    trade_date = models.DateField(verbose_name='交易日期')
    minute_time = models.TimeField(verbose_name='分时时间')
    price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='价格')
    volume = models.BigIntegerField(verbose_name='成交量')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='成交额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_minute_data'
        verbose_name = '股票分时数据'
        verbose_name_plural = '股票分时数据'
        ordering = ['-trade_date', '-minute_time']
        unique_together = ['stock', 'trade_date', 'minute_time']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.trade_date} {self.minute_time}'


class WatchList(models.Model):
    """自选股票表 - 重新设计，与股票概览数据保持一致"""
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    user_id = models.IntegerField(default=1, verbose_name='用户ID')
    add_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='添加时价格')
    notes = models.TextField(blank=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'watch_list'
        verbose_name = '自选股票'
        verbose_name_plural = '自选股票'
        ordering = ['-created_at']
        unique_together = ['stock', 'user_id']
    
    def __str__(self):
        return f'{self.user.username} - {self.stock.stock_code}'


class StockAlert(models.Model):
    """股票提醒表"""
    ALERT_TYPES = [
        ('price_up', '价格上涨'),
        ('price_down', '价格下跌'),
        ('volume_surge', '成交量异动'),
        ('change_pct', '涨跌幅异动'),
    ]
    
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='用户')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, verbose_name='提醒类型')
    threshold_value = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='阈值')
    is_triggered = models.BooleanField(default=False, verbose_name='是否已触发')
    triggered_at = models.DateTimeField(null=True, blank=True, verbose_name='触发时间')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_alert'
        verbose_name = '股票提醒'
        verbose_name_plural = '股票提醒'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.get_alert_type_display()}'