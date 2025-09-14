#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime
import time
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

import akshare as ak
from apps.stocks.models import StockBasicInfo

def parse_listing_date(date_str):
    """解析上市时间字符串，转换为日期对象"""
    if not date_str or date_str == '-' or str(date_str).strip() == '':
        return None
    
    try:
        # akshare返回的日期格式通常是YYYYMMDD
        date_str = str(date_str).strip()
        if len(date_str) == 8 and date_str.isdigit():
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return datetime(year, month, day).date()
        else:
            print(f"Unexpected date format: {date_str}")
            return None
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return None

def get_stock_listing_date(stock_code):
    """获取单只股票的上市时间"""
    try:
        # 添加随机延迟避免请求过于频繁
        time.sleep(random.uniform(0.5, 1.0))
        
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if stock_info is not None and not stock_info.empty:
            # 查找上市时间行
            listing_date_row = stock_info[stock_info['item'] == '上市时间']
            if not listing_date_row.empty:
                listing_date_str = listing_date_row.iloc[0]['value']
                return parse_listing_date(listing_date_str)
        return None
    except Exception as e:
        print(f"Error getting listing date for {stock_code}: {e}")
        return None

def update_missing_listing_dates():
    """批量更新缺失的股票上市时间"""
    # 获取所有上市时间为空的股票
    stocks_without_listing_date = StockBasicInfo.objects.filter(list_date__isnull=True)
    total_stocks = stocks_without_listing_date.count()
    
    print(f"Found {total_stocks} stocks without listing date")
    print("Starting to update listing dates...\n")
    
    updated_count = 0
    failed_count = 0
    
    for i, stock in enumerate(stocks_without_listing_date, 1):
        print(f"Processing {i}/{total_stocks}: {stock.stock_code} - {stock.stock_name}")
        
        listing_date = get_stock_listing_date(stock.stock_code)
        
        if listing_date:
            stock.list_date = listing_date
            stock.save()
            updated_count += 1
            print(f"  ✓ Updated: {listing_date}")
        else:
            failed_count += 1
            print(f"  ✗ Failed to get listing date")
        
        # 每处理10只股票显示一次进度
        if i % 10 == 0:
            print(f"\nProgress: {i}/{total_stocks} processed, {updated_count} updated, {failed_count} failed\n")
    
    print(f"\n=== Update Summary ===")
    print(f"Total processed: {total_stocks}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed: {failed_count}")
    
    # 验证更新结果
    remaining_without_date = StockBasicInfo.objects.filter(list_date__isnull=True).count()
    print(f"Remaining stocks without listing date: {remaining_without_date}")

if __name__ == "__main__":
    print("Starting batch update of stock listing dates...")
    print("This may take a while due to API rate limiting.\n")
    
    # 询问用户确认
    response = input("Do you want to proceed? (y/N): ")
    if response.lower() in ['y', 'yes']:
        update_missing_listing_dates()
    else:
        print("Update cancelled.")