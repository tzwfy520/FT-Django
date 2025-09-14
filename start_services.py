#!/usr/bin/env python
"""
股票分析系统服务启动脚本
用于启动Django开发服务器和Celery工作进程
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = BASE_DIR
        
    def start_django(self, port=8000):
        """启动Django开发服务器"""
        print(f"🚀 启动Django开发服务器 (端口: {port})...")
        
        cmd = [
            sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(('Django Server', process))
        return process
    
    def start_celery_worker(self, concurrency=4):
        """启动Celery工作进程"""
        print(f"🔄 启动Celery工作进程 (并发数: {concurrency})...")
        
        cmd = [
            'celery', '-A', 'stock_analysis', 'worker',
            '--loglevel=info',
            f'--concurrency={concurrency}',
            '--pool=prefork'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(('Celery Worker', process))
        return process
    
    def start_celery_beat(self):
        """启动Celery定时任务调度器"""
        print("⏰ 启动Celery定时任务调度器...")
        
        cmd = [
            'celery', '-A', 'stock_analysis', 'beat',
            '--loglevel=info',
            '--scheduler=django_celery_beat.schedulers:DatabaseScheduler'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(('Celery Beat', process))
        return process
    
    def start_celery_flower(self, port=5555):
        """启动Celery监控面板"""
        print(f"🌸 启动Celery监控面板 (端口: {port})...")
        
        cmd = [
            'celery', '-A', 'stock_analysis', 'flower',
            f'--port={port}',
            '--basic_auth=admin:admin123'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        self.processes.append(('Celery Flower', process))
        return process
    
    def check_dependencies(self):
        """检查依赖服务"""
        print("🔍 检查依赖服务...")
        
        # 检查Redis连接
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            print("✅ Redis连接正常")
        except Exception as e:
            print(f"❌ Redis连接失败: {e}")
            print("请确保Redis服务已启动")
            return False
        
        # 检查数据库连接
        try:
            import django
            django.setup()
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            print("请检查数据库配置和连接")
            return False
        
        return True
    
    def init_database(self):
        """初始化数据库"""
        print("📊 初始化数据库...")
        
        try:
            # 执行数据库迁移
            subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], cwd=self.base_dir, check=True)
            
            # 初始化数据库
            subprocess.run([
                sys.executable, 'manage.py', 'init_database', '--sample-data'
            ], cwd=self.base_dir, check=True)
            
            print("✅ 数据库初始化完成")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False
    
    def start_all_services(self, django_port=8000, flower_port=5555, worker_concurrency=4):
        """启动所有服务"""
        print("🎯 启动股票分析系统服务...")
        print("=" * 50)
        
        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败，请解决依赖问题后重试")
            return False
        
        # 初始化数据库
        if not self.init_database():
            print("❌ 数据库初始化失败")
            return False
        
        print("=" * 50)
        
        try:
            # 启动各个服务
            self.start_django(django_port)
            time.sleep(2)  # 等待Django启动
            
            self.start_celery_worker(worker_concurrency)
            time.sleep(1)
            
            self.start_celery_beat()
            time.sleep(1)
            
            self.start_celery_flower(flower_port)
            
            print("\n" + "=" * 50)
            print("🎉 所有服务启动成功！")
            print(f"📱 Django管理后台: http://localhost:{django_port}/admin/")
            print(f"🌐 API接口文档: http://localhost:{django_port}/swagger/")
            print(f"🌸 Celery监控面板: http://localhost:{flower_port}/")
            print("=" * 50)
            print("按 Ctrl+C 停止所有服务")
            
            # 等待用户中断
            self.wait_for_interrupt()
            
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，正在关闭服务...")
        except Exception as e:
            print(f"❌ 启动服务时出错: {e}")
        finally:
            self.stop_all_services()
    
    def wait_for_interrupt(self):
        """等待用户中断信号"""
        try:
            while True:
                # 检查进程状态
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} 进程意外退出")
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🔄 正在停止所有服务...")
        
        for name, process in self.processes:
            try:
                print(f"停止 {name}...")
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"强制终止 {name}...")
                    process.kill()
                    process.wait()
                
                print(f"✅ {name} 已停止")
                
            except Exception as e:
                print(f"❌ 停止 {name} 时出错: {e}")
        
        print("🎯 所有服务已停止")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='股票分析系统服务管理器')
    parser.add_argument('--django-port', type=int, default=8000, help='Django服务端口')
    parser.add_argument('--flower-port', type=int, default=5555, help='Flower监控端口')
    parser.add_argument('--worker-concurrency', type=int, default=4, help='Celery工作进程并发数')
    parser.add_argument('--init-only', action='store_true', help='仅初始化数据库')
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.init_only:
        manager.check_dependencies()
        manager.init_database()
    else:
        manager.start_all_services(
            django_port=args.django_port,
            flower_port=args.flower_port,
            worker_concurrency=args.worker_concurrency
        )

if __name__ == '__main__':
    main()