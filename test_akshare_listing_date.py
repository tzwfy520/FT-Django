#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

import akshare as ak
import pandas as pd
from utils.akshare_client import AkshareClient

# 测试akshare获取股票基础信息
print("Testing akshare stock basic info...")

# 方法1: 使用ak.stock_info_a_code_name()
try:
    basic_info = ak.stock_info_a_code_name()
    print(f"\nMethod 1 - ak.stock_info_a_code_name():")
    print(f"Columns: {list(basic_info.columns)}")
    print(f"Sample data:")
    print(basic_info.head())
except Exception as e:
    print(f"Error with method 1: {e}")

# 方法2: 使用ak.stock_individual_info_em()获取单只股票详细信息
try:
    # 测试平安银行
    stock_detail = ak.stock_individual_info_em(symbol="000001")
    print(f"\nMethod 2 - ak.stock_individual_info_em('000001'):")
    print(f"Columns: {list(stock_detail.columns)}")
    print(f"Sample data:")
    print(stock_detail.head(10))
except Exception as e:
    print(f"Error with method 2: {e}")

# 方法3: 使用ak.stock_zh_a_spot_em()获取实时行情（可能包含基础信息）
try:
    spot_data = ak.stock_zh_a_spot_em()
    print(f"\nMethod 3 - ak.stock_zh_a_spot_em():")
    print(f"Columns: {list(spot_data.columns)}")
    print(f"Sample data (first 3 rows):")
    print(spot_data.head(3))
except Exception as e:
    print(f"Error with method 3: {e}")

# 方法4: 查找专门的上市日期接口
try:
    # 尝试获取股票基本信息，可能包含上市日期
    print(f"\nSearching for listing date specific functions...")
    # 检查是否有专门的上市日期接口
    print("Available akshare functions containing 'list' or 'date':")
    import inspect
    ak_functions = [name for name, obj in inspect.getmembers(ak) if inspect.isfunction(obj)]
    relevant_functions = [f for f in ak_functions if 'list' in f.lower() or 'date' in f.lower() or 'basic' in f.lower()]
    for func in relevant_functions[:10]:  # 显示前10个相关函数
        print(f"  - {func}")
except Exception as e:
    print(f"Error searching functions: {e}")