#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

def check_empty_tables():
    """检查数据库中哪些表为空"""
    
    with connection.cursor() as cursor:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=== Django Stock 数据库表内容统计 ===")
        print(f"总表数量: {len(tables)}")
        print()
        
        empty_tables = []
        non_empty_tables = []
        table_stats = []
        
        for table in tables:
            table_name = table[0]
            
            # 跳过SQLite系统表
            if table_name == 'sqlite_sequence':
                continue
                
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
                count = cursor.fetchone()[0]
                
                table_stats.append((table_name, count))
                
                if count == 0:
                    empty_tables.append(table_name)
                else:
                    non_empty_tables.append((table_name, count))
                    
            except Exception as e:
                print(f"❌ 查询表 {table_name} 时出错: {e}")
        
        # 显示空表
        if empty_tables:
            print(f"📭 空表 ({len(empty_tables)}张):")
            for table in sorted(empty_tables):
                print(f"  - {table}")
            print()
        else:
            print("✅ 没有发现空表")
            print()
        
        # 显示有数据的表
        if non_empty_tables:
            print(f"📊 有数据的表 ({len(non_empty_tables)}张):")
            # 按记录数量排序
            non_empty_tables.sort(key=lambda x: x[1], reverse=True)
            for table_name, count in non_empty_tables:
                print(f"  - {table_name}: {count:,} 条记录")
            print()
        
        # 按类别统计
        print("=== 按类别统计 ===")
        categories = {
            '股票相关': [],
            '认证相关': [],
            '系统相关': [],
            'Django框架': [],
            '其他': []
        }
        
        for table_name, count in table_stats:
            if 'stock' in table_name.lower():
                categories['股票相关'].append((table_name, count))
            elif table_name.startswith('auth_'):
                categories['认证相关'].append((table_name, count))
            elif table_name.startswith('system_'):
                categories['系统相关'].append((table_name, count))
            elif table_name.startswith('django_'):
                categories['Django框架'].append((table_name, count))
            else:
                categories['其他'].append((table_name, count))
        
        for category, tables in categories.items():
            if tables:
                total_records = sum(count for _, count in tables)
                empty_count = sum(1 for _, count in tables if count == 0)
                print(f"{category}: {len(tables)}张表, {total_records:,}条记录, {empty_count}张空表")
        
        print()
        print(f"总计: {len(table_stats)}张表, {sum(count for _, count in table_stats):,}条记录, {len(empty_tables)}张空表")
        
        return empty_tables, non_empty_tables

if __name__ == "__main__":
    empty_tables, non_empty_tables = check_empty_tables()