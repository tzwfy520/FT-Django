from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
import uuid

from .enhanced_models import (
    TaskDefinition, TaskExecutionEnhanced, TaskLogEnhanced, 
    TaskDependencyEnhanced, TaskScheduleEnhanced, TaskMetricsEnhanced
)
from .models import TaskCategory
from .enhanced_serializers import (
    TaskCategorySerializer, TaskDefinitionListSerializer, TaskDefinitionDetailSerializer,
    TaskExecutionListSerializer, TaskExecutionDetailSerializer, TaskLogSerializer,
    TaskDependencySerializer, TaskScheduleSerializer, TaskMetricsSerializer,
    TaskExecutionCreateSerializer, TaskStatsSerializer, TaskExecutionFilterSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页配置"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskExecutionFilter(filters.FilterSet):
    """任务执行记录过滤器"""
    task_name = filters.CharFilter(field_name='task__name', lookup_expr='icontains')
    trigger_method = filters.ChoiceFilter(field_name='task__trigger_method', choices=[
        ('periodic', '周期任务'),
        ('scheduled', '定时任务'),
        ('immediate', '立即任务'),
        ('special', '特殊任务'),
        ('dependent', '依赖任务')
    ])
    status = filters.ChoiceFilter(choices=[
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('timeout', '超时'),
        ('cancelled', '已取消')
    ])
    trigger_type = filters.ChoiceFilter(choices=[
        ('auto', '自动触发'),
        ('manual', '手动触发'),
        ('api', 'API触发'),
        ('dependency', '依赖触发')
    ])
    worker_name = filters.CharFilter(lookup_expr='icontains')
    start_date = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    end_date = filters.DateTimeFilter(field_name='end_time', lookup_expr='lte')
    duration_min = filters.NumberFilter(field_name='duration_seconds', lookup_expr='gte')
    duration_max = filters.NumberFilter(field_name='duration_seconds', lookup_expr='lte')
    date_range = filters.DateFromToRangeFilter(field_name='created_at')
    
    class Meta:
        model = TaskExecutionEnhanced
        fields = ['task', 'status', 'trigger_type', 'worker_name']


class TaskCategoryViewSet(viewsets.ModelViewSet):
    """任务分类管理视图集"""
    queryset = TaskCategory.objects.all().order_by('name')
    serializer_class = TaskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """获取分类下的任务列表"""
        category = self.get_object()
        tasks = TaskDefinition.objects.filter(category=category, is_active=True)
        serializer = TaskDefinitionListSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskDefinitionViewSet(viewsets.ModelViewSet):
    """任务定义管理视图集"""
    queryset = TaskDefinition.objects.select_related('category', 'created_by').all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'trigger_method', 'priority', 'status', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'last_execution_time', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskDefinitionListSerializer
        return TaskDefinitionDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """手动执行任务"""
        task = self.get_object()
        
        if not task.is_active:
            return Response(
                {'error': '任务已禁用，无法执行'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建任务执行记录
        execution = TaskExecution.objects.create(
            task=task,
            execution_id=str(uuid.uuid4()),
            trigger_type='manual',
            triggered_by=request.user,
            scheduled_time=timezone.now(),
            status='pending'
        )
        
        # 提交到任务调度器
        scheduler = TaskScheduler()
        try:
            scheduler.execute_task(task.id, execution.id)
            return Response({
                'message': '任务已提交执行',
                'execution_id': execution.execution_id
            })
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            return Response(
                {'error': f'任务执行失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换任务启用/禁用状态"""
        task = self.get_object()
        task.is_active = not task.is_active
        task.save()
        
        return Response({
            'message': f'任务已{"启用" if task.is_active else "禁用"}',
            'is_active': task.is_active
        })
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """获取任务的执行记录"""
        task = self.get_object()
        executions = TaskExecution.objects.filter(task=task).order_by('-created_at')
        
        page = self.paginate_queryset(executions)
        if page is not None:
            serializer = TaskExecutionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TaskExecutionListSerializer(executions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def dependencies(self, request, pk=None):
        """获取任务的依赖关系"""
        task = self.get_object()
        
        # 父依赖（当前任务依赖的任务）
        parent_deps = TaskDependency.objects.filter(child_task=task).select_related('parent_task')
        # 子依赖（依赖当前任务的任务）
        child_deps = TaskDependency.objects.filter(parent_task=task).select_related('child_task')
        
        return Response({
            'parent_dependencies': TaskDependencySerializer(parent_deps, many=True).data,
            'child_dependencies': TaskDependencySerializer(child_deps, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """获取任务执行指标"""
        task = self.get_object()
        
        # 基本统计
        executions = TaskExecution.objects.filter(task=task)
        total_count = executions.count()
        success_count = executions.filter(status='success').count()
        failed_count = executions.filter(status='failed').count()
        
        # 平均执行时间
        avg_duration = executions.filter(
            status='success',
            duration_seconds__isnull=False
        ).aggregate(avg_duration=Avg('duration_seconds'))['avg_duration'] or 0
        
        # 最近7天的执行情况
        recent_date = timezone.now() - timedelta(days=7)
        recent_executions = executions.filter(created_at__gte=recent_date)
        recent_success = recent_executions.filter(status='success').count()
        recent_total = recent_executions.count()
        
        return Response({
            'total_executions': total_count,
            'success_executions': success_count,
            'failed_executions': failed_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
            'average_duration': round(avg_duration, 2),
            'recent_success_rate': (recent_success / recent_total * 100) if recent_total > 0 else 0,
            'recent_executions': recent_total
        })
    
    @action(detail=True, methods=['get'])
    def target_details(self, request, pk=None):
        """根据任务目标获取对应的详情清单"""
        task = self.get_object()
        task_target = task.task_target
        
        # 根据不同的任务目标返回对应的清单
        if task_target == 'stock_data_update':
            # 获取股票清单
            from apps.stocks.models import Stock
            stocks = Stock.objects.filter(is_active=True).values('code', 'name', 'market')
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'items': list(stocks),
                'total_count': stocks.count()
            })
        
        elif task_target == 'industry_sector_update':
            # 获取行业板块清单
            from apps.stocks.models import IndustrySector
            sectors = IndustrySector.objects.filter(is_active=True).values('code', 'name')
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'items': list(sectors),
                'total_count': sectors.count()
            })
        
        elif task_target == 'concept_sector_update':
            # 获取概念板块清单
            from apps.stocks.models import ConceptSector
            sectors = ConceptSector.objects.filter(is_active=True).values('code', 'name')
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'items': list(sectors),
                'total_count': sectors.count()
            })
        
        elif task_target == 'market_data_update':
            # 获取大盘数据清单
            market_indices = [
                {'code': '000001', 'name': '上证指数'},
                {'code': '399001', 'name': '深证成指'},
                {'code': '399006', 'name': '创业板指'},
                {'code': '000300', 'name': '沪深300'},
                {'code': '000905', 'name': '中证500'},
                {'code': '000852', 'name': '中证1000'}
            ]
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'items': market_indices,
                'total_count': len(market_indices)
            })
        
        elif task_target == 'ai_analysis':
            # AI分析任务的详情
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'description': '执行AI分析相关任务，包括数据分析、模型训练等',
                'items': [],
                'total_count': 0
            })
        
        else:
            # 其他类型任务
            return Response({
                'task_target': task_target,
                'task_target_display': task.get_task_target_display(),
                'description': '其他类型任务',
                'items': [],
                'total_count': 0
            })


class TaskExecutionViewSet(viewsets.ModelViewSet):
    """任务执行记录管理视图集"""
    queryset = TaskExecutionEnhanced.objects.select_related('task', 'triggered_by').all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskExecutionFilter
    ordering_fields = ['created_at', 'start_time', 'end_time', 'duration_seconds']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskExecutionListSerializer
        return TaskExecutionDetailSerializer
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试失败的任务"""
        execution = self.get_object()
        
        if execution.status not in ['failed', 'timeout', 'cancelled']:
            return Response(
                {'error': '只能重试失败、超时或已取消的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 创建新的执行记录
        new_execution = TaskExecution.objects.create(
            task=execution.task,
            execution_id=str(uuid.uuid4()),
            trigger_type='manual',
            triggered_by=request.user,
            scheduled_time=timezone.now(),
            status='pending',
            retry_count=execution.retry_count + 1
        )
        
        # 提交到任务调度器
        scheduler = TaskScheduler()
        try:
            scheduler.execute_task(execution.task.id, new_execution.id)
            return Response({
                'message': '任务重试已提交',
                'execution_id': new_execution.execution_id
            })
        except Exception as e:
            new_execution.status = 'failed'
            new_execution.error_message = str(e)
            new_execution.save()
            return Response(
                {'error': f'任务重试失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消正在运行的任务"""
        execution = self.get_object()
        
        if execution.status not in ['pending', 'running']:
            return Response(
                {'error': '只能取消等待中或运行中的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新状态
        execution.status = 'cancelled'
        execution.end_time = timezone.now()
        if execution.start_time:
            execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
        execution.save()
        
        # TODO: 实际取消任务执行（需要与Celery集成）
        
        return Response({'message': '任务已取消'})
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """获取任务执行日志"""
        execution = self.get_object()
        logs = TaskLog.objects.filter(task_execution=execution).order_by('timestamp')
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = TaskLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TaskLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取任务执行统计信息"""
        # 基本统计
        total_tasks = TaskDefinition.objects.count()
        active_tasks = TaskDefinition.objects.filter(is_active=True).count()
        total_executions = TaskExecution.objects.count()
        running_executions = TaskExecution.objects.filter(status='running').count()
        
        # 成功率统计
        finished_executions = TaskExecution.objects.filter(
            status__in=['success', 'failed']
        )
        success_executions = finished_executions.filter(status='success').count()
        total_finished = finished_executions.count()
        success_rate = (success_executions / total_finished * 100) if total_finished > 0 else 0
        
        # 按状态统计
        pending_executions = TaskExecution.objects.filter(status='pending').count()
        failed_executions = TaskExecution.objects.filter(status='failed').count()
        
        # 按类型统计
        periodic_tasks = TaskDefinition.objects.filter(task_type='periodic').count()
        scheduled_tasks = TaskDefinition.objects.filter(task_type='scheduled').count()
        immediate_tasks = TaskDefinition.objects.filter(task_type='immediate').count()
        special_tasks = TaskDefinition.objects.filter(task_type='special').count()
        
        # 最近24小时统计
        recent_date = timezone.now() - timedelta(hours=24)
        recent_executions = TaskExecution.objects.filter(created_at__gte=recent_date)
        recent_success = recent_executions.filter(status='success').count()
        recent_total = recent_executions.count()
        recent_success_rate = (recent_success / recent_total * 100) if recent_total > 0 else 0
        
        stats_data = {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'total_executions': total_executions,
            'running_executions': running_executions,
            'success_rate': round(success_rate, 2),
            'pending_executions': pending_executions,
            'success_executions': success_executions,
            'failed_executions': failed_executions,
            'periodic_tasks': periodic_tasks,
            'scheduled_tasks': scheduled_tasks,
            'immediate_tasks': immediate_tasks,
            'special_tasks': special_tasks,
            'recent_executions': recent_total,
            'recent_success_rate': round(recent_success_rate, 2)
        }
        
        serializer = TaskStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_retry(self, request):
        """批量重试失败的任务"""
        execution_ids = request.data.get('execution_ids', [])
        
        if not execution_ids:
            return Response(
                {'error': '请提供要重试的任务执行ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        executions = TaskExecution.objects.filter(
            id__in=execution_ids,
            status__in=['failed', 'timeout', 'cancelled']
        )
        
        retry_count = 0
        scheduler = TaskScheduler()
        
        for execution in executions:
            try:
                new_execution = TaskExecution.objects.create(
                    task=execution.task,
                    execution_id=str(uuid.uuid4()),
                    trigger_type='manual',
                    triggered_by=request.user,
                    scheduled_time=timezone.now(),
                    status='pending',
                    retry_count=execution.retry_count + 1
                )
                
                scheduler.execute_task(execution.task.id, new_execution.id)
                retry_count += 1
            except Exception:
                continue
        
        return Response({
            'message': f'已成功重试 {retry_count} 个任务',
            'retry_count': retry_count
        })


class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    """任务日志查看视图集"""
    queryset = TaskLogEnhanced.objects.select_related('task_execution__task').all()
    serializer_class = TaskLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task_execution', 'level']
    ordering = ['-timestamp']


class TaskDependencyViewSet(viewsets.ModelViewSet):
    """任务依赖关系管理视图集"""
    queryset = TaskDependencyEnhanced.objects.select_related('parent_task', 'child_task').all()
    serializer_class = TaskDependencySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent_task', 'child_task', 'dependency_type']


class TaskScheduleViewSet(viewsets.ModelViewSet):
    """任务调度配置管理视图集"""
    queryset = TaskScheduleEnhanced.objects.select_related('task').all()
    serializer_class = TaskScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', 'schedule_type', 'is_active']
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换调度配置启用/禁用状态"""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        
        return Response({
            'message': f'调度配置已{"启用" if schedule.is_active else "禁用"}',
            'is_active': schedule.is_active
        })


class TaskMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """任务执行指标查看视图集"""
    queryset = TaskMetricsEnhanced.objects.select_related('task').all()
    serializer_class = TaskMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']
    ordering = ['-created_at']