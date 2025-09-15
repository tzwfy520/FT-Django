from django.core.management.base import BaseCommand
import subprocess
import sys
import os
import signal
import time
from threading import Thread

class Command(BaseCommand):
    help = 'Start Celery worker and beat services'
    
    def __init__(self):
        super().__init__()
        self.worker_process = None
        self.beat_process = None
        self.running = True
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--worker-only',
            action='store_true',
            help='Start only the worker process'
        )
        parser.add_argument(
            '--beat-only',
            action='store_true',
            help='Start only the beat process'
        )
        parser.add_argument(
            '--concurrency',
            type=int,
            default=4,
            help='Number of worker processes (default: 4)'
        )
        parser.add_argument(
            '--loglevel',
            default='info',
            help='Logging level (default: info)'
        )
    
    def signal_handler(self, signum, frame):
        """处理终止信号"""
        self.stdout.write(self.style.WARNING('\n正在停止Celery服务...'))
        self.running = False
        
        if self.worker_process:
            self.worker_process.terminate()
            self.worker_process.wait()
            self.stdout.write(self.style.SUCCESS('Worker进程已停止'))
        
        if self.beat_process:
            self.beat_process.terminate()
            self.beat_process.wait()
            self.stdout.write(self.style.SUCCESS('Beat进程已停止'))
        
        sys.exit(0)
    
    def start_worker(self, concurrency, loglevel):
        """启动Celery worker"""
        cmd = [
            'celery', '-A', 'stock_analysis', 'worker',
            '--loglevel', loglevel,
            '--concurrency', str(concurrency)
        ]
        
        self.stdout.write(f'启动Celery Worker: {" ".join(cmd)}')
        self.worker_process = subprocess.Popen(cmd)
        return self.worker_process
    
    def start_beat(self, loglevel):
        """启动Celery beat"""
        cmd = [
            'celery', '-A', 'stock_analysis', 'beat',
            '--loglevel', loglevel,
            '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'
        ]
        
        self.stdout.write(f'启动Celery Beat: {" ".join(cmd)}')
        self.beat_process = subprocess.Popen(cmd)
        return self.beat_process
    
    def monitor_processes(self):
        """监控进程状态"""
        while self.running:
            time.sleep(5)
            
            # 检查worker进程
            if self.worker_process and self.worker_process.poll() is not None:
                self.stdout.write(self.style.ERROR('Worker进程意外退出'))
                if self.running:
                    self.stdout.write('重启Worker进程...')
                    self.worker_process = self.start_worker(
                        self.concurrency, self.loglevel
                    )
            
            # 检查beat进程
            if self.beat_process and self.beat_process.poll() is not None:
                self.stdout.write(self.style.ERROR('Beat进程意外退出'))
                if self.running:
                    self.stdout.write('重启Beat进程...')
                    self.beat_process = self.start_beat(self.loglevel)
    
    def handle(self, *args, **options):
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        worker_only = options['worker_only']
        beat_only = options['beat_only']
        self.concurrency = options['concurrency']
        self.loglevel = options['loglevel']
        
        self.stdout.write(self.style.SUCCESS('启动Celery服务...'))
        
        try:
            # 启动服务
            if not beat_only:
                self.start_worker(self.concurrency, self.loglevel)
                self.stdout.write(self.style.SUCCESS('Celery Worker已启动'))
            
            if not worker_only:
                self.start_beat(self.loglevel)
                self.stdout.write(self.style.SUCCESS('Celery Beat已启动'))
            
            self.stdout.write(self.style.SUCCESS('所有服务已启动，按Ctrl+C停止'))
            
            # 启动监控线程
            monitor_thread = Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 主线程等待
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'启动失败: {e}'))
            self.signal_handler(signal.SIGTERM, None)