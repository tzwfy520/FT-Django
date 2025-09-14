from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class AIModel(models.Model):
    """AI模型配置表"""
    MODEL_TYPES = [
        ('openai', 'OpenAI'),
        ('claude', 'Claude'),
        ('gemini', 'Gemini'),
        ('qwen', '通义千问'),
        ('baichuan', '百川'),
        ('chatglm', 'ChatGLM'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='模型名称')
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES, verbose_name='模型类型')
    model_id = models.CharField(max_length=100, verbose_name='模型ID')
    api_endpoint = models.URLField(verbose_name='API端点')
    api_key = models.CharField(max_length=255, verbose_name='API密钥')
    
    # 模型参数
    max_tokens = models.IntegerField(default=4000, verbose_name='最大令牌数')
    temperature = models.FloatField(default=0.7, verbose_name='温度参数')
    top_p = models.FloatField(default=1.0, verbose_name='Top-p参数')
    frequency_penalty = models.FloatField(default=0.0, verbose_name='频率惩罚')
    presence_penalty = models.FloatField(default=0.0, verbose_name='存在惩罚')
    
    # 费用配置
    input_price_per_1k = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='输入价格(每1K tokens)')
    output_price_per_1k = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='输出价格(每1K tokens)')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    description = models.TextField(blank=True, verbose_name='模型描述')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_model'
        verbose_name = 'AI模型配置'
        verbose_name_plural = 'AI模型配置'
        ordering = ['model_type', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.get_model_type_display()})'


class AIAnalysisTemplate(models.Model):
    """AI分析模板表"""
    TEMPLATE_TYPES = [
        ('stock_analysis', '股票分析'),
        ('market_analysis', '市场分析'),
        ('portfolio_analysis', '投资组合分析'),
        ('risk_analysis', '风险分析'),
        ('news_analysis', '新闻分析'),
        ('technical_analysis', '技术分析'),
        ('fundamental_analysis', '基本面分析'),
        ('custom', '自定义分析'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='模板名称')
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, verbose_name='模板类型')
    description = models.TextField(verbose_name='模板描述')
    
    # 提示词配置
    system_prompt = models.TextField(verbose_name='系统提示词')
    user_prompt_template = models.TextField(verbose_name='用户提示词模板')
    
    # 输入参数配置
    input_parameters = models.TextField(verbose_name='输入参数配置(JSON格式)')
    
    # 输出格式配置
    output_format = models.TextField(blank=True, verbose_name='输出格式要求')
    expected_fields = models.TextField(blank=True, verbose_name='期望字段(JSON格式)')
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    success_count = models.IntegerField(default=0, verbose_name='成功次数')
    
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_analysis_template'
        verbose_name = 'AI分析模板'
        verbose_name_plural = 'AI分析模板'
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.get_template_type_display()})'
    
    def get_input_parameters(self):
        """获取输入参数配置"""
        try:
            return json.loads(self.input_parameters)
        except json.JSONDecodeError:
            return {}
    
    def get_expected_fields(self):
        """获取期望字段"""
        try:
            return json.loads(self.expected_fields)
        except json.JSONDecodeError:
            return []
    
    def get_success_rate(self):
        """获取成功率"""
        if self.usage_count == 0:
            return 0
        return round(self.success_count / self.usage_count * 100, 2)


class AIAnalysisRecord(models.Model):
    """AI分析记录表"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('timeout', '超时'),
    ]
    
    # 基本信息
    record_id = models.CharField(max_length=50, unique=True, verbose_name='记录ID')
    template = models.ForeignKey(AIAnalysisTemplate, on_delete=models.CASCADE, verbose_name='分析模板')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name='使用模型')
    
    # 分析目标
    target_type = models.CharField(max_length=20, choices=[
        ('stock', '股票'),
        ('market', '市场'),
        ('portfolio', '投资组合'),
        ('news', '新闻'),
        ('custom', '自定义'),
    ], verbose_name='分析目标类型')
    target_id = models.CharField(max_length=50, blank=True, verbose_name='目标ID')
    target_name = models.CharField(max_length=100, blank=True, verbose_name='目标名称')
    
    # 输入数据
    input_data = models.TextField(verbose_name='输入数据(JSON格式)')
    system_prompt = models.TextField(verbose_name='系统提示词')
    user_prompt = models.TextField(verbose_name='用户提示词')
    
    # 模型参数
    model_parameters = models.TextField(verbose_name='模型参数(JSON格式)')
    
    # 输出结果
    raw_response = models.TextField(blank=True, verbose_name='原始响应')
    parsed_result = models.TextField(blank=True, verbose_name='解析结果(JSON格式)')
    analysis_summary = models.TextField(blank=True, verbose_name='分析摘要')
    
    # 执行信息
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name='执行时长(秒)')
    
    # 费用统计
    input_tokens = models.IntegerField(default=0, verbose_name='输入令牌数')
    output_tokens = models.IntegerField(default=0, verbose_name='输出令牌数')
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='总费用')
    
    # 错误信息
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    error_code = models.CharField(max_length=50, blank=True, verbose_name='错误代码')
    
    # 质量评估
    quality_score = models.IntegerField(null=True, blank=True, verbose_name='质量评分(1-10)')
    quality_feedback = models.TextField(blank=True, verbose_name='质量反馈')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'ai_analysis_record'
        verbose_name = 'AI分析记录'
        verbose_name_plural = 'AI分析记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['template', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        return f'{self.record_id} - {self.template.name}'
    
    def get_input_data(self):
        """获取输入数据"""
        try:
            return json.loads(self.input_data)
        except json.JSONDecodeError:
            return {}
    
    def get_parsed_result(self):
        """获取解析结果"""
        try:
            return json.loads(self.parsed_result)
        except json.JSONDecodeError:
            return {}
    
    def get_model_parameters(self):
        """获取模型参数"""
        try:
            return json.loads(self.model_parameters)
        except json.JSONDecodeError:
            return {}
    
    def calculate_duration(self):
        """计算执行时长"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
            return self.duration_seconds
        return None
    
    def calculate_cost(self):
        """计算费用"""
        if self.model:
            input_cost = (self.input_tokens / 1000) * float(self.model.input_price_per_1k)
            output_cost = (self.output_tokens / 1000) * float(self.model.output_price_per_1k)
            self.total_cost = input_cost + output_cost
            return self.total_cost
        return 0


class AIConversation(models.Model):
    """AI对话记录表"""
    conversation_id = models.CharField(max_length=50, unique=True, verbose_name='对话ID')
    title = models.CharField(max_length=200, verbose_name='对话标题')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name='使用模型')
    
    # 对话统计
    message_count = models.IntegerField(default=0, verbose_name='消息数量')
    total_input_tokens = models.IntegerField(default=0, verbose_name='总输入令牌数')
    total_output_tokens = models.IntegerField(default=0, verbose_name='总输出令牌数')
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='总费用')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_conversation'
        verbose_name = 'AI对话'
        verbose_name_plural = 'AI对话'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'{self.title} ({self.conversation_id})'


class AIMessage(models.Model):
    """AI消息记录表"""
    MESSAGE_TYPES = [
        ('system', '系统消息'),
        ('user', '用户消息'),
        ('assistant', '助手消息'),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages', verbose_name='对话')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    
    # 令牌统计
    input_tokens = models.IntegerField(default=0, verbose_name='输入令牌数')
    output_tokens = models.IntegerField(default=0, verbose_name='输出令牌数')
    
    # 附加信息
    metadata = models.TextField(blank=True, verbose_name='元数据(JSON格式)')
    
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='时间戳')
    
    class Meta:
        db_table = 'ai_message'
        verbose_name = 'AI消息'
        verbose_name_plural = 'AI消息'
        ordering = ['conversation', 'timestamp']
    
    def __str__(self):
        return f'{self.get_message_type_display()} - {self.content[:50]}'
    
    def get_metadata(self):
        """获取元数据"""
        try:
            return json.loads(self.metadata)
        except json.JSONDecodeError:
            return {}


class AIUsageStatistics(models.Model):
    """AI使用统计表"""
    PERIOD_TYPES = [
        ('hour', '小时'),
        ('day', '天'),
        ('week', '周'),
        ('month', '月'),
    ]
    
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name='模型')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='用户')
    
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPES, verbose_name='统计周期')
    period_start = models.DateTimeField(verbose_name='周期开始时间')
    period_end = models.DateTimeField(verbose_name='周期结束时间')
    
    # 使用统计
    request_count = models.IntegerField(default=0, verbose_name='请求次数')
    success_count = models.IntegerField(default=0, verbose_name='成功次数')
    error_count = models.IntegerField(default=0, verbose_name='错误次数')
    
    # 令牌统计
    total_input_tokens = models.IntegerField(default=0, verbose_name='总输入令牌数')
    total_output_tokens = models.IntegerField(default=0, verbose_name='总输出令牌数')
    
    # 费用统计
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name='总费用')
    
    # 性能统计
    avg_response_time = models.FloatField(default=0, verbose_name='平均响应时间(秒)')
    max_response_time = models.FloatField(default=0, verbose_name='最大响应时间(秒)')
    min_response_time = models.FloatField(default=0, verbose_name='最小响应时间(秒)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'ai_usage_statistics'
        verbose_name = 'AI使用统计'
        verbose_name_plural = 'AI使用统计'
        ordering = ['-period_start']
        unique_together = ['model', 'user', 'period_type', 'period_start']
    
    def __str__(self):
        user_str = self.user.username if self.user else '全部用户'
        return f'{self.model.name} - {user_str} ({self.get_period_type_display()})'
    
    def get_success_rate(self):
        """获取成功率"""
        if self.request_count == 0:
            return 0
        return round(self.success_count / self.request_count * 100, 2)
    
    def get_avg_tokens_per_request(self):
        """获取平均每次请求的令牌数"""
        if self.request_count == 0:
            return 0
        return round((self.total_input_tokens + self.total_output_tokens) / self.request_count, 2)