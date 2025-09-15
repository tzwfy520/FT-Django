#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.tasks.models import TaskExecution
from apps.stocks.models import StockHistoryData, StockDailyHistoryData, StockWeeklyHistoryData, StockMonthlyHistoryData

print("=== Task Execution Records ===")
for record in TaskExecution.objects.order_by('-id')[:3]:
    print(f"ID: {record.id}, Status: {record.status}, Task: {record.task.name}, Created: {record.created_at}")

# 查询股票历史数据记录数
stock_count = StockHistoryData.objects.count()
daily_count = StockDailyHistoryData.objects.count()
weekly_count = StockWeeklyHistoryData.objects.count()
monthly_count = StockMonthlyHistoryData.objects.count()

print(f"StockHistoryData records: {stock_count}")
print(f"StockDailyHistoryData records: {daily_count}")
print(f"StockWeeklyHistoryData records: {weekly_count}")
print(f"StockMonthlyHistoryData records: {monthly_count}")
print(f"Total history records: {daily_count + weekly_count + monthly_count}")

# 显示最近的每日数据
if daily_count > 0:
    recent_daily = StockDailyHistoryData.objects.order_by('-trade_date')[:5]
    print("\n=== Recent Daily Data ===")
    for record in recent_daily:
        print(f"Code: {record.stock_code}, Date: {record.trade_date}, Close: {record.close_price}")