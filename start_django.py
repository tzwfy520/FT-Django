#!/usr/bin/env python
"""
快速启动Django开发服务器
"""

import os
import sys
import subprocess
from pathlib import Path

# 设置项目路径
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

def check_redis():
    """检查Redis连接"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis连接正常")
        return True
    except Exception as e:
        print(f"⚠️  Redis连接失败: {e}")
        print("提示: 请启动Redis服务 (brew services start redis)")
        return False

def run_migrations():
    """执行数据库迁移"""
    print("📊 执行数据库迁移...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ 数据库迁移完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def create_superuser():
    """创建超级用户"""
    print("👤 检查超级用户...")
    try:
        # 检查是否已有超级用户
        result = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())"
        ], capture_output=True, text=True)
        
        if 'True' in result.stdout:
            print("✅ 超级用户已存在")
            return True
        
        # 创建默认超级用户
        subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"
        ], check=True)
        
        print("✅ 创建默认超级用户: admin/admin123")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建超级用户失败: {e}")
        return False

def start_django_server(port=8000):
    """启动Django开发服务器"""
    print(f"🚀 启动Django开发服务器 (端口: {port})...")
    print("=" * 50)
    print(f"🌐 管理后台: http://localhost:{port}/admin/")
    print(f"📱 API接口: http://localhost:{port}/api/")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Django服务器已停止")

def main():
    print("🎯 股票分析系统 - Django服务器启动器")
    print("=" * 50)
    
    # 检查Redis (可选)
    check_redis()
    
    # 执行数据库迁移
    if not run_migrations():
        return
    
    # 创建超级用户
    create_superuser()
    
    # 启动Django服务器
    start_django_server()

if __name__ == '__main__':
    main()