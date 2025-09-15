import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from django.utils import timezone
from celery import current_app
from celery.result import AsyncResult

from .models import DataUpdateTask, TaskExecution, TaskLog
from apps.stocks.tasks import collect_stock_history_qfq_data, collect_specific_stocks_history_data
from apps.stocks.models import StockBasicInfo

logger = logging.getLogger(__name__)


class HistoryDataTaskService:
    """历史数据采集任务服务"""
    
    def __init__(self):
        self.task_type = 'stock_history_qfq'
    
    def create_history_data_task(self, name: str = "历史数据-前复权", 
                                data_type: str = None,
                                is_active: bool = True,
                                target_codes: str = '') -> DataUpdateTask:
        """
        创建历史数据采集任务
        
        Args:
            name: 任务名称
            data_type: 数据类型
            is_active: 是否启用
            
        Returns:
            DataUpdateTask: 创建的任务对象
        """
        try:
            if data_type is None:
                data_type = self.task_type
                
            task, created = DataUpdateTask.objects.get_or_create(
                data_type=data_type,
                defaults={
                    'name': name,
                    'target_codes': target_codes,
                    'update_frequency': 60,  # 60分钟更新一次
                    'is_market_time_only': False,  # 不限制交易时间
                    'is_active': is_active
                }
            )
            
            if created:
                logger.info(f"创建历史数据采集任务: {task.name}")
            else:
                logger.info(f"历史数据采集任务已存在: {task.name}")
                
            return task
            
        except Exception as e:
            logger.error(f"创建历史数据采集任务失败: {e}")
            raise
    
    def create_task(self, task_type: str = 'stock_history_qfq', 
                   stock_codes: List[str] = None, 
                   user_id: int = 1) -> Dict[str, Any]:
        """
        创建并执行历史数据采集任务
        
        Args:
            task_type: 任务类型
            stock_codes: 股票代码列表
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 任务创建结果
        """
        try:
            # 创建或获取任务定义
            target_codes_str = ','.join(stock_codes) if stock_codes else ''
            task = self.create_history_data_task(
                name=f"历史数据-{task_type}",
                data_type=task_type,
                is_active=True,
                target_codes=target_codes_str
            )
            
            # 执行任务
            result = self.execute_history_data_task(
                task_id=task.id,
                symbols=stock_codes,
                periods=['daily', 'weekly', 'monthly'],
                triggered_by='api'
            )
            
            return {
                'success': True,
                'data': {
                    'execution_id': result['execution_id'],
                    'celery_task_id': result.get('celery_task_id'),
                    'status': result['status'],
                    'symbols_count': result.get('symbols_count', 0),
                    'periods': result.get('periods', [])
                },
                'message': result['message']
            }
            
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise
    
    def execute_history_data_task(self, task_id: int, symbols: List[str] = None, 
                                 periods: List[str] = None, 
                                 triggered_by: str = 'manual') -> Dict[str, Any]:
        """
        执行历史数据采集任务
        
        Args:
            task_id: 任务ID
            symbols: 股票代码列表，为None时采集所有活跃股票
            periods: 数据周期列表，默认为['daily', 'weekly', 'monthly']
            triggered_by: 触发方式 ('manual', 'scheduled', 'api')
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            # 获取任务定义
            task = DataUpdateTask.objects.get(id=task_id)
            
            if not task.is_active:
                raise ValueError(f"任务 {task.name} 未启用")
            
            # 生成执行ID
            execution_id = f"history_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{task_id}"
            
            logger.info(f"开始执行历史数据采集任务: {task.name}, 执行ID: {execution_id}")
            
            # 设置默认参数
            if periods is None:
                periods = ['daily', 'weekly', 'monthly']
            
            if symbols is None:
                # 获取所有活跃股票代码
                active_stocks = StockBasicInfo.objects.filter(is_active=True)
                symbols = [stock.ts_code for stock in active_stocks]
                logger.info(f"未指定股票代码，将采集所有活跃股票数据，共 {len(symbols)} 只")
            
            # 提交Celery任务
            celery_task = collect_specific_stocks_history_data.delay(
                symbols=symbols,
                periods=periods
            )
            
            logger.info(f"已提交Celery任务: {celery_task.id}")
            
            # 更新任务最后执行时间
            task.last_update_time = timezone.now()
            task.save()
            
            return {
                'execution_id': execution_id,
                'celery_task_id': celery_task.id,
                'status': 'running',
                'message': f'历史数据采集任务已启动，执行ID: {execution_id}',
                'symbols_count': len(symbols),
                'periods': periods
            }
            
        except DataUpdateTask.DoesNotExist:
            error_msg = f"任务ID {task_id} 不存在"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            logger.error(f"执行历史数据采集任务失败: {e}")
            
            return {
                'execution_id': None,
                'status': 'failed',
                'message': f'执行失败: {str(e)}'
            }
    
    def check_task_status(self, celery_task_id: str) -> Dict[str, Any]:
        """
        检查任务执行状态
        
        Args:
            celery_task_id: Celery任务ID
            
        Returns:
            Dict[str, Any]: 任务状态信息
        """
        try:
            celery_result = AsyncResult(celery_task_id)
            
            result = {
                'celery_task_id': celery_task_id,
                'status': celery_result.status,
                'ready': celery_result.ready()
            }
            
            if celery_result.ready():
                if celery_result.successful():
                    task_result = celery_result.result
                    result['task_result'] = task_result
                    result['status'] = 'completed'
                    
                    if isinstance(task_result, dict):
                        result['message'] = f"任务执行完成: 处理股票 {task_result.get('total_stocks', 0)} 只，" \
                                          f"成功 {task_result.get('success_stocks', 0)} 只，" \
                                          f"采集记录 {task_result.get('total_records', 0)} 条"
                    else:
                        result['message'] = "任务执行完成"
                else:
                    # 任务失败
                    result['status'] = 'failed'
                    result['error_message'] = str(celery_result.result)
                    result['message'] = f"任务执行失败: {celery_result.result}"
            else:
                result['message'] = "任务正在执行中"
            
            return result
            
        except Exception as e:
            logger.error(f"检查任务状态失败: {e}")
            return {
                'celery_task_id': celery_task_id,
                'status': 'error',
                'message': f'检查状态失败: {str(e)}'
            }
    
    def get_task_logs(self, celery_task_id: str) -> List[Dict[str, Any]]:
        """
        获取任务执行日志（简化版本，返回基本信息）
        
        Args:
            celery_task_id: Celery任务ID
            
        Returns:
            List[Dict[str, Any]]: 日志列表
        """
        try:
            celery_result = AsyncResult(celery_task_id)
            
            logs = []
            logs.append({
                'level': 'info',
                'message': f'任务ID: {celery_task_id}',
                'created_at': timezone.now()
            })
            
            logs.append({
                'level': 'info',
                'message': f'任务状态: {celery_result.status}',
                'created_at': timezone.now()
            })
            
            if celery_result.ready():
                if celery_result.successful():
                    logs.append({
                        'level': 'info',
                        'message': f'任务执行成功: {celery_result.result}',
                        'created_at': timezone.now()
                    })
                else:
                    logs.append({
                        'level': 'error',
                        'message': f'任务执行失败: {celery_result.result}',
                        'created_at': timezone.now()
                    })
            
            return logs
            
        except Exception as e:
            logger.error(f"获取任务日志失败: {e}")
            return [{
                'level': 'error',
                'message': f'获取日志失败: {str(e)}',
                'created_at': timezone.now()
            }]
    
    def get_recent_executions(self, task_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的任务执行记录（简化版本）
        
        Args:
            task_id: 任务ID
            limit: 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 执行记录列表
        """
        try:
            # 获取任务信息
            task = DataUpdateTask.objects.get(id=task_id)
            
            # 返回基本任务信息
            return [{
                'id': task.id,
                'name': task.name,
                'data_type': task.data_type,
                'last_update_time': task.last_update_time,
                'is_active': task.is_active,
                'message': '历史执行记录功能已简化，仅显示任务基本信息'
            }]
            
        except DataUpdateTask.DoesNotExist:
            logger.error(f"任务ID {task_id} 不存在")
            return []
        except Exception as e:
            logger.error(f"获取执行记录失败: {e}")
            return []
    
    def cancel_task(self, celery_task_id: str) -> Dict[str, Any]:
        """
        取消正在执行的任务
        
        Args:
            celery_task_id: Celery任务ID
            
        Returns:
            Dict[str, Any]: 取消结果
        """
        try:
            # 检查任务状态
            celery_result = AsyncResult(celery_task_id)
            
            if celery_result.ready():
                return {
                    'status': 'already_finished',
                    'message': f'任务已完成，状态: {celery_result.status}'
                }
            
            # 取消Celery任务
            current_app.control.revoke(celery_task_id, terminate=True)
            
            logger.info(f"已取消Celery任务: {celery_task_id}")
            
            return {
                'status': 'cancelled',
                'message': '任务已取消'
            }
            
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            return {
                'status': 'error',
                'message': f'取消任务失败: {str(e)}'
            }


# 创建全局实例
history_data_task_service = HistoryDataTaskService()