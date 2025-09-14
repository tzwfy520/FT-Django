from django.db import models
from decimal import Decimal


class MarketIndex(models.Model):
    """大盘指数表"""
    index_code = models.CharField(max_length=10, unique=True, verbose_name='指数代码')
    index_name = models.CharField(max_length=50, verbose_name='指数名称')
    market = models.CharField(max_length=10, choices=[
        ('SH', '上海证券交易所'),
        ('SZ', '深圳证券交易所'),
        ('CSI', '中证指数')
    ], verbose_name='交易所')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'market_index'
        verbose_name = '大盘指数'
        verbose_name_plural = '大盘指数'
        ordering = ['index_code']
    
    def __str__(self):
        return f'{self.index_code} - {self.index_name}'


class MarketRealtimeData(models.Model):
    """大盘实时数据表"""
    index = models.ForeignKey(MarketIndex, on_delete=models.CASCADE, verbose_name='指数')
    current_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='当前点位')
    open_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='开盘点位')
    high_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最高点位')
    low_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最低点位')
    pre_close = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='昨收点位')
    change = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='涨跌点数')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    volume = models.BigIntegerField(verbose_name='成交量(手)')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='成交额(元)')
    timestamp = models.DateTimeField(verbose_name='数据时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'market_realtime_data'
        verbose_name = '大盘实时数据'
        verbose_name_plural = '大盘实时数据'
        ordering = ['-timestamp']
        unique_together = ['index', 'timestamp']
    
    def __str__(self):
        return f'{self.index.index_code} - {self.timestamp}'


class MarketHistoryData(models.Model):
    """大盘历史数据表"""
    index = models.ForeignKey(MarketIndex, on_delete=models.CASCADE, verbose_name='指数')
    trade_date = models.DateField(verbose_name='交易日期')
    open_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='开盘点位')
    high_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最高点位')
    low_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最低点位')
    close_point = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='收盘点位')
    pre_close = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='昨收点位')
    change = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='涨跌点数')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    volume = models.BigIntegerField(verbose_name='成交量(手)')
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='成交额(元)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'market_history_data'
        verbose_name = '大盘历史数据'
        verbose_name_plural = '大盘历史数据'
        ordering = ['-trade_date']
        unique_together = ['index', 'trade_date']
    
    def __str__(self):
        return f'{self.index.index_code} - {self.trade_date}'


class IndustryInfo(models.Model):
    """行业板块信息表"""
    industry_code = models.CharField(max_length=20, unique=True, verbose_name='行业代码')
    industry_name = models.CharField(max_length=50, verbose_name='行业名称')
    parent_industry = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父级行业')
    level = models.IntegerField(default=1, verbose_name='层级')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'industry_info'
        verbose_name = '行业板块信息'
        verbose_name_plural = '行业板块信息'
        ordering = ['industry_code']
    
    def __str__(self):
        return f'{self.industry_code} - {self.industry_name}'


class ConceptInfo(models.Model):
    """概念板块信息表"""
    concept_code = models.CharField(max_length=20, unique=True, verbose_name='概念代码')
    concept_name = models.CharField(max_length=50, verbose_name='概念名称')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'concept_info'
        verbose_name = '概念板块信息'
        verbose_name_plural = '概念板块信息'
        ordering = ['concept_code']
    
    def __str__(self):
        return f'{self.concept_code} - {self.concept_name}'


class IndustryRealtimeData(models.Model):
    """行业实时数据表"""
    industry = models.ForeignKey(IndustryInfo, on_delete=models.CASCADE, verbose_name='行业')
    avg_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='平均价格')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    up_count = models.IntegerField(verbose_name='上涨家数')
    down_count = models.IntegerField(verbose_name='下跌家数')
    flat_count = models.IntegerField(verbose_name='平盘家数')
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总成交额')
    timestamp = models.DateTimeField(verbose_name='数据时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'industry_realtime_data'
        verbose_name = '行业实时数据'
        verbose_name_plural = '行业实时数据'
        ordering = ['-timestamp']
        unique_together = ['industry', 'timestamp']
    
    def __str__(self):
        return f'{self.industry.industry_name} - {self.timestamp}'


class ConceptRealtimeData(models.Model):
    """概念实时数据表"""
    concept = models.ForeignKey(ConceptInfo, on_delete=models.CASCADE, verbose_name='概念')
    avg_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='平均价格')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    up_count = models.IntegerField(verbose_name='上涨家数')
    down_count = models.IntegerField(verbose_name='下跌家数')
    flat_count = models.IntegerField(verbose_name='平盘家数')
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总成交额')
    timestamp = models.DateTimeField(verbose_name='数据时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'concept_realtime_data'
        verbose_name = '概念实时数据'
        verbose_name_plural = '概念实时数据'
        ordering = ['-timestamp']
        unique_together = ['concept', 'timestamp']
    
    def __str__(self):
        return f'{self.concept.concept_name} - {self.timestamp}'


class MoneyFlow(models.Model):
    """资金流向表"""
    FLOW_TYPES = [
        ('market', '大盘资金流向'),
        ('industry', '行业资金流向'),
        ('concept', '概念资金流向'),
        ('stock', '个股资金流向'),
    ]
    
    flow_type = models.CharField(max_length=20, choices=FLOW_TYPES, verbose_name='流向类型')
    target_code = models.CharField(max_length=20, verbose_name='目标代码')
    target_name = models.CharField(max_length=50, verbose_name='目标名称')
    main_net_inflow = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='主力净流入')
    super_large_net_inflow = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='超大单净流入')
    large_net_inflow = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='大单净流入')
    medium_net_inflow = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='中单净流入')
    small_net_inflow = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='小单净流入')
    trade_date = models.DateField(verbose_name='交易日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'money_flow'
        verbose_name = '资金流向'
        verbose_name_plural = '资金流向'
        ordering = ['-trade_date']
        unique_together = ['flow_type', 'target_code', 'trade_date']
    
    def __str__(self):
        return f'{self.target_name} - {self.trade_date}'


class DragonTigerList(models.Model):
    """龙虎榜数据表"""
    stock_code = models.CharField(max_length=10, verbose_name='股票代码')
    stock_name = models.CharField(max_length=50, verbose_name='股票名称')
    trade_date = models.DateField(verbose_name='交易日期')
    close_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='收盘价')
    change_pct = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='涨跌幅(%)')
    turnover_rate = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='换手率(%)')
    net_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='净买额')
    buy_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='买入额')
    sell_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='卖出额')
    reason = models.CharField(max_length=100, verbose_name='上榜原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'dragon_tiger_list'
        verbose_name = '龙虎榜数据'
        verbose_name_plural = '龙虎榜数据'
        ordering = ['-trade_date', '-net_amount']
        unique_together = ['stock_code', 'trade_date']
    
    def __str__(self):
        return f'{self.stock_code} - {self.trade_date}'


class MarginTradingData(models.Model):
    """两融数据表"""
    stock_code = models.CharField(max_length=10, verbose_name='股票代码')
    stock_name = models.CharField(max_length=50, verbose_name='股票名称')
    trade_date = models.DateField(verbose_name='交易日期')
    margin_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='融资余额')
    margin_buy_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='融资买入额')
    margin_repay_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='融资偿还额')
    short_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='融券余额')
    short_sell_volume = models.BigIntegerField(verbose_name='融券卖出量')
    short_repay_volume = models.BigIntegerField(verbose_name='融券偿还量')
    total_balance = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='融资融券余额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'margin_trading_data'
        verbose_name = '两融数据'
        verbose_name_plural = '两融数据'
        ordering = ['-trade_date']
        unique_together = ['stock_code', 'trade_date']
    
    def __str__(self):
        return f'{self.stock_code} - {self.trade_date}'


class StockCalendar(models.Model):
    """股票日历表"""
    EVENT_TYPES = [
        ('earnings', '业绩发布'),
        ('dividend', '分红派息'),
        ('meeting', '股东大会'),
        ('ipo', '新股上市'),
        ('suspension', '停牌复牌'),
        ('other', '其他事件'),
    ]
    
    stock_code = models.CharField(max_length=10, verbose_name='股票代码')
    stock_name = models.CharField(max_length=50, verbose_name='股票名称')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='事件类型')
    event_title = models.CharField(max_length=100, verbose_name='事件标题')
    event_content = models.TextField(verbose_name='事件内容')
    event_date = models.DateField(verbose_name='事件日期')
    is_important = models.BooleanField(default=False, verbose_name='是否重要')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_calendar'
        verbose_name = '股票日历'
        verbose_name_plural = '股票日历'
        ordering = ['-event_date']
    
    def __str__(self):
        return f'{self.stock_code} - {self.event_title}'