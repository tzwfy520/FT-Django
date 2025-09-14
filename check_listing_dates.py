#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockBasicInfo

# 查询未知上市时间的股票
stocks_with_unknown_listing = StockBasicInfo.objects.filter(list_date__isnull=True)
print(f'Stocks with unknown listing date: {stocks_with_unknown_listing.count()}')
print('\nList of stocks with unknown listing date:')
for stock in stocks_with_unknown_listing[:20]:
    print(f'{stock.stock_code} - {stock.stock_name}')

# 查询所有股票的上市时间情况
all_stocks = StockBasicInfo.objects.all()
stocks_with_listing = StockBasicInfo.objects.filter(list_date__isnull=False)
print(f'\nTotal stocks: {all_stocks.count()}')
print(f'Stocks with known listing date: {stocks_with_listing.count()}')
print(f'Stocks with unknown listing date: {stocks_with_unknown_listing.count()}')

# 显示一些有上市时间的股票作为对比
print('\nSample stocks with known listing date:')
for stock in stocks_with_listing[:10]:
    print(f'{stock.stock_code} - {stock.stock_name} - {stock.list_date}')