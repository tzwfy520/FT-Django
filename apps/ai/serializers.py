from rest_framework import serializers
from .models import AIModel, AIAnalysis, AIConversation, AITemplate


class AIModelSerializer(serializers.ModelSerializer):
    """AI模型序列化器"""
    
    class Meta:
        model = AIModel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIAnalysisSerializer(serializers.ModelSerializer):
    """AI分析序列化器"""
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIConversationSerializer(serializers.ModelSerializer):
    """AI对话序列化器"""
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIConversation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AITemplateSerializer(serializers.ModelSerializer):
    """AI模板序列化器"""
    
    class Meta:
        model = AITemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIAnalysisRequestSerializer(serializers.Serializer):
    """AI分析请求序列化器"""
    model_id = serializers.IntegerField(help_text="AI模型ID")
    analysis_type = serializers.ChoiceField(
        choices=['technical', 'fundamental', 'sentiment', 'prediction'],
        help_text="分析类型"
    )
    stock_codes = serializers.ListField(
        child=serializers.CharField(max_length=10),
        help_text="股票代码列表"
    )
    parameters = serializers.JSONField(
        required=False,
        help_text="分析参数"
    )
    template_id = serializers.IntegerField(
        required=False,
        help_text="使用的模板ID"
    )


class AIConversationRequestSerializer(serializers.Serializer):
    """AI对话请求序列化器"""
    model_id = serializers.IntegerField(help_text="AI模型ID")
    message = serializers.CharField(
        max_length=2000,
        help_text="用户消息"
    )
    context = serializers.JSONField(
        required=False,
        help_text="对话上下文"
    )
    session_id = serializers.CharField(
        max_length=100,
        required=False,
        help_text="会话ID"
    )


class AIStatsSerializer(serializers.Serializer):
    """AI统计序列化器"""
    total_models = serializers.IntegerField()
    active_models = serializers.IntegerField()
    total_analyses = serializers.IntegerField()
    total_conversations = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_response_time = serializers.DecimalField(max_digits=10, decimal_places=2)
    popular_analysis_types = serializers.ListField(
        child=serializers.DictField()
    )