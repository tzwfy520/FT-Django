from rest_framework import serializers
from .models import TaskDefinition, TaskExecution, TaskSchedule


class TaskDefinitionSerializer(serializers.ModelSerializer):
    """任务定义序列化器"""
    
    class Meta:
        model = TaskDefinition
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TaskExecutionSerializer(serializers.ModelSerializer):
    """任务执行记录序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_type = serializers.CharField(source='task.task_type', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskExecution
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_duration(self, obj):
        """计算任务执行时长"""
        if obj.start_time and obj.end_time:
            return (obj.end_time - obj.start_time).total_seconds()
        return None


class TaskScheduleSerializer(serializers.ModelSerializer):
    """任务调度序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_type = serializers.CharField(source='task.task_type', read_only=True)
    next_run_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskSchedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_next_run_time(self, obj):
        """计算下次执行时间"""
        # 这里可以根据cron表达式计算下次执行时间
        # 暂时返回None，后续可以集成croniter库
        return None


class TaskControlSerializer(serializers.Serializer):
    """任务控制序列化器"""
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'restart', 'pause', 'resume'],
        help_text="操作类型"
    )
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="任务ID列表"
    )
    force = serializers.BooleanField(
        default=False,
        help_text="是否强制执行"
    )


class TaskStatsSerializer(serializers.Serializer):
    """任务统计序列化器"""
    total_tasks = serializers.IntegerField()
    active_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    failed_tasks = serializers.IntegerField()
    scheduled_tasks = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_execution_time = serializers.DecimalField(max_digits=10, decimal_places=2)
    

class TaskCreateSerializer(serializers.ModelSerializer):
    """任务创建序列化器"""
    
    class Meta:
        model = TaskDefinition
        fields = ('name', 'description', 'task_type', 'parameters', 'is_active')
    
    def validate_parameters(self, value):
        """验证参数格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("参数必须是JSON对象格式")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """任务更新序列化器"""
    
    class Meta:
        model = TaskDefinition
        fields = ('name', 'description', 'parameters', 'is_active')
        
    def validate_parameters(self, value):
        """验证参数格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("参数必须是JSON对象格式")
        return value