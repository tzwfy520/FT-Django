from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ApiProvider(models.Model):
    """API提供商模型"""
    PROVIDER_CHOICES = [
        ('aihubmix', '推理时代'),
        ('coze', 'Coze'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True, verbose_name='提供商名称')
    display_name = models.CharField(max_length=100, verbose_name='显示名称')
    base_url = models.URLField(verbose_name='基础URL')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'api_provider'
        verbose_name = 'API提供商'
        verbose_name_plural = 'API提供商'
    
    def __str__(self):
        return self.display_name


class ApiToken(models.Model):
    """API Token配置模型"""
    provider = models.OneToOneField(ApiProvider, on_delete=models.CASCADE, verbose_name='API提供商')
    token = models.TextField(verbose_name='API Token')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='配置用户')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'api_token'
        verbose_name = 'API Token'
        verbose_name_plural = 'API Token'
    
    def __str__(self):
        return f'{self.provider.display_name} - {self.user.username}'


class ApiInterface(models.Model):
    """API接口配置模型"""
    provider = models.ForeignKey(ApiProvider, on_delete=models.CASCADE, verbose_name='API提供商')
    name = models.CharField(max_length=100, verbose_name='接口名称')
    model = models.CharField(max_length=100, verbose_name='模型名称')
    temperature = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name='温度参数'
    )
    max_tokens = models.IntegerField(
        default=1024,
        validators=[MinValueValidator(1)],
        verbose_name='最大令牌数'
    )
    purposes = models.JSONField(default=list, blank=True, verbose_name='接口用途')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建用户')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'api_interface'
        verbose_name = 'API接口配置'
        verbose_name_plural = 'API接口配置'
        unique_together = ['provider', 'name', 'user']
    
    def __str__(self):
        return f'{self.provider.display_name} - {self.name}'


class ApiCallLog(models.Model):
    """API调用日志模型"""
    interface = models.ForeignKey(ApiInterface, on_delete=models.CASCADE, verbose_name='接口配置')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='调用用户')
    request_data = models.JSONField(verbose_name='请求数据')
    response_data = models.JSONField(null=True, blank=True, verbose_name='响应数据')
    status_code = models.IntegerField(verbose_name='状态码')
    response_time = models.FloatField(verbose_name='响应时间(秒)')
    prompt_tokens = models.IntegerField(default=0, verbose_name='输入令牌数')
    completion_tokens = models.IntegerField(default=0, verbose_name='输出令牌数')
    total_tokens = models.IntegerField(default=0, verbose_name='总令牌数')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='调用时间')
    
    class Meta:
        db_table = 'api_call_log'
        verbose_name = 'API调用日志'
        verbose_name_plural = 'API调用日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.interface.name} - {self.created_at}'