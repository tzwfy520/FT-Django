#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查股票实时交易数据表的详细信息
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append('/Users/wangfuyu/PythonCode/FT-Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockRealtimeData, StockBasicInfo
from django.db import connection

def check_realtime_data_table():
    """
    检查股票实时交易数据表的详细信息
    """
    print("=== 股票实时交易数据表分析 ===")
    print()
    
    # 1. 表基本信息
    print("📊 表基本信息:")
    print(f"  模型名称: StockRealtimeData")
    print(f"  数据库表名: stock_realtime_data")
    print(f"  表描述: 股票实时数据表")
    print()
    
    # 2. 表结构信息
    print("🏗️ 表结构信息:")
    print("  主要字段:")
    print("    - stock: 股票外键 (关联StockBasicInfo)")
    print("    - current_price: 当前价格")
    print("    - open_price: 开盘价")
    print("    - high_price: 最高价")
    print("    - low_price: 最低价")
    print("    - pre_close: 昨收价")
    print("    - change: 涨跌额")
    print("    - change_pct: 涨跌幅(%)")
    print("    - volume: 成交量(手)")
    print("    - amount: 成交额(元)")
    print("    - turnover_rate: 换手率(%)")
    print("    - pe_ratio: 市盈率")
    print("    - pb_ratio: 市净率")
    print("    - timestamp: 数据时间")
    print("    - created_at: 创建时间")
    print()
    
    # 3. 数据统计
    print("📈 数据统计:")
    total_count = StockRealtimeData.objects.count()
    print(f"  总记录数: {total_count:,} 条")
    
    if total_count > 0:
        # 最新数据时间
        latest_data = StockRealtimeData.objects.order_by('-timestamp').first()
        print(f"  最新数据时间: {latest_data.timestamp}")
        
        # 最早数据时间
        earliest_data = StockRealtimeData.objects.order_by('timestamp').first()
        print(f"  最早数据时间: {earliest_data.timestamp}")
        
        # 涉及股票数量
        stock_count = StockRealtimeData.objects.values('stock').distinct().count()
        print(f"  涉及股票数量: {stock_count:,} 只")
        
        # 按日期统计
        print("\n  📅 按日期统计 (最近10天):")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM stock_realtime_data 
                GROUP BY DATE(timestamp) 
                ORDER BY date DESC 
                LIMIT 10
            """)
            for row in cursor.fetchall():
                print(f"    {row[0]}: {row[1]:,} 条记录")
        
        # 价格范围统计
        print("\n  💰 价格统计:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    MIN(current_price) as min_price,
                    MAX(current_price) as max_price,
                    AVG(current_price) as avg_price,
                    MIN(change_pct) as min_change,
                    MAX(change_pct) as max_change
                FROM stock_realtime_data
            """)
            row = cursor.fetchone()
            if row:
                print(f"    价格范围: {row[0]:.3f} - {row[1]:.3f} 元")
                print(f"    平均价格: {row[2]:.3f} 元")
                print(f"    涨跌幅范围: {row[3]:.2f}% - {row[4]:.2f}%")
        
        # 成交量统计
        print("\n  📊 成交量统计:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    MIN(volume) as min_volume,
                    MAX(volume) as max_volume,
                    AVG(volume) as avg_volume,
                    SUM(volume) as total_volume
                FROM stock_realtime_data
            """)
            row = cursor.fetchone()
            if row:
                print(f"    成交量范围: {row[0]:,} - {row[1]:,} 手")
                print(f"    平均成交量: {row[2]:,.0f} 手")
                print(f"    总成交量: {row[3]:,} 手")
        
        # 示例数据
        print("\n  📋 示例数据 (最新5条):")
        sample_data = StockRealtimeData.objects.select_related('stock').order_by('-timestamp')[:5]
        for data in sample_data:
            print(f"    {data.stock.stock_code} {data.stock.stock_name}: ")
            print(f"      价格: {data.current_price} 元, 涨跌幅: {data.change_pct}%, ")
            print(f"      成交量: {data.volume:,} 手, 时间: {data.timestamp}")
    else:
        print("  ❌ 表中暂无数据")
    
    print()
    print("=== 相关表信息 ===")
    
    # 4. 相关表统计
    basic_info_count = StockBasicInfo.objects.count()
    print(f"📋 股票基础信息表 (stock_basic_info): {basic_info_count:,} 条记录")
    
    # 5. 表关系说明
    print("\n🔗 表关系说明:")
    print("  - stock_realtime_data.stock_id → stock_basic_info.id")
    print("  - 每只股票可以有多条实时数据记录")
    print("  - 通过timestamp字段区分不同时间点的数据")
    print("  - unique_together约束: ['stock', 'timestamp']")
    
    print("\n✅ 分析完成")

if __name__ == '__main__':
    check_realtime_data_table()