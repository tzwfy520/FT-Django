from django.db import models
from django.contrib.auth.models import User


class AIAnalysisRecord(models.Model):
    """AI分析记录模型"""
    
    ANALYSIS_TYPE_CHOICES = [
        ('stock', '股票分析'),
        ('market', '市场分析'),
        ('technical', '技术分析'),
        ('sentiment', '情绪分析'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, verbose_name='分析类型')
    stock_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='股票代码')
    prompt = models.TextField(verbose_name='分析提示')
    result = models.TextField(blank=True, null=True, verbose_name='分析结果')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_analysis_records'
        verbose_name = 'AI分析记录'
        verbose_name_plural = 'AI分析记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_analysis_type_display()} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class AIModelConfig(models.Model):
    """AI模型配置"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='模型名称')
    api_key = models.CharField(max_length=200, verbose_name='API密钥')
    base_url = models.URLField(verbose_name='API基础URL')
    model_name = models.CharField(max_length=100, verbose_name='模型标识')
    max_tokens = models.IntegerField(default=4000, verbose_name='最大令牌数')
    temperature = models.FloatField(default=0.7, verbose_name='温度参数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_model_configs'
        verbose_name = 'AI模型配置'
        verbose_name_plural = 'AI模型配置'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name