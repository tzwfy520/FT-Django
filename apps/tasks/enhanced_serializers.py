from rest_framework import serializers
from django.contrib.auth.models import User
from .enhanced_models import (
    TaskCategory, TaskDefinition, TaskExecution, TaskLog, 
    TaskDependency, TaskSchedule, TaskMetrics
)
from croniter import croniter
from datetime import datetime, timedelta
import json


class TaskCategorySerializer(serializers.ModelSerializer):
    """任务分类序列化器"""
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskCategory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_task_count(self, obj):
        """获取分类下的任务数量"""
        return obj.taskdefinition_set.filter(is_active=True).count()


class TaskDefinitionListSerializer(serializers.ModelSerializer):
    """任务定义列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskDefinition
        fields = [
            'id', 'name', 'description', 'task_type', 'category_name', 
            'priority', 'status', 'is_active', 'success_rate',
            'total_executions', 'success_executions', 'failed_executions',
            'last_execution_time', 'next_execution_time', 'created_by_name', 'created_at'
        ]


class TaskDefinitionDetailSerializer(serializers.ModelSerializer):
    """任务定义详情序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    task_args_dict = serializers.SerializerMethodField()
    success_rate = serializers.ReadOnlyField()
    next_run_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskDefinition
        fields = '__all__'
        read_only_fields = (
            'total_executions', 'success_executions', 'failed_executions',
            'last_execution_time', 'created_at', 'updated_at'
        )
    
    def get_task_args_dict(self, obj):
        """获取任务参数字典"""
        return obj.get_task_args()
    
    def get_next_run_time(self, obj):
        """计算下次执行时间"""
        if obj.task_type == 'periodic' and obj.interval_seconds:
            if obj.last_execution_time:
                return obj.last_execution_time + timedelta(seconds=obj.interval_seconds)
            else:
                return datetime.now() + timedelta(seconds=obj.interval_seconds)
        elif obj.task_type == 'scheduled' and obj.cron_expression:
            try:
                cron = croniter(obj.cron_expression, datetime.now())
                return cron.get_next(datetime)
            except:
                return None
        elif obj.task_type == 'immediate' and obj.execute_at:
            return obj.execute_at
        return None
    
    def validate_cron_expression(self, value):
        """验证Cron表达式"""
        if value:
            try:
                croniter(value)
            except:
                raise serializers.ValidationError("无效的Cron表达式")
        return value
    
    def validate_task_args(self, value):
        """验证任务参数JSON格式"""
        if value:
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("任务参数必须是有效的JSON格式")
        return value


class TaskExecutionListSerializer(serializers.ModelSerializer):
    """任务执行记录列表序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_type = serializers.CharField(source='task.task_type', read_only=True)
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True)
    
    class Meta:
        model = TaskExecution
        fields = [
            'id', 'execution_id', 'task_name', 'task_type', 'status',
            'scheduled_time', 'start_time', 'end_time', 'duration_seconds',
            'retry_count', 'trigger_type', 'triggered_by_name', 'worker_name',
            'created_at'
        ]


class TaskExecutionDetailSerializer(serializers.ModelSerializer):
    """任务执行记录详情序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_description = serializers.CharField(source='task.description', read_only=True)
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True)
    is_finished = serializers.ReadOnlyField()
    is_successful = serializers.ReadOnlyField()
    can_retry = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskExecution
        fields = '__all__'
        read_only_fields = (
            'task', 'execution_id', 'scheduled_time', 'start_time', 
            'end_time', 'duration_seconds', 'created_at'
        )


class TaskLogSerializer(serializers.ModelSerializer):
    """任务日志序列化器"""
    task_name = serializers.CharField(source='task_execution.task.name', read_only=True)
    execution_id = serializers.CharField(source='task_execution.execution_id', read_only=True)
    
    class Meta:
        model = TaskLog
        fields = '__all__'
        read_only_fields = ('timestamp',)


class TaskDependencySerializer(serializers.ModelSerializer):
    """任务依赖关系序列化器"""
    parent_task_name = serializers.CharField(source='parent_task.name', read_only=True)
    child_task_name = serializers.CharField(source='child_task.name', read_only=True)
    
    class Meta:
        model = TaskDependency
        fields = '__all__'
        read_only_fields = ('created_at',)
    
    def validate(self, data):
        """验证依赖关系"""
        parent_task = data.get('parent_task')
        child_task = data.get('child_task')
        
        if parent_task == child_task:
            raise serializers.ValidationError("任务不能依赖自己")
        
        # 检查循环依赖
        if self._has_circular_dependency(parent_task, child_task):
            raise serializers.ValidationError("存在循环依赖")
        
        return data
    
    def _has_circular_dependency(self, parent, child):
        """检查是否存在循环依赖"""
        visited = set()
        
        def dfs(task):
            if task.id in visited:
                return task == parent
            visited.add(task.id)
            
            for dep in task.child_dependencies.all():
                if dfs(dep.child_task):
                    return True
            return False
        
        return dfs(child)


class TaskScheduleSerializer(serializers.ModelSerializer):
    """任务调度配置序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    next_run_time_calculated = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskSchedule
        fields = '__all__'
        read_only_fields = ('last_run_time', 'created_at', 'updated_at')
    
    def get_next_run_time_calculated(self, obj):
        """计算下次运行时间"""
        if obj.schedule_type == 'cron' and obj.cron_expression:
            try:
                cron = croniter(obj.cron_expression, datetime.now())
                return cron.get_next(datetime)
            except:
                return None
        elif obj.schedule_type == 'interval' and obj.interval_seconds:
            if obj.last_run_time:
                return obj.last_run_time + timedelta(seconds=obj.interval_seconds)
            else:
                return datetime.now() + timedelta(seconds=obj.interval_seconds)
        elif obj.schedule_type == 'date' and obj.run_date:
            return obj.run_date
        return None
    
    def validate_cron_expression(self, value):
        """验证Cron表达式"""
        if value:
            try:
                croniter(value)
            except:
                raise serializers.ValidationError("无效的Cron表达式")
        return value


class TaskMetricsSerializer(serializers.ModelSerializer):
    """任务执行指标序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskMetrics
        fields = '__all__'
        read_only_fields = ('created_at',)


class TaskExecutionCreateSerializer(serializers.Serializer):
    """创建任务执行序列化器"""
    task_id = serializers.UUIDField()
    trigger_type = serializers.ChoiceField(choices=[
        ('manual', '手动触发'),
        ('api', 'API触发'),
    ], default='manual')
    scheduled_time = serializers.DateTimeField(required=False)
    task_args = serializers.JSONField(required=False)
    
    def validate_task_id(self, value):
        """验证任务ID"""
        try:
            task = TaskDefinition.objects.get(id=value, is_active=True)
            return value
        except TaskDefinition.DoesNotExist:
            raise serializers.ValidationError("任务不存在或已禁用")


class TaskStatsSerializer(serializers.Serializer):
    """任务统计序列化器"""
    total_tasks = serializers.IntegerField()
    active_tasks = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    running_executions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    
    # 按状态统计
    pending_executions = serializers.IntegerField()
    success_executions = serializers.IntegerField()
    failed_executions = serializers.IntegerField()
    
    # 按类型统计
    periodic_tasks = serializers.IntegerField()
    scheduled_tasks = serializers.IntegerField()
    immediate_tasks = serializers.IntegerField()
    special_tasks = serializers.IntegerField()
    
    # 最近执行统计
    recent_executions = serializers.IntegerField()
    recent_success_rate = serializers.FloatField()


class TaskExecutionFilterSerializer(serializers.Serializer):
    """任务执行记录筛选序列化器"""
    task_id = serializers.UUIDField(required=False)
    task_type = serializers.ChoiceField(
        choices=['periodic', 'scheduled', 'immediate', 'special', 'dependent'],
        required=False
    )
    status = serializers.ChoiceField(
        choices=['pending', 'running', 'success', 'failed', 'timeout', 'cancelled'],
        required=False
    )
    trigger_type = serializers.ChoiceField(
        choices=['auto', 'manual', 'api', 'dependency'],
        required=False
    )
    worker_name = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    duration_min = serializers.FloatField(required=False)
    duration_max = serializers.FloatField(required=False)
    
    def validate(self, data):
        """验证筛选条件"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始时间不能大于结束时间")
        
        duration_min = data.get('duration_min')
        duration_max = data.get('duration_max')
        
        if duration_min and duration_max and duration_min > duration_max:
            raise serializers.ValidationError("最小执行时长不能大于最大执行时长")
        
        return data