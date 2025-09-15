from rest_framework import serializers
from .models import TaskDefinition
from .enhanced_models import TaskExecutionEnhanced, TaskScheduleEnhanced


class TaskDefinitionSerializer(serializers.ModelSerializer):
    """任务定义序列化器"""
    
    class Meta:
        model = TaskDefinition
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TaskExecutionSerializer(serializers.ModelSerializer):
    """任务执行记录序列化器"""
    task_name = serializers.CharField(source='task.name', read_only=True)
    trigger_method = serializers.CharField(source='task.trigger_method', read_only=True)
    task_target = serializers.CharField(source='task.task_target', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskExecutionEnhanced
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
    trigger_method = serializers.CharField(source='task.trigger_method', read_only=True)
    task_target = serializers.CharField(source='task.task_target', read_only=True)
    next_run_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskScheduleEnhanced
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
    stock_targets_list = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        write_only=True,
        help_text="股票目标列表，仅当任务目标为股票数据更新时需要"
    )
    
    class Meta:
        model = TaskDefinition
        fields = ('name', 'description', 'trigger_method', 'task_target', 'task_args', 'stock_targets_list', 'is_active')
    
    def validate_task_args(self, value):
        """验证参数格式"""
        if value:
            try:
                import json
                if isinstance(value, str):
                    json.loads(value)
                elif not isinstance(value, dict):
                    raise serializers.ValidationError("参数必须是JSON对象格式")
            except json.JSONDecodeError:
                raise serializers.ValidationError("参数格式不正确")
        return value
    
    def validate(self, attrs):
        """整体验证"""
        task_target = attrs.get('task_target')
        stock_targets_list = attrs.get('stock_targets_list')
        
        # 如果任务目标是股票数据更新，必须提供股票目标列表
        if task_target == 'stock_data_update' and not stock_targets_list:
            raise serializers.ValidationError({
                'stock_targets_list': '当任务目标为股票数据更新时，必须提供股票目标列表'
            })
        
        return attrs
    
    def create(self, validated_data):
        """创建任务"""
        stock_targets_list = validated_data.pop('stock_targets_list', [])
        task = super().create(validated_data)
        
        if stock_targets_list:
            task.set_stock_targets(stock_targets_list)
            task.save()
        
        return task


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