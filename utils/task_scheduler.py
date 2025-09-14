from celery import Celery
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import logging
from django.conf import settings
from django.utils import timezone
import json
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    RETRY = 'retry'
    REVOKED = 'revoked'


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'


class TaskType(Enum):
    """任务类型枚举"""
    PERIODIC = 'periodic'  # 周期任务
    SCHEDULED = 'scheduled'  # 定时任务
    IMMEDIATE = 'immediate'  # 立即执行任务
    DEPENDENT = 'dependent'  # 依赖任务


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.celery_app = None
        self.registered_tasks = {}
        self.task_configs = {}
        self._init_celery()
    
    def _init_celery(self):
        """初始化Celery应用"""
        try:
            from stock_analysis.celery import app
            self.celery_app = app
            logger.info("Celery app initialized")
        except Exception as e:
            logger.error(f"Error initializing Celery app: {str(e)}")
    
    def register_task(self, task_name: str, task_func: Callable, config: Dict[str, Any] = None):
        """
        注册任务
        
        Args:
            task_name: 任务名称
            task_func: 任务函数
            config: 任务配置
        """
        self.registered_tasks[task_name] = task_func
        self.task_configs[task_name] = config or {}
        logger.info(f"Task '{task_name}' registered")
    
    def create_periodic_task(self, 
                           task_name: str,
                           schedule: Dict[str, Any],
                           args: List[Any] = None,
                           kwargs: Dict[str, Any] = None,
                           priority: TaskPriority = TaskPriority.NORMAL,
                           enabled: bool = True) -> Dict[str, Any]:
        """
        创建周期任务
        
        Args:
            task_name: 任务名称
            schedule: 调度配置
            args: 任务参数
            kwargs: 任务关键字参数
            priority: 任务优先级
            enabled: 是否启用
        
        Returns:
            Dict[str, Any]: 任务配置
        """
        task_config = {
            'task': task_name,
            'schedule': schedule,
            'args': args or [],
            'kwargs': kwargs or {},
            'options': {
                'priority': priority.value,
                'expires': 3600,  # 1小时过期
            },
            'enabled': enabled,
            'type': TaskType.PERIODIC.value,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            # 保存任务配置到数据库
            self._save_task_config(task_name, task_config)
            logger.info(f"Periodic task '{task_name}' created")
            return task_config
        except Exception as e:
            logger.error(f"Error creating periodic task: {str(e)}")
            return {}
    
    def create_scheduled_task(self,
                            task_name: str,
                            eta: datetime,
                            args: List[Any] = None,
                            kwargs: Dict[str, Any] = None,
                            priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        创建定时任务
        
        Args:
            task_name: 任务名称
            eta: 执行时间
            args: 任务参数
            kwargs: 任务关键字参数
            priority: 任务优先级
        
        Returns:
            str: 任务ID
        """
        try:
            if self.celery_app and task_name in self.registered_tasks:
                result = self.celery_app.send_task(
                    task_name,
                    args=args or [],
                    kwargs=kwargs or {},
                    eta=eta,
                    priority=self._get_priority_value(priority)
                )
                
                # 记录任务执行信息
                self._log_task_execution({
                    'task_id': result.id,
                    'task_name': task_name,
                    'type': TaskType.SCHEDULED.value,
                    'eta': eta.isoformat(),
                    'args': args or [],
                    'kwargs': kwargs or {},
                    'priority': priority.value,
                    'status': TaskStatus.PENDING.value,
                    'created_at': datetime.now().isoformat()
                })
                
                logger.info(f"Scheduled task '{task_name}' created with ID: {result.id}")
                return result.id
        except Exception as e:
            logger.error(f"Error creating scheduled task: {str(e)}")
        return ""
    
    def execute_immediate_task(self,
                             task_name: str,
                             args: List[Any] = None,
                             kwargs: Dict[str, Any] = None,
                             priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """
        立即执行任务
        
        Args:
            task_name: 任务名称
            args: 任务参数
            kwargs: 任务关键字参数
            priority: 任务优先级
        
        Returns:
            str: 任务ID
        """
        try:
            if self.celery_app and task_name in self.registered_tasks:
                result = self.celery_app.send_task(
                    task_name,
                    args=args or [],
                    kwargs=kwargs or {},
                    priority=self._get_priority_value(priority)
                )
                
                # 记录任务执行信息
                self._log_task_execution({
                    'task_id': result.id,
                    'task_name': task_name,
                    'type': TaskType.IMMEDIATE.value,
                    'args': args or [],
                    'kwargs': kwargs or {},
                    'priority': priority.value,
                    'status': TaskStatus.PENDING.value,
                    'created_at': datetime.now().isoformat()
                })
                
                logger.info(f"Immediate task '{task_name}' executed with ID: {result.id}")
                return result.id
        except Exception as e:
            logger.error(f"Error executing immediate task: {str(e)}")
        return ""
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            Dict[str, Any]: 任务状态信息
        """
        try:
            if self.celery_app:
                result = self.celery_app.AsyncResult(task_id)
                return {
                    'task_id': task_id,
                    'status': result.status,
                    'result': result.result,
                    'traceback': result.traceback,
                    'date_done': result.date_done.isoformat() if result.date_done else None
                }
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
        return {}
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """
        撤销任务
        
        Args:
            task_id: 任务ID
            terminate: 是否强制终止
        
        Returns:
            bool: 是否成功
        """
        try:
            if self.celery_app:
                self.celery_app.control.revoke(task_id, terminate=terminate)
                
                # 更新任务状态
                self._update_task_status(task_id, TaskStatus.REVOKED)
                
                logger.info(f"Task '{task_id}' revoked")
                return True
        except Exception as e:
            logger.error(f"Error revoking task: {str(e)}")
        return False
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        获取活跃任务列表
        
        Returns:
            List[Dict[str, Any]]: 活跃任务列表
        """
        try:
            if self.celery_app:
                inspect = self.celery_app.control.inspect()
                active_tasks = inspect.active()
                
                tasks = []
                for worker, task_list in (active_tasks or {}).items():
                    for task in task_list:
                        tasks.append({
                            'worker': worker,
                            'task_id': task.get('id'),
                            'task_name': task.get('name'),
                            'args': task.get('args'),
                            'kwargs': task.get('kwargs'),
                            'time_start': task.get('time_start')
                        })
                
                return tasks
        except Exception as e:
            logger.error(f"Error getting active tasks: {str(e)}")
        return []
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        获取计划任务列表
        
        Returns:
            List[Dict[str, Any]]: 计划任务列表
        """
        try:
            if self.celery_app:
                inspect = self.celery_app.control.inspect()
                scheduled_tasks = inspect.scheduled()
                
                tasks = []
                for worker, task_list in (scheduled_tasks or {}).items():
                    for task in task_list:
                        tasks.append({
                            'worker': worker,
                            'task_id': task.get('request', {}).get('id'),
                            'task_name': task.get('request', {}).get('task'),
                            'args': task.get('request', {}).get('args'),
                            'kwargs': task.get('request', {}).get('kwargs'),
                            'eta': task.get('eta'),
                            'priority': task.get('request', {}).get('priority')
                        })
                
                return tasks
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {str(e)}")
        return []
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        获取工作节点统计信息
        
        Returns:
            Dict[str, Any]: 工作节点统计信息
        """
        try:
            if self.celery_app:
                inspect = self.celery_app.control.inspect()
                stats = inspect.stats()
                return stats or {}
        except Exception as e:
            logger.error(f"Error getting worker stats: {str(e)}")
        return {}
    
    def create_task_chain(self, tasks: List[Dict[str, Any]]) -> str:
        """
        创建任务链
        
        Args:
            tasks: 任务列表，每个任务包含name, args, kwargs
        
        Returns:
            str: 任务链ID
        """
        try:
            if self.celery_app and tasks:
                from celery import chain
                
                task_signatures = []
                for task in tasks:
                    signature = self.celery_app.signature(
                        task['name'],
                        args=task.get('args', []),
                        kwargs=task.get('kwargs', {})
                    )
                    task_signatures.append(signature)
                
                task_chain = chain(*task_signatures)
                result = task_chain.apply_async()
                
                logger.info(f"Task chain created with ID: {result.id}")
                return result.id
        except Exception as e:
            logger.error(f"Error creating task chain: {str(e)}")
        return ""
    
    def create_task_group(self, tasks: List[Dict[str, Any]]) -> str:
        """
        创建任务组（并行执行）
        
        Args:
            tasks: 任务列表
        
        Returns:
            str: 任务组ID
        """
        try:
            if self.celery_app and tasks:
                from celery import group
                
                task_signatures = []
                for task in tasks:
                    signature = self.celery_app.signature(
                        task['name'],
                        args=task.get('args', []),
                        kwargs=task.get('kwargs', {})
                    )
                    task_signatures.append(signature)
                
                task_group = group(*task_signatures)
                result = task_group.apply_async()
                
                logger.info(f"Task group created with ID: {result.id}")
                return result.id
        except Exception as e:
            logger.error(f"Error creating task group: {str(e)}")
        return ""
    
    def _get_priority_value(self, priority: TaskPriority) -> int:
        """
        获取优先级数值
        
        Args:
            priority: 优先级枚举
        
        Returns:
            int: 优先级数值
        """
        priority_map = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 5,
            TaskPriority.HIGH: 8,
            TaskPriority.CRITICAL: 10
        }
        return priority_map.get(priority, 5)
    
    def _save_task_config(self, task_name: str, config: Dict[str, Any]):
        """
        保存任务配置到数据库
        
        Args:
            task_name: 任务名称
            config: 任务配置
        """
        try:
            from utils.database import db_manager
            
            data = {
                'name': task_name,
                'task_type': config.get('type', TaskType.PERIODIC.value),
                'schedule_config': json.dumps(config.get('schedule', {})),
                'args': json.dumps(config.get('args', [])),
                'kwargs': json.dumps(config.get('kwargs', {})),
                'priority': config.get('options', {}).get('priority', TaskPriority.NORMAL.value),
                'enabled': config.get('enabled', True),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            db_manager.execute_upsert('tasks_scheduledtask', data, ['name'])
        except Exception as e:
            logger.error(f"Error saving task config: {str(e)}")
    
    def _log_task_execution(self, execution_info: Dict[str, Any]):
        """
        记录任务执行信息
        
        Args:
            execution_info: 执行信息
        """
        try:
            from utils.database import db_manager
            
            data = {
                'task_id': execution_info.get('task_id'),
                'task_name': execution_info.get('task_name'),
                'task_type': execution_info.get('type'),
                'args': json.dumps(execution_info.get('args', [])),
                'kwargs': json.dumps(execution_info.get('kwargs', {})),
                'priority': execution_info.get('priority'),
                'status': execution_info.get('status'),
                'scheduled_time': execution_info.get('eta'),
                'created_at': datetime.now()
            }
            
            db_manager.execute_insert('tasks_taskexecution', data)
        except Exception as e:
            logger.error(f"Error logging task execution: {str(e)}")
    
    def _update_task_status(self, task_id: str, status: TaskStatus):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态
        """
        try:
            from utils.database import db_manager
            
            query = """
                UPDATE tasks_taskexecution 
                SET status = %s, updated_at = %s 
                WHERE task_id = %s
            """
            
            with db_manager.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (status.value, datetime.now(), task_id))
                    connection.commit()
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")


class StockDataTaskScheduler(TaskScheduler):
    """股票数据任务调度器"""
    
    def __init__(self):
        super().__init__()
        self._register_stock_tasks()
    
    def _register_stock_tasks(self):
        """注册股票相关任务"""
        # 注册股票数据更新任务
        stock_tasks = {
            'update_stock_realtime_data': {
                'description': '更新股票实时数据',
                'default_schedule': {'seconds': 30},  # 每30秒执行一次
                'trading_hours_only': True
            },
            'update_market_data': {
                'description': '更新市场数据',
                'default_schedule': {'minutes': 1},  # 每分钟执行一次
                'trading_hours_only': True
            },
            'analyze_stocks': {
                'description': '股票分析',
                'default_schedule': {'hour': 16, 'minute': 30},  # 每日16:30执行
                'trading_days_only': True
            },
            'update_stock_history': {
                'description': '更新股票历史数据',
                'default_schedule': {'hour': 17, 'minute': 0},  # 每日17:00执行
                'trading_days_only': True
            },
            'update_industry_data': {
                'description': '更新行业板块数据',
                'default_schedule': {'minutes': 5},  # 每5分钟执行一次
                'trading_hours_only': True
            },
            'update_concept_data': {
                'description': '更新概念板块数据',
                'default_schedule': {'minutes': 5},  # 每5分钟执行一次
                'trading_hours_only': True
            },
            'update_money_flow': {
                'description': '更新资金流向数据',
                'default_schedule': {'minutes': 2},  # 每2分钟执行一次
                'trading_hours_only': True
            },
            'update_dragon_tiger': {
                'description': '更新龙虎榜数据',
                'default_schedule': {'hour': 18, 'minute': 0},  # 每日18:00执行
                'trading_days_only': True
            }
        }
        
        for task_name, config in stock_tasks.items():
            self.task_configs[task_name] = config
            logger.info(f"Stock task '{task_name}' registered")
    
    def setup_default_schedules(self):
        """
        设置默认调度计划
        """
        for task_name, config in self.task_configs.items():
            if 'default_schedule' in config:
                self.create_periodic_task(
                    task_name=task_name,
                    schedule=config['default_schedule'],
                    priority=TaskPriority.NORMAL,
                    enabled=True
                )
                logger.info(f"Default schedule created for task '{task_name}'")
    
    def is_trading_hours(self) -> bool:
        """
        检查是否为交易时间
        
        Returns:
            bool: 是否为交易时间
        """
        now = datetime.now()
        # 简单的交易时间判断：周一到周五，9:30-11:30, 13:00-15:00
        if now.weekday() >= 5:  # 周末
            return False
        
        current_time = now.time()
        morning_start = datetime.strptime('09:30', '%H:%M').time()
        morning_end = datetime.strptime('11:30', '%H:%M').time()
        afternoon_start = datetime.strptime('13:00', '%H:%M').time()
        afternoon_end = datetime.strptime('15:00', '%H:%M').time()
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
    
    def is_trading_day(self) -> bool:
        """
        检查是否为交易日
        
        Returns:
            bool: 是否为交易日
        """
        now = datetime.now()
        # 简单的交易日判断：周一到周五
        return now.weekday() < 5


# 创建全局实例
task_scheduler = TaskScheduler()
stock_task_scheduler = StockDataTaskScheduler()