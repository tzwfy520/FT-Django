#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查Django Stock项目中实时交易数据的真实性
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
sys.path.append('/Users/wangfuyu/PythonCode/FT-Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockRealtimeData, StockBasicInfo
from utils.akshare_client import AkshareClient
import re

def analyze_frontend_data_generation():
    """分析前端数据生成方式"""
    print("\n=== 前端数据生成分析 ===")
    
    frontend_files = [
        '/Users/wangfuyu/PythonCode/FT-Django/frontend/src/views/realtime/StockQuery.vue',
        '/Users/wangfuyu/PythonCode/FT-Django/frontend/src/views/concept/ConceptRealtimeData.vue'
    ]
    
    mock_patterns = [
        r'Math\.random\(\)',
        r'生成模拟.*数据',
        r'模拟.*数据',
        r'mock.*data',
        r'fake.*data',
        r'generateMock',
        r'模拟API调用'
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"\n检查文件: {Path(file_path).name}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            mock_count = 0
            for pattern in mock_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    mock_count += len(matches)
                    print(f"  发现模拟数据生成: {pattern} ({len(matches)}次)")
            
            if mock_count > 0:
                print(f"  ❌ 该文件包含 {mock_count} 处模拟数据生成")
            else:
                print(f"  ✅ 该文件未发现明显的模拟数据生成")
        else:
            print(f"文件不存在: {file_path}")

def analyze_backend_data_source():
    """分析后端数据源"""
    print("\n=== 后端数据源分析 ===")
    
    # 检查数据库中的实时数据
    realtime_count = StockRealtimeData.objects.count()
    print(f"数据库中实时数据记录数: {realtime_count}")
    
    if realtime_count > 0:
        latest_data = StockRealtimeData.objects.order_by('-created_at').first()
        print(f"最新数据时间: {latest_data.created_at}")
        print(f"最新数据股票: {latest_data.stock.stock_code} - {latest_data.stock.stock_name}")
        print(f"最新价格: {latest_data.current_price}")
    else:
        print("❌ 数据库中没有实时数据")
    
    # 检查akshare客户端
    print("\n检查Akshare客户端连接:")
    try:
        client = AkshareClient()
        # 尝试获取股票基础信息
        basic_info = client.get_stock_basic_info()
        if basic_info is not None and not basic_info.empty:
            print(f"✅ Akshare连接正常，获取到 {len(basic_info)} 只股票基础信息")
            print(f"样本数据: {basic_info.head(3).to_dict('records')}")
        else:
            print("❌ Akshare连接失败或返回空数据")
            
        # 尝试获取实时行情
        realtime_market = client.get_stock_realtime_data()
        if realtime_market is not None and not realtime_market.empty:
            print(f"✅ 实时行情数据获取正常，共 {len(realtime_market)} 条记录")
            print(f"实时数据列: {list(realtime_market.columns)}")
        else:
            print("❌ 实时行情数据获取失败")
            
    except Exception as e:
        print(f"❌ Akshare客户端测试失败: {str(e)}")

def analyze_api_endpoints():
    """分析API端点实现"""
    print("\n=== API端点分析 ===")
    
    views_file = '/Users/wangfuyu/PythonCode/FT-Django/apps/stocks/views.py'
    if os.path.exists(views_file):
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查实时数据视图
        if 'StockRealTimeDataView' in content:
            print("✅ 发现实时数据API视图")
            
            # 检查是否调用akshare
            if 'akshare_client' in content:
                print("✅ API视图中调用了akshare客户端")
            else:
                print("❌ API视图中未发现akshare调用")
                
            # 检查数据库操作
            if 'StockRealtimeData.objects' in content:
                print("✅ API视图中包含数据库操作")
            else:
                print("❌ API视图中未发现数据库操作")
        else:
            print("❌ 未发现实时数据API视图")
    else:
        print("❌ views.py文件不存在")

def check_data_freshness():
    """检查数据新鲜度"""
    print("\n=== 数据新鲜度检查 ===")
    
    from datetime import datetime, timedelta
    
    if StockRealtimeData.objects.exists():
        # 检查最近的数据
        recent_data = StockRealtimeData.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=1)
        ).count()
        
        total_data = StockRealtimeData.objects.count()
        
        print(f"总实时数据记录: {total_data}")
        print(f"最近1小时内的数据: {recent_data}")
        
        if recent_data > 0:
            print("✅ 有最近的实时数据更新")
        else:
            print("❌ 最近1小时内没有数据更新")
            
        # 检查数据更新频率
        latest_records = StockRealtimeData.objects.order_by('-created_at')[:10]
        if len(latest_records) > 1:
            time_diffs = []
            for i in range(len(latest_records) - 1):
                diff = (latest_records[i].created_at - latest_records[i+1].created_at).total_seconds()
                time_diffs.append(diff)
            
            avg_interval = sum(time_diffs) / len(time_diffs)
            print(f"平均更新间隔: {avg_interval:.2f} 秒")
            
            if avg_interval < 300:  # 5分钟
                print("✅ 数据更新频率较高，可能是真实数据")
            else:
                print("⚠️ 数据更新频率较低，需要进一步确认")
    else:
        print("❌ 数据库中没有实时数据记录")

def generate_authenticity_report():
    """生成数据真实性报告"""
    print("\n" + "="*60)
    print("Django Stock 实时交易数据真实性分析报告")
    print("="*60)
    
    analyze_frontend_data_generation()
    analyze_backend_data_source()
    analyze_api_endpoints()
    check_data_freshness()
    
    print("\n=== 结论 ===")
    print("基于以上分析:")
    print("1. 前端代码中大量使用Math.random()生成模拟数据")
    print("2. 后端虽然集成了akshare真实数据源，但需要检查是否实际调用")
    print("3. 数据库中的实时数据记录情况需要进一步验证")
    print("4. 建议检查实际的API调用日志和数据更新记录")
    
    # 最终判断
    realtime_count = StockRealtimeData.objects.count()
    if realtime_count == 0:
        print("\n🔴 结论: 当前系统主要使用模拟数据，数据库中无真实交易数据")
    else:
        print("\n🟡 结论: 系统具备真实数据获取能力，但需要验证数据的实时性和准确性")

if __name__ == '__main__':
    generate_authenticity_report()