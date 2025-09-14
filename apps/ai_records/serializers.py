from rest_framework import serializers
from .models import AIAnalysisRecord, AIModelConfig


class AIAnalysisRecordSerializer(serializers.ModelSerializer):
    """AI分析记录序列化器"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AIAnalysisRecord
        fields = [
            'id', 'user', 'user_name', 'analysis_type', 'analysis_type_display',
            'stock_code', 'prompt', 'result', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_prompt(self, value):
        """验证提示内容"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError('分析提示内容至少需要10个字符')
        return value


class AIModelConfigSerializer(serializers.ModelSerializer):
    """AI模型配置序列化器"""
    
    class Meta:
        model = AIModelConfig
        fields = [
            'id', 'name', 'api_key', 'base_url', 'model_name',
            'max_tokens', 'temperature', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True}  # API密钥只写不读
        }
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if not 0 <= value <= 2:
            raise serializers.ValidationError('温度参数必须在0-2之间')
        return value
    
    def validate_max_tokens(self, value):
        """验证最大令牌数"""
        if value < 100 or value > 32000:
            raise serializers.ValidationError('最大令牌数必须在100-32000之间')
        return value


class AIAnalysisCreateSerializer(serializers.ModelSerializer):
    """创建AI分析记录的序列化器"""
    
    class Meta:
        model = AIAnalysisRecord
        fields = ['analysis_type', 'stock_code', 'prompt']
    
    def validate(self, attrs):
        """验证数据"""
        analysis_type = attrs.get('analysis_type')
        stock_code = attrs.get('stock_code')
        
        # 如果是股票分析，必须提供股票代码
        if analysis_type == 'stock' and not stock_code:
            raise serializers.ValidationError('股票分析必须提供股票代码')
        
        return attrs