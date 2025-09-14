from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import AIAnalysisRecord, AIModelConfig
from .serializers import AIAnalysisRecordSerializer, AIModelConfigSerializer


class AIAnalysisRecordViewSet(viewsets.ModelViewSet):
    """AI分析记录视图集"""
    
    serializer_class = AIAnalysisRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['analysis_type', 'status', 'stock_code']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """只返回当前用户的记录"""
        return AIAnalysisRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """创建时自动设置用户"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取统计信息"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'processing': queryset.filter(status='processing').count(),
            'completed': queryset.filter(status='completed').count(),
            'failed': queryset.filter(status='failed').count(),
            'by_type': {}
        }
        
        # 按分析类型统计
        for choice in AIAnalysisRecord.ANALYSIS_TYPE_CHOICES:
            type_code = choice[0]
            type_name = choice[1]
            count = queryset.filter(analysis_type=type_code).count()
            stats['by_type'][type_code] = {
                'name': type_name,
                'count': count
            }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def rerun(self, request, pk=None):
        """重新运行分析"""
        record = self.get_object()
        record.status = 'pending'
        record.result = None
        record.save()
        
        # TODO: 这里可以触发异步任务重新分析
        
        return Response({'message': '已重新提交分析任务'})


class AIModelConfigViewSet(viewsets.ModelViewSet):
    """AI模型配置视图集"""
    
    queryset = AIModelConfig.objects.all()
    serializer_class = AIModelConfigSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active_models(self, request):
        """获取激活的模型配置"""
        active_models = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_models, many=True)
        return Response(serializer.data)