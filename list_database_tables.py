#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

def list_all_tables():
    """列出数据库中的所有表"""
    
    with connection.cursor() as cursor:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=== Django Stock 数据库中的所有表 ===")
        print(f"总表数量: {len(tables)}")
        print()
        
        # 按类别分组显示表
        django_tables = []
        stock_tables = []
        system_tables = []
        auth_tables = []
        other_tables = []
        
        for table in tables:
            table_name = table[0]
            if table_name.startswith('django_'):
                django_tables.append(table_name)
            elif 'stock' in table_name.lower():
                stock_tables.append(table_name)
            elif table_name.startswith('auth_'):
                auth_tables.append(table_name)
            elif table_name.startswith('system_'):
                system_tables.append(table_name)
            else:
                other_tables.append(table_name)
        
        # 显示分类结果
        if stock_tables:
            print(f"📈 股票相关表 ({len(stock_tables)}张):")
            for table in sorted(stock_tables):
                print(f"  - {table}")
            print()
        
        if auth_tables:
            print(f"🔐 认证相关表 ({len(auth_tables)}张):")
            for table in sorted(auth_tables):
                print(f"  - {table}")
            print()
        
        if system_tables:
            print(f"⚙️ 系统相关表 ({len(system_tables)}张):")
            for table in sorted(system_tables):
                print(f"  - {table}")
            print()
        
        if django_tables:
            print(f"🔧 Django框架表 ({len(django_tables)}张):")
            for table in sorted(django_tables):
                print(f"  - {table}")
            print()
        
        if other_tables:
            print(f"📋 其他表 ({len(other_tables)}张):")
            for table in sorted(other_tables):
                print(f"  - {table}")
            print()
        
        # 显示所有表的完整列表
        print("=== 完整表列表 ===")
        all_tables = sorted([table[0] for table in tables])
        for i, table in enumerate(all_tables, 1):
            print(f"{i:2d}. {table}")
        
        return len(tables)

if __name__ == "__main__":
    total_tables = list_all_tables()
    print(f"\n总计: {total_tables} 张表")