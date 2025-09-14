#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
from collections import Counter

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockBasicInfo

def verify_listing_dates():
    """验证股票上市时间数据的完整性和合理性"""
    
    print("=== 股票上市时间数据验证报告 ===")
    print()
    
    # 基本统计
    all_stocks = StockBasicInfo.objects.all()
    stocks_with_date = StockBasicInfo.objects.filter(list_date__isnull=False)
    stocks_without_date = StockBasicInfo.objects.filter(list_date__isnull=True)
    
    print(f"总股票数量: {all_stocks.count()}")
    print(f"有上市时间的股票: {stocks_with_date.count()}")
    print(f"无上市时间的股票: {stocks_without_date.count()}")
    print(f"数据完整率: {stocks_with_date.count() / all_stocks.count() * 100:.1f}%")
    print()
    
    # 按年份统计上市数量
    print("=== 按年份统计上市数量 ===")
    years = []
    for stock in stocks_with_date:
        if stock.list_date:
            years.append(stock.list_date.year)
    
    year_counts = Counter(years)
    for year in sorted(year_counts.keys()):
        print(f"{year}年: {year_counts[year]}只股票")
    print()
    
    # 按交易所统计
    print("=== 按交易所统计 ===")
    markets = ['SH', 'SZ', 'BJ']
    for market in markets:
        market_stocks = StockBasicInfo.objects.filter(market=market)
        market_with_date = market_stocks.filter(list_date__isnull=False)
        market_name = {'SH': '上海证券交易所', 'SZ': '深圳证券交易所', 'BJ': '北京证券交易所'}[market]
        print(f"{market_name}: {market_with_date.count()}/{market_stocks.count()}只股票有上市时间")
    print()
    
    # 最早和最晚上市的股票
    print("=== 上市时间范围 ===")
    earliest_stock = stocks_with_date.order_by('list_date').first()
    latest_stock = stocks_with_date.order_by('-list_date').first()
    
    if earliest_stock:
        print(f"最早上市: {earliest_stock.stock_code} - {earliest_stock.stock_name} ({earliest_stock.list_date})")
    if latest_stock:
        print(f"最晚上市: {latest_stock.stock_code} - {latest_stock.stock_name} ({latest_stock.list_date})")
    print()
    
    # 数据合理性检查
    print("=== 数据合理性检查 ===")
    current_year = datetime.now().year
    future_stocks = stocks_with_date.filter(list_date__year__gt=current_year)
    very_old_stocks = stocks_with_date.filter(list_date__year__lt=1990)
    
    print(f"未来上市的股票（可能有误）: {future_stocks.count()}只")
    if future_stocks.exists():
        for stock in future_stocks:
            print(f"  - {stock.stock_code} - {stock.stock_name} ({stock.list_date})")
    
    print(f"1990年前上市的股票: {very_old_stocks.count()}只")
    if very_old_stocks.exists():
        for stock in very_old_stocks[:5]:  # 显示前5只
            print(f"  - {stock.stock_code} - {stock.stock_name} ({stock.list_date})")
    print()
    
    # 随机抽样验证
    print("=== 随机抽样验证 ===")
    import random
    sample_stocks = random.sample(list(stocks_with_date), min(10, stocks_with_date.count()))
    for stock in sample_stocks:
        print(f"{stock.stock_code} - {stock.stock_name} - {stock.list_date} ({stock.get_market_display()})")
    
    print()
    print("=== 验证完成 ===")

if __name__ == "__main__":
    verify_listing_dates()