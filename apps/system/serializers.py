from rest_framework import serializers
from .models import SystemConfig, DataSource, SystemLog


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    
    class Meta:
        model = SystemConfig
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DataSourceSerializer(serializers.ModelSerializer):
    """数据源序列化器"""
    
    class Meta:
        model = DataSource
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'api_key': {'write_only': True},
        }


class SystemLogSerializer(serializers.ModelSerializer):
    """系统日志序列化器"""
    
    class Meta:
        model = SystemLog
        fields = '__all__'
        read_only_fields = ('created_at',)


class SystemConfigUpdateSerializer(serializers.ModelSerializer):
    """系统配置更新序列化器"""
    
    class Meta:
        model = SystemConfig
        fields = ('config_value', 'description')
    
    def validate_config_value(self, value):
        """验证配置值格式"""
        if not isinstance(value, (str, int, float, bool, dict, list)):
            raise serializers.ValidationError("配置值格式不正确")
        return value


class DataSourceTestSerializer(serializers.Serializer):
    """数据源测试序列化器"""
    source_type = serializers.ChoiceField(
        choices=['database', 'api', 'file'],
        help_text="数据源类型"
    )
    connection_string = serializers.CharField(
        max_length=500,
        help_text="连接字符串"
    )
    username = serializers.CharField(
        max_length=100,
        required=False,
        help_text="用户名"
    )
    password = serializers.CharField(
        max_length=100,
        required=False,
        help_text="密码"
    )
    api_key = serializers.CharField(
        max_length=200,
        required=False,
        help_text="API密钥"
    )
    timeout = serializers.IntegerField(
        default=30,
        help_text="超时时间（秒）"
    )


class SystemMonitorSerializer(serializers.Serializer):
    """系统监控序列化器"""
    cpu_usage = serializers.DecimalField(max_digits=5, decimal_places=2)
    memory_usage = serializers.DecimalField(max_digits=5, decimal_places=2)
    disk_usage = serializers.DecimalField(max_digits=5, decimal_places=2)
    network_io = serializers.DictField()
    database_connections = serializers.IntegerField()
    active_tasks = serializers.IntegerField()
    system_load = serializers.DecimalField(max_digits=5, decimal_places=2)
    uptime = serializers.IntegerField()
    timestamp = serializers.DateTimeField()


class SystemStatsSerializer(serializers.Serializer):
    """系统统计序列化器"""
    total_stocks = serializers.IntegerField()
    total_data_points = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    total_analyses = serializers.IntegerField()
    system_uptime = serializers.IntegerField()
    data_freshness = serializers.DictField()
    performance_metrics = serializers.DictField()
    error_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class SystemTestResultSerializer(serializers.Serializer):
    """系统测试结果序列化器"""
    test_name = serializers.CharField()
    status = serializers.ChoiceField(choices=['pass', 'fail', 'warning'])
    message = serializers.CharField()
    details = serializers.JSONField(required=False)
    execution_time = serializers.DecimalField(max_digits=10, decimal_places=3)
    timestamp = serializers.DateTimeField()