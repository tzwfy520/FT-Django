from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
import uuid
from enum import Enum


class TaskTypeEnum(models.TextChoices):
    """任务类型枚举"""
    PERIODIC = 'periodic', '周期任务'
    SCHEDULED = 'scheduled', '定时任务'
    IMMEDIATE = 'immediate', '立即执行'
    SPECIAL = 'special', '特殊任务'
    DEPENDENT = 'dependent', '依赖任务'


class TaskStatusEnum(models.TextChoices):
    """任务状态枚举"""
    ACTIVE = 'active', '激活'
    INACTIVE = 'inactive', '未激活'
    PAUSED = 'paused', '暂停'
    ERROR = 'error', '错误'
    ARCHIVED = 'archived', '已归档'


class ExecutionStatusEnum(models.TextChoices):
    """执行状态枚举"""
    PENDING = 'pending', '等待执行'
    RUNNING = 'running', '执行中'
    SUCCESS = 'success', '执行成功'
    FAILED = 'failed', '执行失败'
    TIMEOUT = 'timeout', '执行超时'
    CANCELLED = 'cancelled', '已取消'
    RETRY = 'retry', '重试中'
    SKIPPED = 'skipped', '已跳过'


class PriorityEnum(models.TextChoices):
    """优先级枚举"""
    LOW = 'low', '低'
    NORMAL = 'normal', '普通'
    HIGH = 'high', '高'
    CRITICAL = 'critical', '紧急'


class TaskCategory(models.Model):
    """任务分类表"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='描述')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='显示颜色')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'task_category_enhanced'
        verbose_name = '任务分类'
        verbose_name_plural = '任务分类'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class TaskDefinition(models.Model):
    """任务定义表 - 统一管理所有类型的任务"""
    
    # 基本信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name='任务名称')
    description = models.TextField(blank=True, verbose_name='任务描述')
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='任务分类')
    
    # 任务类型和配置
    task_type = models.CharField(max_length=20, choices=TaskTypeEnum.choices, verbose_name='任务类型')
    task_module = models.CharField(max_length=200, verbose_name='任务模块路径')
    task_function = models.CharField(max_length=100, verbose_name='任务函数名')
    task_args = models.TextField(blank=True, verbose_name='任务参数(JSON格式)')
    
    # 执行配置
    priority = models.CharField(max_length=20, choices=PriorityEnum.choices, default=PriorityEnum.NORMAL, verbose_name='优先级')
    timeout_seconds = models.IntegerField(default=3600, validators=[MinValueValidator(1)], verbose_name='超时时间(秒)')
    max_retries = models.IntegerField(default=3, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name='最大重试次数')
    retry_delay_seconds = models.IntegerField(default=60, validators=[MinValueValidator(1)], verbose_name='重试延迟(秒)')
    
    # 周期任务配置
    interval_seconds = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)], verbose_name='间隔秒数')
    
    # 定时任务配置
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name='Cron表达式')
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    
    # 一次性任务配置
    execute_at = models.DateTimeField(null=True, blank=True, verbose_name='执行时间')
    
    # 特殊任务配置
    is_singleton = models.BooleanField(default=False, verbose_name='是否单例执行')
    allow_overlap = models.BooleanField(default=False, verbose_name='是否允许重叠执行')
    
    # 状态和控制
    status = models.CharField(max_length=20, choices=TaskStatusEnum.choices, default=TaskStatusEnum.ACTIVE, verbose_name='状态')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 统计信息
    total_executions = models.IntegerField(default=0, verbose_name='总执行次数')
    success_executions = models.IntegerField(default=0, verbose_name='成功执行次数')
    failed_executions = models.IntegerField(default=0, verbose_name='失败执行次数')
    last_execution_time = models.DateTimeField(null=True, blank=True, verbose_name='最后执行时间')
    next_execution_time = models.DateTimeField(null=True, blank=True, verbose_name='下次执行时间')
    
    # 创建和更新信息
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'task_definition_enhanced'
        verbose_name = '任务定义'
        verbose_name_plural = '任务定义'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_type', 'status']),
            models.Index(fields=['is_active', 'next_execution_time']),
            models.Index(fields=['category', 'created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_task_args(self):
        """获取任务参数"""
        if self.task_args:
            try:
                return json.loads(self.task_args)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_task_args(self, args_dict):
        """设置任务参数"""
        self.task_args = json.dumps(args_dict, ensure_ascii=False)
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_executions == 0:
            return 0
        return round(self.success_executions / self.total_executions * 100, 2)
    
    def is_periodic(self):
        """是否为周期任务"""
        return self.task_type == TaskTypeEnum.PERIODIC
    
    def is_scheduled(self):
        """是否为定时任务"""
        return self.task_type == TaskTypeEnum.SCHEDULED
    
    def is_special(self):
        """是否为特殊任务"""
        return self.task_type == TaskTypeEnum.SPECIAL


class TaskExecution(models.Model):
    """任务执行记录表 - 增强版"""
    
    # 基本信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(TaskDefinition, on_delete=models.CASCADE, verbose_name='关联任务')
    execution_id = models.CharField(max_length=100, unique=True, verbose_name='执行ID')
    
    # 执行状态
    status = models.CharField(max_length=20, choices=ExecutionStatusEnum.choices, default=ExecutionStatusEnum.PENDING, verbose_name='执行状态')
    
    # 时间信息
    scheduled_time = models.DateTimeField(verbose_name='计划执行时间')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_seconds = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')
    
    # 执行结果
    result_data = models.TextField(blank=True, verbose_name='执行结果')
    output_data = models.TextField(blank=True, verbose_name='输出数据')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    traceback_info = models.TextField(blank=True, verbose_name='错误堆栈')
    
    # 重试信息
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    max_retries = models.IntegerField(default=3, verbose_name='最大重试次数')
    
    # 执行环境
    worker_name = models.CharField(max_length=100, blank=True, verbose_name='执行节点')
    worker_pid = models.IntegerField(null=True, blank=True, verbose_name='进程ID')
    
    # 资源使用
    memory_usage_mb = models.FloatField(null=True, blank=True, verbose_name='内存使用(MB)')
    cpu_usage_percent = models.FloatField(null=True, blank=True, verbose_name='CPU使用率(%)')
    
    # 触发信息
    trigger_type = models.CharField(max_length=20, choices=[
        ('auto', '自动触发'),
        ('manual', '手动触发'),
        ('api', 'API触发'),
        ('dependency', '依赖触发'),
    ], default='auto', verbose_name='触发类型')
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='触发者')
    
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_execution_enhanced'
        verbose_name = '任务执行记录'
        verbose_name_plural = '任务执行记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['worker_name', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.task.name} - {self.execution_id}'
    
    @property
    def is_finished(self):
        """是否已完成"""
        return self.status in [ExecutionStatusEnum.SUCCESS, ExecutionStatusEnum.FAILED, 
                              ExecutionStatusEnum.TIMEOUT, ExecutionStatusEnum.CANCELLED]
    
    @property
    def is_successful(self):
        """是否成功"""
        return self.status == ExecutionStatusEnum.SUCCESS
    
    def calculate_duration(self):
        """计算执行时长"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = delta.total_seconds()
            return self.duration_seconds
        return None
    
    def can_retry(self):
        """是否可以重试"""
        return (self.status in [ExecutionStatusEnum.FAILED, ExecutionStatusEnum.TIMEOUT] and 
                self.retry_count < self.max_retries)


class TaskLog(models.Model):
    """任务日志表 - 增强版"""
    LOG_LEVELS = [
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_execution = models.ForeignKey(TaskExecution, on_delete=models.CASCADE, verbose_name='任务执行记录')
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name='日志级别')
    message = models.TextField(verbose_name='日志消息')
    
    # 代码位置信息
    module = models.CharField(max_length=100, blank=True, verbose_name='模块名')
    function = models.CharField(max_length=100, blank=True, verbose_name='函数名')
    line_number = models.IntegerField(null=True, blank=True, verbose_name='行号')
    
    # 额外数据
    extra_data = models.TextField(blank=True, verbose_name='额外数据(JSON格式)')
    tags = models.CharField(max_length=200, blank=True, verbose_name='标签')
    
    # 时间戳
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='时间戳')
    
    class Meta:
        db_table = 'task_log_enhanced'
        verbose_name = '任务日志'
        verbose_name_plural = '任务日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['task_execution', 'level']),
            models.Index(fields=['level', 'timestamp']),
        ]
    
    def __str__(self):
        return f'{self.level} - {self.message[:50]}'


class TaskDependency(models.Model):
    """任务依赖关系表"""
    DEPENDENCY_TYPES = [
        ('success', '成功后执行'),
        ('failure', '失败后执行'),
        ('always', '总是执行'),
        ('condition', '条件执行'),
    ]
    
    parent_task = models.ForeignKey(TaskDefinition, on_delete=models.CASCADE, 
                                   related_name='child_dependencies', verbose_name='父任务')
    child_task = models.ForeignKey(TaskDefinition, on_delete=models.CASCADE, 
                                  related_name='parent_dependencies', verbose_name='子任务')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPES, 
                                     default='success', verbose_name='依赖类型')
    condition_expression = models.TextField(blank=True, verbose_name='条件表达式')
    delay_seconds = models.IntegerField(default=0, verbose_name='延迟执行(秒)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_dependency_enhanced'
        verbose_name = '任务依赖关系'
        verbose_name_plural = '任务依赖关系'
        unique_together = ['parent_task', 'child_task']
    
    def __str__(self):
        return f'{self.parent_task.name} -> {self.child_task.name}'


class TaskSchedule(models.Model):
    """任务调度配置表"""
    SCHEDULE_TYPES = [
        ('interval', '间隔调度'),
        ('cron', 'Cron调度'),
        ('date', '日期调度'),
    ]
    
    task = models.OneToOneField(TaskDefinition, on_delete=models.CASCADE, verbose_name='关联任务')
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, verbose_name='调度类型')
    
    # 间隔调度
    interval_seconds = models.IntegerField(null=True, blank=True, verbose_name='间隔秒数')
    
    # Cron调度
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name='Cron表达式')
    
    # 日期调度
    run_date = models.DateTimeField(null=True, blank=True, verbose_name='运行日期')
    
    # 调度配置
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开始日期')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='结束日期')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    last_run_time = models.DateTimeField(null=True, blank=True, verbose_name='最后运行时间')
    next_run_time = models.DateTimeField(null=True, blank=True, verbose_name='下次运行时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'task_schedule_enhanced'
        verbose_name = '任务调度配置'
        verbose_name_plural = '任务调度配置'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.task.name} - {self.schedule_type}'


class TaskMetrics(models.Model):
    """任务执行指标表"""
    task = models.ForeignKey(TaskDefinition, on_delete=models.CASCADE, verbose_name='关联任务')
    date = models.DateField(verbose_name='日期')
    
    # 执行统计
    total_executions = models.IntegerField(default=0, verbose_name='总执行次数')
    success_executions = models.IntegerField(default=0, verbose_name='成功次数')
    failed_executions = models.IntegerField(default=0, verbose_name='失败次数')
    timeout_executions = models.IntegerField(default=0, verbose_name='超时次数')
    cancelled_executions = models.IntegerField(default=0, verbose_name='取消次数')
    
    # 性能指标
    avg_duration_seconds = models.FloatField(null=True, blank=True, verbose_name='平均执行时长(秒)')
    max_duration_seconds = models.FloatField(null=True, blank=True, verbose_name='最大执行时长(秒)')
    min_duration_seconds = models.FloatField(null=True, blank=True, verbose_name='最小执行时长(秒)')
    
    # 资源使用
    avg_memory_usage_mb = models.FloatField(null=True, blank=True, verbose_name='平均内存使用(MB)')
    max_memory_usage_mb = models.FloatField(null=True, blank=True, verbose_name='最大内存使用(MB)')
    avg_cpu_usage_percent = models.FloatField(null=True, blank=True, verbose_name='平均CPU使用率(%)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_metrics'
        verbose_name = '任务执行指标'
        verbose_name_plural = '任务执行指标'
        unique_together = ['task', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f'{self.task.name} - {self.date}'
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_executions == 0:
            return 0
        return round(self.success_executions / self.total_executions * 100, 2)