from django.core.management.base import BaseCommand
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django_celery_results.models import TaskResult
from celery import current_app
import json
from datetime import timedelta

class Command(BaseCommand):
    help = 'Show Celery tasks status and statistics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--active',
            action='store_true',
            help='Show only active tasks'
        )
        parser.add_argument(
            '--recent',
            type=int,
            default=24,
            help='Show tasks from last N hours (default: 24)'
        )
        parser.add_argument(
            '--task-name',
            help='Filter by task name'
        )
        parser.add_argument(
            '--status',
            choices=['SUCCESS', 'FAILURE', 'PENDING', 'RETRY', 'REVOKED'],
            help='Filter by task status'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Celery任务状态报告 ===\n'))
        
        # 显示活跃的worker
        self.show_active_workers()
        
        # 显示定时任务
        self.show_periodic_tasks(options['active'])
        
        # 显示最近的任务执行结果
        self.show_recent_tasks(options)
        
        # 显示任务统计
        self.show_task_statistics(options['recent'])
    
    def show_active_workers(self):
        """显示活跃的worker"""
        self.stdout.write(self.style.HTTP_INFO('活跃的Worker:'))
        
        try:
            # 获取活跃的worker
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                for worker, tasks in active_workers.items():
                    self.stdout.write(f'  • {worker}: {len(tasks)} 个活跃任务')
                    for task in tasks[:3]:  # 只显示前3个任务
                        self.stdout.write(f'    - {task["name"]} (ID: {task["id"][:8]}...)')
                    if len(tasks) > 3:
                        self.stdout.write(f'    ... 还有 {len(tasks) - 3} 个任务')
            else:
                self.stdout.write(self.style.WARNING('  没有活跃的worker'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  无法获取worker信息: {e}'))
        
        self.stdout.write('')
    
    def show_periodic_tasks(self, active_only=False):
        """显示定时任务"""
        self.stdout.write(self.style.HTTP_INFO('定时任务:'))
        
        tasks = PeriodicTask.objects.all()
        if active_only:
            tasks = tasks.filter(enabled=True)
        
        if tasks.exists():
            for task in tasks:
                status = '✓' if task.enabled else '✗'
                schedule_info = self.get_schedule_info(task)
                self.stdout.write(f'  {status} {task.name}')
                self.stdout.write(f'    任务: {task.task}')
                self.stdout.write(f'    调度: {schedule_info}')
                if task.last_run_at:
                    self.stdout.write(f'    上次运行: {task.last_run_at.strftime("%Y-%m-%d %H:%M:%S")}')
                self.stdout.write('')
        else:
            self.stdout.write(self.style.WARNING('  没有定时任务'))
        
        self.stdout.write('')
    
    def get_schedule_info(self, task):
        """获取调度信息"""
        if task.crontab:
            cron = task.crontab
            return f'Cron: {cron.minute} {cron.hour} {cron.day_of_month} {cron.month_of_year} {cron.day_of_week}'
        elif task.interval:
            interval = task.interval
            return f'间隔: 每 {interval.every} {interval.period}'
        else:
            return '一次性任务'
    
    def show_recent_tasks(self, options):
        """显示最近的任务执行结果"""
        hours = options['recent']
        task_name = options.get('task_name')
        status = options.get('status')
        
        self.stdout.write(self.style.HTTP_INFO(f'最近{hours}小时的任务执行结果:'))
        
        # 构建查询
        since = timezone.now() - timedelta(hours=hours)
        tasks = TaskResult.objects.filter(date_created__gte=since)
        
        if task_name:
            tasks = tasks.filter(task_name__icontains=task_name)
        
        if status:
            tasks = tasks.filter(status=status)
        
        tasks = tasks.order_by('-date_created')[:20]  # 最多显示20个
        
        if tasks.exists():
            for task in tasks:
                status_color = self.get_status_color(task.status)
                self.stdout.write(
                    f'  {status_color(task.status.ljust(8))} '
                    f'{task.task_name} '
                    f'({task.date_created.strftime("%m-%d %H:%M:%S")})')
                
                if task.status == 'FAILURE' and task.traceback:
                    # 显示错误信息的前两行
                    error_lines = task.traceback.split('\n')[:2]
                    for line in error_lines:
                        if line.strip():
                            self.stdout.write(f'    错误: {line.strip()}')
                            break
        else:
            self.stdout.write(self.style.WARNING('  没有找到匹配的任务'))
        
        self.stdout.write('')
    
    def get_status_color(self, status):
        """根据状态返回颜色函数"""
        colors = {
            'SUCCESS': self.style.SUCCESS,
            'FAILURE': self.style.ERROR,
            'PENDING': self.style.WARNING,
            'RETRY': self.style.HTTP_INFO,
            'REVOKED': self.style.HTTP_NOT_MODIFIED,
        }
        return colors.get(status, self.style.NOTICE)
    
    def show_task_statistics(self, hours):
        """显示任务统计信息"""
        self.stdout.write(self.style.HTTP_INFO(f'最近{hours}小时任务统计:'))
        
        since = timezone.now() - timedelta(hours=hours)
        tasks = TaskResult.objects.filter(date_created__gte=since)
        
        # 按状态统计
        status_stats = {}
        for status in ['SUCCESS', 'FAILURE', 'PENDING', 'RETRY', 'REVOKED']:
            count = tasks.filter(status=status).count()
            if count > 0:
                status_stats[status] = count
        
        if status_stats:
            self.stdout.write('  按状态统计:')
            for status, count in status_stats.items():
                color_func = self.get_status_color(status)
                self.stdout.write(f'    {color_func(status)}: {count}')
        
        # 按任务名统计
        task_stats = {}
        for task in tasks:
            task_name = task.task_name.split('.')[-1]  # 只取最后一部分
            task_stats[task_name] = task_stats.get(task_name, 0) + 1
        
        if task_stats:
            self.stdout.write('\n  按任务类型统计:')
            sorted_tasks = sorted(task_stats.items(), key=lambda x: x[1], reverse=True)
            for task_name, count in sorted_tasks[:10]:  # 只显示前10个
                self.stdout.write(f'    {task_name}: {count}')
        
        # 总计
        total = tasks.count()
        if total > 0:
            success_rate = (status_stats.get('SUCCESS', 0) / total) * 100
            self.stdout.write(f'\n  总计: {total} 个任务，成功率: {success_rate:.1f}%')
        else:
            self.stdout.write('\n  没有任务执行记录')