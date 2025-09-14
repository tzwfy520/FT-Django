from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class TaskCategory(models.Model):
    """任务分类表"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否有效')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_category'
        verbose_name = '任务分类'
        verbose_name_plural = '任务分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ScheduledTask(models.Model):
    """定时任务表"""
    TASK_TYPES = [
        ('periodic', '周期任务'),
        ('cron', '定时任务'),
        ('once', '一次性任务'),
    ]
    
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('paused', '暂停'),
        ('error', '错误'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='任务名称')
    description = models.TextField(blank=True, verbose_name='任务描述')
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='任务分类')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name='任务类型')
    task_module = models.CharField(max_length=200, verbose_name='任务模块路径')
    task_function = models.CharField(max_length=100, verbose_name='任务函数名')
    task_args = models.TextField(blank=True, verbose_name='任务参数(JSON格式)')
    
    # 周期任务配置
    interval_seconds = models.IntegerField(null=True, blank=True, verbose_name='间隔秒数')
    
    # 定时任务配置
    cron_expression = models.CharField(max_length=100, blank=True, verbose_name='Cron表达式')
    
    # 一次性任务配置
    execute_at = models.DateTimeField(null=True, blank=True, verbose_name='执行时间')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    priority = models.IntegerField(default=5, verbose_name='优先级(1-10)')
    max_retries = models.IntegerField(default=3, verbose_name='最大重试次数')
    timeout_seconds = models.IntegerField(default=300, verbose_name='超时时间(秒)')
    
    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name='最后执行时间')
    next_run_at = models.DateTimeField(null=True, blank=True, verbose_name='下次执行时间')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'scheduled_task'
        verbose_name = '定时任务'
        verbose_name_plural = '定时任务'
        ordering = ['-created_at']
    
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


class TaskExecution(models.Model):
    """任务执行记录表"""
    STATUS_CHOICES = [
        ('pending', '等待执行'),
        ('running', '执行中'),
        ('success', '执行成功'),
        ('failed', '执行失败'),
        ('timeout', '执行超时'),
        ('cancelled', '已取消'),
    ]
    
    task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, verbose_name='关联任务')
    execution_id = models.CharField(max_length=100, unique=True, verbose_name='执行ID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='执行状态')
    
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration_seconds = models.FloatField(null=True, blank=True, verbose_name='执行时长(秒)')
    
    result_data = models.TextField(blank=True, verbose_name='执行结果')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    traceback_info = models.TextField(blank=True, verbose_name='错误堆栈')
    
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    worker_name = models.CharField(max_length=100, blank=True, verbose_name='执行节点')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_execution'
        verbose_name = '任务执行记录'
        verbose_name_plural = '任务执行记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.task.name} - {self.execution_id}'
    
    @property
    def is_finished(self):
        """是否已完成"""
        return self.status in ['success', 'failed', 'timeout', 'cancelled']
    
    def calculate_duration(self):
        """计算执行时长"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = delta.total_seconds()
            return self.duration_seconds
        return None


class DataUpdateTask(models.Model):
    """数据更新任务表"""
    DATA_TYPES = [
        ('stock_basic', '股票基础信息'),
        ('stock_realtime', '股票实时数据'),
        ('stock_history', '股票历史数据'),
        ('stock_minute', '股票分时数据'),
        ('market_realtime', '大盘实时数据'),
        ('market_history', '大盘历史数据'),
        ('industry_data', '行业数据'),
        ('concept_data', '概念数据'),
        ('money_flow', '资金流向'),
        ('dragon_tiger', '龙虎榜'),
        ('margin_trading', '两融数据'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='任务名称')
    data_type = models.CharField(max_length=30, choices=DATA_TYPES, verbose_name='数据类型')
    target_codes = models.TextField(blank=True, verbose_name='目标代码(多个用逗号分隔)')
    update_frequency = models.IntegerField(verbose_name='更新频率(分钟)')
    is_market_time_only = models.BooleanField(default=True, verbose_name='仅交易时间执行')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    last_update_time = models.DateTimeField(null=True, blank=True, verbose_name='最后更新时间')
    last_update_count = models.IntegerField(default=0, verbose_name='最后更新数量')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'data_update_task'
        verbose_name = '数据更新任务'
        verbose_name_plural = '数据更新任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_target_codes_list(self):
        """获取目标代码列表"""
        if self.target_codes:
            return [code.strip() for code in self.target_codes.split(',') if code.strip()]
        return []
    
    def set_target_codes_list(self, codes_list):
        """设置目标代码列表"""
        self.target_codes = ','.join(codes_list)


class TaskLog(models.Model):
    """任务日志表"""
    LOG_LEVELS = [
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]
    
    task_execution = models.ForeignKey(TaskExecution, on_delete=models.CASCADE, null=True, blank=True, verbose_name='任务执行记录')
    level = models.CharField(max_length=10, choices=LOG_LEVELS, verbose_name='日志级别')
    message = models.TextField(verbose_name='日志消息')
    module = models.CharField(max_length=100, blank=True, verbose_name='模块名')
    function = models.CharField(max_length=100, blank=True, verbose_name='函数名')
    line_number = models.IntegerField(null=True, blank=True, verbose_name='行号')
    extra_data = models.TextField(blank=True, verbose_name='额外数据(JSON格式)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_log'
        verbose_name = '任务日志'
        verbose_name_plural = '任务日志'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.level} - {self.message[:50]}'


class TaskDependency(models.Model):
    """任务依赖关系表"""
    parent_task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='child_dependencies', verbose_name='父任务')
    child_task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='parent_dependencies', verbose_name='子任务')
    dependency_type = models.CharField(max_length=20, choices=[
        ('success', '成功后执行'),
        ('failure', '失败后执行'),
        ('always', '总是执行'),
    ], default='success', verbose_name='依赖类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'task_dependency'
        verbose_name = '任务依赖关系'
        verbose_name_plural = '任务依赖关系'
        unique_together = ['parent_task', 'child_task']
    
    def __str__(self):
        return f'{self.parent_task.name} -> {self.child_task.name}'