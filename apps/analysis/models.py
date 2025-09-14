from django.db import models
from django.contrib.auth.models import User
from apps.stocks.models import StockBasicInfo
from decimal import Decimal
import json


class AnalysisTemplate(models.Model):
    """分析模板表"""
    TEMPLATE_TYPES = [
        ('realtime', '实时分析'),
        ('daily', '日常复盘'),
        ('recommendation', '股票推荐'),
        ('custom', '自定义分析'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='模板名称')
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, verbose_name='模板类型')
    description = models.TextField(blank=True, verbose_name='模板描述')
    analysis_config = models.TextField(verbose_name='分析配置(JSON格式)')
    indicators = models.TextField(verbose_name='技术指标配置(JSON格式)')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'analysis_template'
        verbose_name = '分析模板'
        verbose_name_plural = '分析模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_analysis_config(self):
        """获取分析配置"""
        try:
            return json.loads(self.analysis_config)
        except json.JSONDecodeError:
            return {}
    
    def get_indicators(self):
        """获取技术指标配置"""
        try:
            return json.loads(self.indicators)
        except json.JSONDecodeError:
            return {}


class StockAnalysisResult(models.Model):
    """股票分析结果表"""
    ANALYSIS_TYPES = [
        ('realtime', '实时分析'),
        ('daily', '日常复盘'),
        ('recommendation', '推荐分析'),
        ('technical', '技术分析'),
        ('fundamental', '基本面分析'),
    ]
    
    RATING_CHOICES = [
        ('strong_buy', '强烈买入'),
        ('buy', '买入'),
        ('hold', '持有'),
        ('sell', '卖出'),
        ('strong_sell', '强烈卖出'),
    ]
    
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    template = models.ForeignKey(AnalysisTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分析模板')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES, verbose_name='分析类型')
    analysis_date = models.DateField(verbose_name='分析日期')
    
    # 分析结果
    overall_rating = models.CharField(max_length=20, choices=RATING_CHOICES, verbose_name='综合评级')
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='置信度(0-100)')
    
    # 价格建议
    target_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='目标价格')
    stop_loss_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='止损价格')
    entry_price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='建议买入价')
    
    # 技术分析结果
    technical_indicators = models.TextField(blank=True, verbose_name='技术指标结果(JSON格式)')
    support_levels = models.TextField(blank=True, verbose_name='支撑位(JSON格式)')
    resistance_levels = models.TextField(blank=True, verbose_name='阻力位(JSON格式)')
    
    # 基本面分析
    pe_analysis = models.TextField(blank=True, verbose_name='市盈率分析')
    pb_analysis = models.TextField(blank=True, verbose_name='市净率分析')
    roe_analysis = models.TextField(blank=True, verbose_name='ROE分析')
    
    # 资金面分析
    money_flow_analysis = models.TextField(blank=True, verbose_name='资金流向分析')
    volume_analysis = models.TextField(blank=True, verbose_name='成交量分析')
    
    # 分析摘要
    analysis_summary = models.TextField(verbose_name='分析摘要')
    risk_warning = models.TextField(blank=True, verbose_name='风险提示')
    
    # AI分析相关
    ai_analysis = models.TextField(blank=True, verbose_name='AI分析结果')
    ai_model_used = models.CharField(max_length=50, blank=True, verbose_name='使用的AI模型')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='分析者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'stock_analysis_result'
        verbose_name = '股票分析结果'
        verbose_name_plural = '股票分析结果'
        ordering = ['-analysis_date', '-created_at']
        unique_together = ['stock', 'analysis_type', 'analysis_date']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.analysis_date} - {self.get_analysis_type_display()}'
    
    def get_technical_indicators(self):
        """获取技术指标结果"""
        try:
            return json.loads(self.technical_indicators)
        except json.JSONDecodeError:
            return {}
    
    def get_support_levels(self):
        """获取支撑位"""
        try:
            return json.loads(self.support_levels)
        except json.JSONDecodeError:
            return []
    
    def get_resistance_levels(self):
        """获取阻力位"""
        try:
            return json.loads(self.resistance_levels)
        except json.JSONDecodeError:
            return []


class StockRecommendation(models.Model):
    """股票推荐表"""
    RECOMMENDATION_SOURCES = [
        ('dragon_tiger', '龙虎榜推荐'),
        ('money_flow', '资金流向推荐'),
        ('technical', '技术面推荐'),
        ('ai_analysis', 'AI分析推荐'),
        ('manual', '人工推荐'),
    ]
    
    RISK_LEVELS = [
        ('low', '低风险'),
        ('medium', '中风险'),
        ('high', '高风险'),
    ]
    
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    recommendation_source = models.CharField(max_length=20, choices=RECOMMENDATION_SOURCES, verbose_name='推荐来源')
    recommendation_date = models.DateField(verbose_name='推荐日期')
    
    # 推荐信息
    title = models.CharField(max_length=200, verbose_name='推荐标题')
    reason = models.TextField(verbose_name='推荐理由')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, verbose_name='风险等级')
    
    # 价格建议
    recommended_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='推荐买入价')
    target_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='目标价格')
    stop_loss_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='止损价格')
    
    # 预期收益
    expected_return_pct = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='预期收益率(%)')
    holding_period_days = models.IntegerField(verbose_name='建议持有天数')
    
    # 推荐状态
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    is_hit_target = models.BooleanField(default=False, verbose_name='是否达到目标价')
    is_hit_stop_loss = models.BooleanField(default=False, verbose_name='是否触及止损价')
    
    # 实际表现
    actual_return_pct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='实际收益率(%)')
    max_return_pct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='最大收益率(%)')
    max_drawdown_pct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='最大回撤(%)')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='推荐者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'stock_recommendation'
        verbose_name = '股票推荐'
        verbose_name_plural = '股票推荐'
        ordering = ['-recommendation_date', '-created_at']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.title}'


class PortfolioAnalysis(models.Model):
    """投资组合分析表"""
    name = models.CharField(max_length=100, verbose_name='组合名称')
    description = models.TextField(blank=True, verbose_name='组合描述')
    stocks = models.ManyToManyField(StockBasicInfo, through='PortfolioStock', verbose_name='包含股票')
    
    # 组合配置
    total_capital = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='总资金')
    risk_tolerance = models.CharField(max_length=15, choices=[
        ('conservative', '保守型'),
        ('moderate', '稳健型'),
        ('aggressive', '激进型'),
    ], verbose_name='风险偏好')
    
    # 分析结果
    expected_return = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='预期收益率')
    expected_risk = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='预期风险')
    sharpe_ratio = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True, verbose_name='夏普比率')
    
    analysis_date = models.DateField(verbose_name='分析日期')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'portfolio_analysis'
        verbose_name = '投资组合分析'
        verbose_name_plural = '投资组合分析'
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f'{self.name} - {self.analysis_date}'


class PortfolioStock(models.Model):
    """投资组合股票表"""
    portfolio = models.ForeignKey(PortfolioAnalysis, on_delete=models.CASCADE, verbose_name='投资组合')
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    weight = models.DecimalField(max_digits=8, decimal_places=4, verbose_name='权重(%)')
    shares = models.IntegerField(verbose_name='股数')
    cost_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='成本价格')
    
    class Meta:
        db_table = 'portfolio_stock'
        verbose_name = '投资组合股票'
        verbose_name_plural = '投资组合股票'
        unique_together = ['portfolio', 'stock']
    
    def __str__(self):
        return f'{self.portfolio.name} - {self.stock.stock_code}'


class TechnicalIndicator(models.Model):
    """技术指标计算结果表"""
    INDICATOR_TYPES = [
        ('MA', '移动平均线'),
        ('EMA', '指数移动平均线'),
        ('MACD', 'MACD'),
        ('RSI', 'RSI'),
        ('KDJ', 'KDJ'),
        ('BOLL', '布林带'),
        ('VOL', '成交量指标'),
        ('OBV', 'OBV'),
        ('CCI', 'CCI'),
        ('WR', '威廉指标'),
    ]
    
    stock = models.ForeignKey(StockBasicInfo, on_delete=models.CASCADE, verbose_name='股票')
    indicator_type = models.CharField(max_length=10, choices=INDICATOR_TYPES, verbose_name='指标类型')
    trade_date = models.DateField(verbose_name='交易日期')
    
    # 指标值(JSON格式存储不同指标的多个值)
    indicator_values = models.TextField(verbose_name='指标值(JSON格式)')
    
    # 信号
    signal = models.CharField(max_length=10, choices=[
        ('buy', '买入信号'),
        ('sell', '卖出信号'),
        ('hold', '持有信号'),
        ('neutral', '中性'),
    ], verbose_name='信号')
    
    signal_strength = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='信号强度(0-100)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'technical_indicator'
        verbose_name = '技术指标'
        verbose_name_plural = '技术指标'
        ordering = ['-trade_date']
        unique_together = ['stock', 'indicator_type', 'trade_date']
    
    def __str__(self):
        return f'{self.stock.stock_code} - {self.get_indicator_type_display()} - {self.trade_date}'
    
    def get_indicator_values(self):
        """获取指标值"""
        try:
            return json.loads(self.indicator_values)
        except json.JSONDecodeError:
            return {}