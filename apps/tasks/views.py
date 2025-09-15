from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json
import logging

from .models import TaskDefinition, TaskCategory, TaskExecution, ScheduledTask
from .enhanced_models import TaskExecutionEnhanced, TaskScheduleEnhanced, TaskDependencyEnhanced
from apps.stocks.models import StockBasicInfo

logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """API视图基类"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"API请求处理异常: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'服务器内部错误: {str(e)}',
                'data': None
            }, status=500)
    
    def success_response(self, data=None, message='操作成功'):
        """成功响应"""
        return JsonResponse({
            'success': True,
            'message': message,
            'data': data
        })
    
    def error_response(self, message='操作失败', status=400):
        """错误响应"""
        return JsonResponse({
            'success': False,
            'message': message,
            'data': None
        }, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class TaskDefinitionView(BaseAPIView):
    """任务定义API"""
    
    def get(self, request):
        """获取任务定义列表"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            trigger_method = request.GET.get('trigger_method', '').strip()
            task_target = request.GET.get('task_target', '').strip()
            is_active = request.GET.get('is_active', '').strip()
            search = request.GET.get('search', '').strip()
            
            # 构建查询条件
            queryset = TaskDefinition.objects.all()
            
            if trigger_method:
                queryset = queryset.filter(trigger_method=trigger_method)
            
            if task_target:
                queryset = queryset.filter(task_target=task_target)
            
            if is_active:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | 
                    Q(description__icontains=search)
                )
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            tasks = []
            for task in page_obj:
                # 获取最近执行记录
                latest_execution = TaskExecutionEnhanced.objects.filter(task=task).order_by('-created_at').first()
                
                tasks.append({
                    'id': task.id,
                    'name': task.name,
                    'trigger_method': task.trigger_method,
                    'task_target': task.task_target,
                    'stock_targets': task.get_stock_targets() if task.is_stock_data_task() else None,
                    'description': task.description,
                    'task_args': task.task_args,
                    'is_active': task.is_active,
                    'priority': task.priority,
                    'timeout': task.timeout_seconds,
                    'retry_count': task.max_retries,
                    'latest_execution': {
                        'status': latest_execution.status if latest_execution else None,
                        'started_at': latest_execution.start_time.strftime('%Y-%m-%d %H:%M:%S') if latest_execution and latest_execution.start_time else None,
                        'completed_at': latest_execution.end_time.strftime('%Y-%m-%d %H:%M:%S') if latest_execution and latest_execution.end_time else None
                    } if latest_execution else None,
                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return self.success_response({
                'tasks': tasks,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取任务定义列表失败: {str(e)}")
            return self.error_response('获取任务列表失败')
    
    def post(self, request):
        """创建任务定义"""
        try:
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            trigger_method = data.get('trigger_method', '').strip()
            task_target = data.get('task_target', '').strip()
            description = data.get('description', '').strip()
            task_args = data.get('task_args', {})
            stock_targets = data.get('stock_targets', [])
            priority = data.get('priority', 5)
            timeout = data.get('timeout', 3600)
            retry_count = data.get('retry_count', 3)
            
            if not name:
                return self.error_response('请提供任务名称')
            
            if not trigger_method:
                return self.error_response('请提供触发方式')
            
            if not task_target:
                return self.error_response('请提供任务目标')
            
            # 如果任务目标是股票数据更新，必须提供股票目标列表
            if task_target == 'stock_data_update' and not stock_targets:
                return self.error_response('股票数据更新任务必须提供股票目标列表')
            
            # 检查任务名称是否已存在
            if TaskDefinition.objects.filter(name=name).exists():
                return self.error_response('任务名称已存在')
            
            # 创建任务定义
            task = TaskDefinition.objects.create(
                name=name,
                trigger_method=trigger_method,
                task_target=task_target,
                description=description,
                task_args=task_args,
                priority=priority,
                timeout_seconds=timeout,
                max_retries=retry_count
            )
            
            # 如果有股票目标列表，设置股票目标
            if stock_targets:
                task.set_stock_targets(stock_targets)
                task.save()
            
            return self.success_response({
                'id': task.id,
                'name': task.name,
                'trigger_method': task.trigger_method,
                'task_target': task.task_target,
                'stock_targets': task.get_stock_targets() if task.is_stock_data_task() else None,
                'description': task.description,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '任务创建成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"创建任务定义失败: {str(e)}")
            return self.error_response('创建任务失败')
    
    def put(self, request):
        """更新任务定义"""
        try:
            data = json.loads(request.body)
            task_id = data.get('id')
            
            if not task_id:
                return self.error_response('请提供任务ID')
            
            try:
                task = TaskDefinition.objects.get(id=task_id)
            except TaskDefinition.DoesNotExist:
                return self.error_response('任务不存在', 404)
            
            # 更新字段
            if 'name' in data:
                name = data['name'].strip()
                if name and name != task.name:
                    if TaskDefinition.objects.filter(name=name).exclude(id=task_id).exists():
                        return self.error_response('任务名称已存在')
                    task.name = name
            
            if 'description' in data:
                task.description = data['description'].strip()
            
            if 'trigger_method' in data:
                task.trigger_method = data['trigger_method']
            
            if 'task_target' in data:
                task.task_target = data['task_target']
            
            if 'task_args' in data:
                task.task_args = data['task_args']
            
            if 'stock_targets' in data:
                stock_targets = data['stock_targets']
                if isinstance(stock_targets, list):
                    task.set_stock_targets(stock_targets)
            
            if 'is_active' in data:
                task.is_active = data['is_active']
            
            if 'priority' in data:
                task.priority = data['priority']
            
            if 'timeout' in data:
                task.timeout = data['timeout']
            
            if 'retry_count' in data:
                task.retry_count = data['retry_count']
            
            task.save()
            
            return self.success_response({
                'id': task.id,
                'name': task.name,
                'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '任务更新成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"更新任务定义失败: {str(e)}")
            return self.error_response('更新任务失败')
    
    def delete(self, request):
        """删除任务定义"""
        try:
            data = json.loads(request.body)
            task_id = data.get('id')
            
            if not task_id:
                return self.error_response('请提供任务ID')
            
            try:
                task = TaskDefinition.objects.get(id=task_id)
            except TaskDefinition.DoesNotExist:
                return self.error_response('任务不存在', 404)
            
            # 检查是否有正在执行的任务
            running_executions = task.executions.filter(status='running').count()
            if running_executions > 0:
                return self.error_response('任务正在执行中，无法删除')
            
            task_name = task.name
            task.delete()
            
            return self.success_response(message=f'任务 "{task_name}" 删除成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"删除任务定义失败: {str(e)}")
            return self.error_response('删除任务失败')


@method_decorator(csrf_exempt, name='dispatch')
class TaskExecutionView(BaseAPIView):
    """任务执行API"""
    
    def get(self, request):
        """获取任务执行记录"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            task_id = request.GET.get('task_id')
            status = request.GET.get('status', '').strip()
            date_from = request.GET.get('date_from', '').strip()
            date_to = request.GET.get('date_to', '').strip()
            
            # 构建查询条件
            queryset = TaskExecutionEnhanced.objects.select_related('task')
            
            if task_id:
                queryset = queryset.filter(task_id=task_id)
            
            if status:
                queryset = queryset.filter(status=status)
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                    queryset = queryset.filter(created_at__gte=date_from_obj)
                except ValueError:
                    return self.error_response('开始日期格式错误，请使用YYYY-MM-DD格式')
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                    queryset = queryset.filter(created_at__lt=date_to_obj)
                except ValueError:
                    return self.error_response('结束日期格式错误，请使用YYYY-MM-DD格式')
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            executions = []
            for execution in page_obj:
                duration = None
                if execution.started_at and execution.completed_at:
                    duration = int((execution.completed_at - execution.started_at).total_seconds())
                
                executions.append({
                    'id': execution.id,
                    'task': {
                        'id': execution.task.id,
                        'name': execution.task.name,
                        'task_type': execution.task.task_type
                    },
                    'status': execution.status,
                    'parameters': execution.parameters,
                    'result': execution.result,
                    'error_message': execution.error_message,
                    'duration': duration,
                    'created_at': execution.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'started_at': execution.started_at.strftime('%Y-%m-%d %H:%M:%S') if execution.started_at else None,
                    'completed_at': execution.completed_at.strftime('%Y-%m-%d %H:%M:%S') if execution.completed_at else None
                })
            
            return self.success_response({
                'executions': executions,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取任务执行记录失败: {str(e)}")
            return self.error_response('获取执行记录失败')
    
    def post(self, request):
        """手动执行任务"""
        try:
            data = json.loads(request.body)
            
            task_id = data.get('task_id')
            parameters = data.get('parameters', {})
            
            if not task_id:
                return self.error_response('请提供任务ID')
            
            try:
                task = TaskDefinition.objects.get(id=task_id, is_active=True)
            except TaskDefinition.DoesNotExist:
                return self.error_response('任务不存在或已停用', 404)
            
            # 检查是否有正在执行的同类任务
            running_count = TaskExecution.objects.filter(
                task=task,
                status='running'
            ).count()
            
            if running_count > 0:
                return self.error_response('该任务正在执行中，请等待完成后再试')
            
            # 创建执行记录
            execution = TaskExecution.objects.create(
                task=task,
                execution_id=f"exec_{task.id}_{int(datetime.now().timestamp())}",
                status='pending'
            )
            
            # 触发异步任务执行
            try:
                # 根据任务定义执行相应的Celery任务
                if task.task_function == 'collect_specific_stocks_history_data':
                    from apps.stocks.tasks import collect_specific_stocks_history_data
                    
                    # 从参数中获取股票代码
                    symbols = parameters.get('symbols', ['000002'])
                    periods = parameters.get('periods', ['daily'])
                    
                    # 提交Celery任务
                    celery_task = collect_specific_stocks_history_data.delay(
                        symbols=symbols,
                        periods=periods
                    )
                    
                    # 更新执行记录状态
                    execution.status = 'running'
                    execution.start_time = datetime.now()
                    execution.save()
                    
                    logger.info(f"已提交Celery任务: {celery_task.id}，执行ID: {execution.execution_id}")
                    
                else:
                    logger.warning(f"未知的任务函数: {task.task_function}")
                    execution.status = 'failed'
                    execution.error_message = f"未知的任务函数: {task.task_function}"
                    execution.save()
                    
            except Exception as e:
                logger.error(f"启动任务失败: {str(e)}")
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.save()
            
            return self.success_response({
                'execution_id': execution.id,
                'task_name': task.name,
                'status': 'pending',
                'created_at': execution.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '任务已提交执行')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"执行任务失败: {str(e)}")
            return self.error_response('执行任务失败')


@method_decorator(csrf_exempt, name='dispatch')
class TaskScheduleView(BaseAPIView):
    """任务调度API"""
    
    def get(self, request):
        """获取任务调度列表"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            task_id = request.GET.get('task_id')
            is_active = request.GET.get('is_active', '').strip()
            
            # 构建查询条件
            queryset = TaskScheduleEnhanced.objects.select_related('task')
            
            if task_id:
                queryset = queryset.filter(task_id=task_id)
            
            if is_active:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            schedules = []
            for schedule in page_obj:
                schedules.append({
                    'id': schedule.id,
                    'task': {
                        'id': schedule.task.id,
                        'name': schedule.task.name,
                        'task_type': schedule.task.task_type
                    },
                    'schedule_type': schedule.schedule_type,
                    'cron_expression': schedule.cron_expression,
                    'interval_seconds': schedule.interval_seconds,
                    'is_active': schedule.is_active,
                    'next_run_time': schedule.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if schedule.next_run_time else None,
                    'last_run_time': schedule.last_run_time.strftime('%Y-%m-%d %H:%M:%S') if schedule.last_run_time else None,
                    'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': schedule.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return self.success_response({
                'schedules': schedules,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取任务调度列表失败: {str(e)}")
            return self.error_response('获取调度列表失败')
    
    def post(self, request):
        """创建任务调度"""
        try:
            data = json.loads(request.body)
            
            task_id = data.get('task_id')
            schedule_type = data.get('schedule_type', '').strip()
            cron_expression = data.get('cron_expression', '').strip()
            interval_seconds = data.get('interval_seconds')
            
            if not task_id:
                return self.error_response('请提供任务ID')
            
            if not schedule_type:
                return self.error_response('请提供调度类型')
            
            try:
                task = TaskDefinition.objects.get(id=task_id)
            except TaskDefinition.DoesNotExist:
                return self.error_response('任务不存在', 404)
            
            # 验证调度参数
            if schedule_type == 'cron' and not cron_expression:
                return self.error_response('Cron调度需要提供cron表达式')
            
            if schedule_type == 'interval' and not interval_seconds:
                return self.error_response('间隔调度需要提供间隔秒数')
            
            # 检查是否已存在调度
            if TaskSchedule.objects.filter(task=task, is_active=True).exists():
                return self.error_response('该任务已存在活跃的调度配置')
            
            # 创建调度
            schedule = TaskSchedule.objects.create(
                task=task,
                schedule_type=schedule_type,
                cron_expression=cron_expression if schedule_type == 'cron' else None,
                interval_seconds=interval_seconds if schedule_type == 'interval' else None
            )
            
            return self.success_response({
                'id': schedule.id,
                'task_name': task.name,
                'schedule_type': schedule.schedule_type,
                'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '调度创建成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"创建任务调度失败: {str(e)}")
            return self.error_response('创建调度失败')


@require_http_methods(["GET"])
def task_stats(request):
    """任务统计信息"""
    try:
        # 基础统计
        total_tasks = TaskDefinition.objects.count()
        active_tasks = TaskDefinition.objects.filter(is_active=True).count()
        total_executions = TaskExecutionEnhanced.objects.count()
        
        # 执行状态统计
        execution_stats = TaskExecutionEnhanced.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # 最近24小时执行统计
        yesterday = datetime.now() - timedelta(hours=24)
        recent_executions = TaskExecutionEnhanced.objects.filter(
            created_at__gte=yesterday
        ).count()
        
        # 成功率统计
        completed_executions = TaskExecutionEnhanced.objects.filter(status='success').count()
        success_rate = round(completed_executions / total_executions * 100, 2) if total_executions > 0 else 0
        
        # 按任务目标统计
        task_target_stats = TaskDefinition.objects.values('task_target').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 正在运行的任务
        running_tasks = TaskExecutionEnhanced.objects.filter(status='running').count()
        
        # 调度统计
        total_schedules = TaskScheduleEnhanced.objects.count()
        active_schedules = TaskScheduleEnhanced.objects.filter(is_active=True).count()
        
        stats = {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'total_executions': total_executions,
            'recent_executions': recent_executions,
            'running_tasks': running_tasks,
            'success_rate': success_rate,
            'total_schedules': total_schedules,
            'active_schedules': active_schedules,
            'execution_stats': list(execution_stats),
            'task_target_stats': list(task_target_stats)
        }
        
        return JsonResponse({
            'success': True,
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取任务统计信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取统计信息失败',
            'data': None
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TaskControlView(BaseAPIView):
    """任务控制API"""
    
    def post(self, request):
        """任务控制操作（停止、重启等）"""
        try:
            data = json.loads(request.body)
            
            action = data.get('action', '').strip()
            execution_id = data.get('execution_id')
            
            if not action:
                return self.error_response('请提供操作类型')
            
            if not execution_id:
                return self.error_response('请提供执行ID')
            
            try:
                execution = TaskExecution.objects.get(id=execution_id)
            except TaskExecution.DoesNotExist:
                return self.error_response('执行记录不存在', 404)
            
            if action == 'stop':
                if execution.status != 'running':
                    return self.error_response('只能停止正在运行的任务')
                
                # 这里应该实现实际的任务停止逻辑
                execution.status = 'cancelled'
                execution.completed_at = datetime.now()
                execution.error_message = '任务被手动停止'
                execution.save()
                
                return self.success_response(message='任务已停止')
            
            elif action == 'retry':
                if execution.status not in ['failed', 'cancelled']:
                    return self.error_response('只能重试失败或已取消的任务')
                
                # 创建新的执行记录
                new_execution = TaskExecution.objects.create(
                    task=execution.task,
                    parameters=execution.parameters,
                    status='pending'
                )
                
                return self.success_response({
                    'new_execution_id': new_execution.id
                }, '任务已重新提交执行')
            
            else:
                return self.error_response('不支持的操作类型')
                
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"任务控制操作失败: {str(e)}")
            return self.error_response('操作失败')