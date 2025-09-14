from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class SystemConfig(models.Model):
    """系统配置表"""
    CONFIG_TYPES = [
        ('database', '数据库配置'),
        ('api', 'API配置'),
        ('task', '任务配置'),
        ('notification', '通知配置'),
        ('security', '安全配置'),
        ('other', '其他配置'),
    ]
    
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_name = models.CharField(max_length=100, verbose_name='配置名称')
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPES, verbose_name='配置类型')
    config_value = models.TextField(verbose_name='配置值')
    description = models.TextField(blank=True, verbose_name='配置描述')
    is_encrypted = models.BooleanField(default=False, verbose_name='是否加密')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'system_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['config_type', 'config_key']
    
    def __str__(self):
        return f'{self.config_name} ({self.config_key})'


class DataSource(models.Model):
    """数据源配置表"""
    SOURCE_TYPES = [
        ('mysql', 'MySQL数据库'),
        ('postgresql', 'PostgreSQL数据库'),
        ('redis', 'Redis缓存'),
        ('minio', 'MinIO对象存储'),
        ('api', 'API接口'),
        ('file', '文件系统'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='数据源名称')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, verbose_name='数据源类型')
    host = models.CharField(max_length=255, verbose_name='主机地址')
    port = models.IntegerField(verbose_name='端口')
    username = models.CharField(max_length=100, blank=True, verbose_name='用户名')
    password = models.CharField(max_length=255, blank=True, verbose_name='密码')
    database_name = models.CharField(max_length=100, blank=True, verbose_name='数据库名')
    
    # 连接配置
    connection_params = models.TextField(blank=True, verbose_name='连接参数(JSON格式)')
    max_connections = models.IntegerField(default=10, verbose_name='最大连接数')
    connection_timeout = models.IntegerField(default=30, verbose_name='连接超时(秒)')
    
    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    last_test_time = models.DateTimeField(null=True, blank=True, verbose_name='最后测试时间')
    last_test_result = models.BooleanField(null=True, blank=True, verbose_name='最后测试结果')
    test_error_message = models.TextField(blank=True, verbose_name='测试错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'data_source'
        verbose_name = '数据源配置'
        verbose_name_plural = '数据源配置'
        ordering = ['name']
    
    def __str__(self):
        return f'{self.name} ({self.get_source_type_display()})'
    
    def get_connection_params(self):
        """获取连接参数"""
        try:
            return json.loads(self.connection_params)
        except json.JSONDecodeError:
            return {}
    
    def set_connection_params(self, params_dict):
        """设置连接参数"""
        self.connection_params = json.dumps(params_dict, ensure_ascii=False)


class DatabaseTable(models.Model):
    """数据库表信息表"""
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, verbose_name='数据源')
    table_name = models.CharField(max_length=100, verbose_name='表名')
    table_comment = models.CharField(max_length=255, blank=True, verbose_name='表注释')
    row_count = models.BigIntegerField(default=0, verbose_name='行数')
    data_size_mb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='数据大小(MB)')
    index_size_mb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='索引大小(MB)')
    
    # 表结构信息
    columns_info = models.TextField(blank=True, verbose_name='列信息(JSON格式)')
    indexes_info = models.TextField(blank=True, verbose_name='索引信息(JSON格式)')
    
    last_updated = models.DateTimeField(null=True, blank=True, verbose_name='最后更新时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'database_table'
        verbose_name = '数据库表信息'
        verbose_name_plural = '数据库表信息'
        ordering = ['data_source', 'table_name']
        unique_together = ['data_source', 'table_name']
    
    def __str__(self):
        return f'{self.data_source.name}.{self.table_name}'
    
    def get_columns_info(self):
        """获取列信息"""
        try:
            return json.loads(self.columns_info)
        except json.JSONDecodeError:
            return []
    
    def get_indexes_info(self):
        """获取索引信息"""
        try:
            return json.loads(self.indexes_info)
        except json.JSONDecodeError:
            return []
    
    def get_total_size_mb(self):
        """获取总大小(MB)"""
        return self.data_size_mb + self.index_size_mb
    
    def get_size_display(self):
        """获取大小显示字符串"""
        total_size = self.get_total_size_mb()
        if total_size >= 1024:
            return f'{total_size / 1024:.2f} GB'
        elif total_size >= 1:
            return f'{total_size:.2f} MB'
        else:
            return f'{total_size * 1024:.2f} KB'


class APIEndpoint(models.Model):
    """API接口配置表"""
    ENDPOINT_TYPES = [
        ('stock_data', '股票数据接口'),
        ('market_data', '市场数据接口'),
        ('ai_model', 'AI模型接口'),
        ('notification', '通知接口'),
        ('other', '其他接口'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='接口名称')
    endpoint_type = models.CharField(max_length=20, choices=ENDPOINT_TYPES, verbose_name='接口类型')
    base_url = models.URLField(verbose_name='基础URL')
    api_key = models.CharField(max_length=255, blank=True, verbose_name='API密钥')
    secret_key = models.CharField(max_length=255, blank=True, verbose_name='密钥')
    
    # 请求配置
    headers = models.TextField(blank=True, verbose_name='请求头(JSON格式)')
    timeout_seconds = models.IntegerField(default=30, verbose_name='超时时间(秒)')
    max_retries = models.IntegerField(default=3, verbose_name='最大重试次数')
    rate_limit_per_minute = models.IntegerField(null=True, blank=True, verbose_name='每分钟请求限制')
    
    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    last_test_time = models.DateTimeField(null=True, blank=True, verbose_name='最后测试时间')
    last_test_result = models.BooleanField(null=True, blank=True, verbose_name='最后测试结果')
    test_error_message = models.TextField(blank=True, verbose_name='测试错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'api_endpoint'
        verbose_name = 'API接口配置'
        verbose_name_plural = 'API接口配置'
        ordering = ['endpoint_type', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.get_endpoint_type_display()})'
    
    def get_headers(self):
        """获取请求头"""
        try:
            return json.loads(self.headers)
        except json.JSONDecodeError:
            return {}


class SystemMonitor(models.Model):
    """系统监控表"""
    MONITOR_TYPES = [
        ('cpu', 'CPU使用率'),
        ('memory', '内存使用率'),
        ('disk', '磁盘使用率'),
        ('network', '网络流量'),
        ('database', '数据库连接'),
        ('task_queue', '任务队列'),
    ]
    
    monitor_type = models.CharField(max_length=20, choices=MONITOR_TYPES, verbose_name='监控类型')
    metric_name = models.CharField(max_length=100, verbose_name='指标名称')
    metric_value = models.DecimalField(max_digits=15, decimal_places=4, verbose_name='指标值')
    metric_unit = models.CharField(max_length=20, verbose_name='单位')
    
    # 阈值设置
    warning_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, verbose_name='警告阈值')
    critical_threshold = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True, verbose_name='严重阈值')
    
    # 状态
    status = models.CharField(max_length=10, choices=[
        ('normal', '正常'),
        ('warning', '警告'),
        ('critical', '严重'),
    ], default='normal', verbose_name='状态')
    
    timestamp = models.DateTimeField(verbose_name='监控时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'system_monitor'
        verbose_name = '系统监控'
        verbose_name_plural = '系统监控'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.get_monitor_type_display()} - {self.metric_name}'


class SystemLog(models.Model):
    """系统日志表"""
    LOG_LEVELS = [
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]
    
    LOG_CATEGORIES = [
        ('system', '系统日志'),
        ('user', '用户操作'),
        ('api', 'API调用'),
        ('task', '任务执行'),
        ('data', '数据处理'),
        ('security', '安全相关'),
    ]
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name='日志级别')
    category = models.CharField(max_length=20, choices=LOG_CATEGORIES, verbose_name='日志分类')
    message = models.TextField(verbose_name='日志消息')
    
    # 详细信息
    module = models.CharField(max_length=100, blank=True, verbose_name='模块名')
    function = models.CharField(max_length=100, blank=True, verbose_name='函数名')
    line_number = models.IntegerField(null=True, blank=True, verbose_name='行号')
    
    # 用户和IP信息
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    # 额外数据
    extra_data = models.TextField(blank=True, verbose_name='额外数据(JSON格式)')
    
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='日志时间')
    
    class Meta:
        db_table = 'system_log'
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['level', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f'{self.level} - {self.message[:50]}'
    
    def get_extra_data(self):
        """获取额外数据"""
        try:
            return json.loads(self.extra_data)
        except json.JSONDecodeError:
            return {}


class SystemNotification(models.Model):
    """系统通知表"""
    NOTIFICATION_TYPES = [
        ('system', '系统通知'),
        ('alert', '告警通知'),
        ('task', '任务通知'),
        ('user', '用户通知'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, verbose_name='优先级')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    
    # 接收者
    recipient_users = models.ManyToManyField(User, blank=True, verbose_name='接收用户')
    recipient_emails = models.TextField(blank=True, verbose_name='接收邮箱(多个用逗号分隔)')
    
    # 发送状态
    is_sent = models.BooleanField(default=False, verbose_name='是否已发送')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    send_error = models.TextField(blank=True, verbose_name='发送错误信息')
    
    # 阅读状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='阅读时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'system_notification'
        verbose_name = '系统通知'
        verbose_name_plural = '系统通知'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.title}'