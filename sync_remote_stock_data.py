#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从远程MySQL服务器同步股票基础信息到本地数据库
"""

import os
import sys
import django
import pymysql
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockBasicInfo

def connect_remote_mysql():
    """连接远程MySQL数据库"""
    try:
        connection = pymysql.connect(
            host='115.190.90.219',
            user='root',  # 请根据实际情况修改用户名
            password='',  # 请根据实际情况修改密码
            database='flask_stock',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("成功连接到远程MySQL数据库")
        return connection
    except Exception as e:
        print(f"连接远程MySQL数据库失败: {e}")
        return None

def fetch_remote_stock_data(connection):
    """从远程数据库获取股票基础信息"""
    try:
        with connection.cursor() as cursor:
            # 查询远程数据库的stock_basic_info表结构
            cursor.execute("DESCRIBE stock_basic_info")
            columns = cursor.fetchall()
            print("远程数据库表结构:")
            for col in columns:
                print(f"  {col['Field']}: {col['Type']}")
            
            # 获取所有股票基础信息
            cursor.execute("SELECT * FROM stock_basic_info")
            stock_data = cursor.fetchall()
            print(f"从远程数据库获取到 {len(stock_data)} 条股票数据")
            return stock_data
    except Exception as e:
        print(f"获取远程股票数据失败: {e}")
        return []

def sync_to_local_database(stock_data):
    """将数据同步到本地数据库"""
    success_count = 0
    error_count = 0
    
    for stock in stock_data:
        try:
            # 根据远程数据库字段映射到本地模型
            # 需要根据实际的远程数据库字段进行调整
            stock_obj = StockBasicInfo(
                stock_code=stock.get('stock_code', ''),
                stock_name=stock.get('stock_name', ''),
                market=stock.get('market', 'SH'),  # 默认上海
                industry=stock.get('industry', ''),
                concept=stock.get('concept', ''),
                list_date=stock.get('list_date'),
                total_share=stock.get('total_share'),
                float_share=stock.get('float_share'),
                market_cap=stock.get('market_cap'),
                is_active=True
            )
            stock_obj.save()
            success_count += 1
            
            if success_count % 100 == 0:
                print(f"已同步 {success_count} 条数据...")
                
        except Exception as e:
            error_count += 1
            print(f"同步股票 {stock.get('stock_code', 'Unknown')} 失败: {e}")
    
    print(f"数据同步完成: 成功 {success_count} 条, 失败 {error_count} 条")
    return success_count, error_count

def main():
    """主函数"""
    print("开始同步远程股票数据...")
    
    # 连接远程数据库
    connection = connect_remote_mysql()
    if not connection:
        return
    
    try:
        # 获取远程数据
        stock_data = fetch_remote_stock_data(connection)
        if not stock_data:
            print("未获取到任何数据")
            return
        
        # 同步到本地数据库
        success_count, error_count = sync_to_local_database(stock_data)
        
        print(f"\n同步结果统计:")
        print(f"  成功同步: {success_count} 条")
        print(f"  同步失败: {error_count} 条")
        print(f"  本地数据库总数: {StockBasicInfo.objects.count()} 条")
        
    finally:
        connection.close()
        print("已关闭数据库连接")

if __name__ == '__main__':
    main()