#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票数据同步脚本
从远程MySQL数据库同步股票基础信息到本地Django数据库
"""

import os
import sys
import django
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime

# 设置Django环境
sys.path.append('/Users/wangfuyu/PythonCode/FT-Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.stocks.models import StockBasicInfo
from django.conf import settings
from django.core.management import call_command

# 远程MySQL连接配置
REMOTE_DB_CONFIG = {
    'host': '115.190.80.219',
    'port': 3306,
    'user': 'root',
    'password': 'Eccom@12345',
    'database': 'flask_stock',
    'charset': 'utf8mb4',
    'connect_timeout': 30,
    'autocommit': True
}

# 新增：根据股票代码推断交易所
def derive_market_from_code(code: str) -> str:
    try:
        c = (code or '').strip()
        if not c:
            return 'SH'
        # 科创板、主板(上交所)
        if c.startswith(('60', '68')):
            return 'SH'
        # 深市主板/中小板/创业板
        if c.startswith(('00', '30')):
            return 'SZ'
        # 北交所常见以8开头
        if c.startswith('8'):
            return 'BJ'
        return 'SH'
    except Exception:
        return 'SH'

def ensure_default_db_ready():
    """确保默认Django数据库存在并已迁移"""
    try:
        db = settings.DATABASES['default']
        host = db.get('HOST', 'localhost')
        user = db.get('USER', '')
        password = db.get('PASSWORD', '')
        port = int(db.get('PORT', 3306) or 3306)
        name = db.get('NAME')
        print(f"检查并创建数据库: {name} @ {host}:{port}")
        conn = pymysql.connect(host=host, user=user, password=password, port=port, charset='utf8mb4', autocommit=True)
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
            print(f"数据库 {name} 已存在或创建成功")
        finally:
            conn.close()
        print("开始执行数据库迁移...")
        call_command('migrate', interactive=False, verbosity=1)
        print("数据库迁移完成")
    except Exception as e:
        print(f"确保数据库可用失败: {e}")
        raise

def connect_remote_mysql():
    """连接远程MySQL数据库"""
    try:
        print(f"正在连接远程MySQL数据库: {REMOTE_DB_CONFIG['host']}")
        connection = pymysql.connect(**REMOTE_DB_CONFIG)
        print("远程MySQL数据库连接成功！")
        return connection
    except Exception as e:
        print(f"连接远程MySQL数据库失败: {e}")
        return None

def get_remote_stock_data(connection):
    """从远程数据库获取股票基础信息"""
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查询远程数据库的stock_basic_info表结构
        cursor.execute("DESCRIBE stock_basic_info")
        columns = cursor.fetchall()
        print("远程数据库表结构:")
        col_names = set()
        for col in columns:
            print(f"  {col['Field']}: {col['Type']}")
            col_names.add(col['Field'])
        
        # 动态构建查询字段，兼容缺失列
        select_parts = [
            "code AS stock_code",
            "name AS stock_name"
        ]
        if 'industry' in col_names:
            select_parts.append("industry")
        # 兼容不同的上市日期字段名
        if 'listing_date' in col_names:
            select_parts.append("listing_date AS list_date")
        elif 'list_date' in col_names:
            select_parts.append("list_date AS list_date")
        # market 列可选
        if 'market' in col_names:
            select_parts.append("market")
        select_clause = ",\n            ".join(select_parts)
        
        query = f"""
        SELECT 
            {select_clause}
        FROM stock_basic_info 
        WHERE code IS NOT NULL 
        AND name IS NOT NULL
        ORDER BY stock_code
        """
        
        cursor.execute(query)
        stocks = cursor.fetchall()
        print(f"从远程数据库获取到 {len(stocks)} 条股票数据")
        
        cursor.close()
        return stocks
        
    except Exception as e:
        print(f"获取远程股票数据失败: {e}")
        return []


def clear_local_stock_table():
    """清空本地StockBasicInfo表（安全：仅在拿到远程数据后调用）"""
    try:
        deleted_count, detail = StockBasicInfo.objects.all().delete()
        print(f"已清空本地StockBasicInfo表，删除 {deleted_count} 条记录")
    except Exception as e:
        print(f"清空本地StockBasicInfo表失败: {e}")
        raise


def sync_to_local_db(stocks_data):
    """将股票数据同步到本地Django数据库"""
    try:
        success_count = 0
        error_count = 0
        
        for stock in stocks_data:
            try:
                # 处理市场字段映射
                market_mapping = {
                    '上海证券交易所': 'SH',
                    '深圳证券交易所': 'SZ', 
                    '北京证券交易所': 'BJ',
                    'SH': 'SH',
                    'SZ': 'SZ',
                    'BJ': 'BJ'
                }
                raw_market = stock.get('market', '')
                if not raw_market:
                    # 缺失market时，根据代码推断
                    raw_market = derive_market_from_code(stock.get('stock_code'))
                mapped_market = market_mapping.get(raw_market, raw_market)
                if mapped_market not in ('SH', 'SZ', 'BJ'):
                    mapped_market = derive_market_from_code(stock.get('stock_code'))
                
                # 处理上市日期
                list_date = stock.get('list_date')
                if isinstance(list_date, str):
                    # 兼容多种格式
                    parsed = None
                    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y%m%d'):
                        try:
                            parsed = datetime.strptime(list_date, fmt).date()
                            break
                        except Exception:
                            continue
                    list_date = parsed
                
                # 创建或更新股票信息
                stock_obj, created = StockBasicInfo.objects.update_or_create(
                    stock_code=stock['stock_code'],
                    defaults={
                        'stock_name': stock['stock_name'],
                        'market': mapped_market,
                        'industry': stock.get('industry', ''),
                        'list_date': list_date,
                        'is_active': True
                    }
                )
                
                if created:
                    print(f"新增股票: {stock['stock_code']} - {stock['stock_name']}")
                else:
                    print(f"更新股票: {stock['stock_code']} - {stock['stock_name']}")
                    
                success_count += 1
                
            except Exception as e:
                print(f"同步股票 {stock.get('stock_code', 'Unknown')} 失败: {e}")
                error_count += 1
        
        print(f"\n同步完成! 成功: {success_count}, 失败: {error_count}")
        return success_count, error_count
        
    except Exception as e:
        print(f"同步到本地数据库失败: {e}")
        return 0, 0

def main():
    """主函数"""
    print("=== 股票数据同步开始 ===")
    print(f"开始时间: {datetime.now()}")
    
    # 连接远程数据库
    remote_conn = connect_remote_mysql()
    if not remote_conn:
        print("无法连接远程数据库，同步终止")
        return
    
    try:
        # 获取远程数据
        stocks_data = get_remote_stock_data(remote_conn)
        if not stocks_data:
            print("未获取到股票数据，本地数据不会被清空")
            return
        
        # 确保默认数据库存在并迁移（在清空和写入之前）
        ensure_default_db_ready()
        
        # 清空本地表（仅在成功获取远程数据后执行）
        clear_local_stock_table()
        
        # 同步到本地数据库
        success_count, error_count = sync_to_local_db(stocks_data)
        
        # 验证同步结果
        local_count = StockBasicInfo.objects.count()
        print(f"\n本地数据库现有股票数量: {local_count}")
        
        # 显示部分同步的股票
        print("\n最新同步的股票 (前10条):")
        recent_stocks = StockBasicInfo.objects.all()[:10]
        for stock in recent_stocks:
            print(f"  {stock.stock_code} - {stock.stock_name} - {stock.get_market_display()} - {stock.industry}")
            
    finally:
        remote_conn.close()
        print(f"\n结束时间: {datetime.now()}")
        print("=== 股票数据同步结束 ===")

if __name__ == '__main__':
    main()