#!/usr/bin/env python
"""
初始化股票基础数据
"""

import os
import sys
import django
from datetime import date

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockBasicInfo

def init_stock_data():
    """初始化股票基础数据"""
    
    # 测试数据
    test_stocks = [
        {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'market': 'SZ',
            'industry': '银行',
            'concept': '金融科技,数字货币',
            'list_date': date(1991, 4, 3),
            'total_share': 19405918198,
            'float_share': 19405918198,
            'market_cap': 250000000000.00,
            'is_active': True
        },
        {
            'stock_code': '000002',
            'stock_name': '万科A',
            'market': 'SZ',
            'industry': '房地产开发',
            'concept': '深圳本地,房地产',
            'list_date': date(1991, 1, 29),
            'total_share': 11039152001,
            'float_share': 11039152001,
            'market_cap': 180000000000.00,
            'is_active': True
        },
        {
            'stock_code': '600000',
            'stock_name': '浦发银行',
            'market': 'SH',
            'industry': '银行',
            'concept': '上海本地,金融改革',
            'list_date': date(1999, 11, 10),
            'total_share': 29352050819,
            'float_share': 29352050819,
            'market_cap': 220000000000.00,
            'is_active': True
        },
        {
            'stock_code': '600036',
            'stock_name': '招商银行',
            'market': 'SH',
            'industry': '银行',
            'concept': '金融科技,粤港澳大湾区',
            'list_date': date(2002, 4, 9),
            'total_share': 25220645819,
            'float_share': 25220645819,
            'market_cap': 900000000000.00,
            'is_active': True
        },
        {
            'stock_code': '000858',
            'stock_name': '五粮液',
            'market': 'SZ',
            'industry': '白酒',
            'concept': '白酒,消费升级',
            'list_date': date(1998, 4, 27),
            'total_share': 3868050000,
            'float_share': 3868050000,
            'market_cap': 650000000000.00,
            'is_active': True
        },
        {
            'stock_code': '600519',
            'stock_name': '贵州茅台',
            'market': 'SH',
            'industry': '白酒',
            'concept': '白酒,消费升级',
            'list_date': date(2001, 8, 27),
            'total_share': 1256197800,
            'float_share': 1256197800,
            'market_cap': 2200000000000.00,
            'is_active': True
        },
        {
            'stock_code': '000166',
            'stock_name': '申万宏源',
            'market': 'SZ',
            'industry': '证券',
            'concept': '券商,金融改革',
            'list_date': date(1996, 12, 16),
            'total_share': 12345678901,
            'float_share': 12345678901,
            'market_cap': 80000000000.00,
            'is_active': True
        },
        {
            'stock_code': '300059',
            'stock_name': '东方财富',
            'market': 'SZ',
            'industry': '互联网金融',
            'concept': '互联网金融,大数据',
            'list_date': date(2010, 3, 19),
            'total_share': 15678901234,
            'float_share': 15678901234,
            'market_cap': 320000000000.00,
            'is_active': True
        },
        {
            'stock_code': '002415',
            'stock_name': '海康威视',
            'market': 'SZ',
            'industry': '安防设备',
            'concept': '人工智能,物联网,安防',
            'list_date': date(2010, 5, 28),
            'total_share': 9345678901,
            'float_share': 9345678901,
            'market_cap': 380000000000.00,
            'is_active': True
        },
        {
            'stock_code': '600276',
            'stock_name': '恒瑞医药',
            'market': 'SH',
            'industry': '化学制药',
            'concept': '创新药,医药',
            'list_date': date(2000, 10, 18),
            'total_share': 4567890123,
            'float_share': 4567890123,
            'market_cap': 280000000000.00,
            'is_active': True
        }
    ]
    
    print("开始初始化股票基础数据...")
    
    # 清空现有数据
    StockBasicInfo.objects.all().delete()
    print("已清空现有数据")
    
    # 批量创建数据
    created_count = 0
    for stock_data in test_stocks:
        try:
            stock, created = StockBasicInfo.objects.get_or_create(
                stock_code=stock_data['stock_code'],
                defaults=stock_data
            )
            if created:
                created_count += 1
                print(f"创建股票: {stock.stock_code} - {stock.stock_name}")
            else:
                print(f"股票已存在: {stock.stock_code} - {stock.stock_name}")
        except Exception as e:
            print(f"创建股票 {stock_data['stock_code']} 失败: {str(e)}")
    
    print(f"\n数据初始化完成！共创建 {created_count} 条股票记录")
    print(f"当前数据库中共有 {StockBasicInfo.objects.count()} 条股票记录")

if __name__ == '__main__':
    init_stock_data()