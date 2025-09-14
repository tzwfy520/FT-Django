from rest_framework import serializers
from .models import ApiProvider, ApiToken, ApiInterface, ApiCallLog


class ApiProviderSerializer(serializers.ModelSerializer):
    """API提供商序列化器"""
    
    class Meta:
        model = ApiProvider
        fields = ['id', 'name', 'display_name', 'base_url', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApiTokenSerializer(serializers.ModelSerializer):
    """API Token序列化器"""
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    
    class Meta:
        model = ApiToken
        fields = ['id', 'provider', 'provider_name', 'token', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'token': {'write_only': True}
        }
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)


class ApiTokenListSerializer(serializers.ModelSerializer):
    """API Token列表序列化器（不包含敏感信息）"""
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    token_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = ApiToken
        fields = ['id', 'provider', 'provider_name', 'token_preview', 'is_active', 'created_at', 'updated_at']
    
    def get_token_preview(self, obj):
        """返回Token的预览（只显示前4位和后4位）"""
        if len(obj.token) > 8:
            return f"{obj.token[:4]}****{obj.token[-4:]}"
        return "****"


class ApiInterfaceSerializer(serializers.ModelSerializer):
    """API接口配置序列化器"""
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    
    class Meta:
        model = ApiInterface
        fields = [
            'id', 'provider', 'provider_name', 'name', 'model', 
            'temperature', 'max_tokens', 'purposes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if not 0.0 <= value <= 2.0:
            raise serializers.ValidationError("温度参数必须在0.0到2.0之间")
        return value
    
    def validate_max_tokens(self, value):
        """验证最大令牌数"""
        if value < 1:
            raise serializers.ValidationError("最大令牌数必须大于0")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApiCallLogSerializer(serializers.ModelSerializer):
    """API调用日志序列化器"""
    interface_name = serializers.CharField(source='interface.name', read_only=True)
    provider_name = serializers.CharField(source='interface.provider.display_name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ApiCallLog
        fields = [
            'id', 'interface', 'interface_name', 'provider_name', 'user_name',
            'request_data', 'response_data', 'status_code', 'response_time',
            'prompt_tokens', 'completion_tokens', 'total_tokens', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ApiCallRequest(serializers.Serializer):
    """API调用请求序列化器"""
    interface_id = serializers.IntegerField()
    message = serializers.CharField()
    
    def validate_interface_id(self, value):
        """验证接口ID"""
        try:
            interface = ApiInterface.objects.get(id=value, is_active=True)
            if not interface.provider.is_active:
                raise serializers.ValidationError("API提供商未启用")
            return value
        except ApiInterface.DoesNotExist:
            raise serializers.ValidationError("接口不存在或未启用")


class ApiCallResponse(serializers.Serializer):
    """API调用响应序列化器"""
    success = serializers.BooleanField()
    data = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
    log_id = serializers.IntegerField(required=False)