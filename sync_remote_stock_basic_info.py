#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票基础信息同步脚本
从远程MySQL数据库(flask_stock.stock_basic_info)同步数据到本地数据库(django_stock.stock_basic_info)
"""

import os
import sys
import django
import pymysql
from datetime import datetime
import logging
from typing import List, Dict, Any

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

# 使用PyMySQL作为MySQL驱动
import pymysql
pymysql.install_as_MySQLdb()

django.setup()

from apps.stocks.models import StockBasicInfo
from django.db import transaction, models
from django.conf import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_stock_basic_info.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockBasicInfoSyncer:
    """股票基础信息同步器"""
    
    def __init__(self):
        # 远程数据库配置（flask_stock数据库）
        self.remote_config = {
            'host': '115.190.80.219',
            'user': 'root',
            'password': 'Eccom@12345',
            'database': 'flask_stock',
            'charset': 'utf8mb4'
        }
        
        # 本地数据库配置（django_stock数据库）
        self.local_config = {
            'host': settings.DATABASES['default']['HOST'],
            'user': settings.DATABASES['default']['USER'],
            'password': settings.DATABASES['default']['PASSWORD'],
            'database': settings.DATABASES['default']['NAME'],
            'port': settings.DATABASES['default']['PORT'],
            'charset': 'utf8mb4'
        }
        
    def get_remote_connection(self):
        """获取远程数据库连接"""
        try:
            connection = pymysql.connect(**self.remote_config)
            logger.info("远程数据库连接成功")
            return connection
        except Exception as e:
            logger.error(f"远程数据库连接失败: {e}")
            raise
    
    def get_local_connection(self):
        """获取本地数据库连接"""
        try:
            connection = pymysql.connect(**self.local_config)
            logger.info("本地数据库连接成功")
            return connection
        except Exception as e:
            logger.error(f"本地数据库连接失败: {e}")
            raise
    
    def check_remote_table_structure(self):
        """检查远程数据库表结构"""
        connection = None
        try:
            connection = self.get_remote_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # 查看表结构
            cursor.execute("DESCRIBE stock_basic_info")
            columns = cursor.fetchall()
            logger.info("远程数据库stock_basic_info表结构:")
            for col in columns:
                logger.info(f"  {col['Field']} - {col['Type']} - {col['Null']} - {col['Key']}")
            
            return [col['Field'] for col in columns]
            
        except Exception as e:
            logger.error(f"检查远程表结构失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def fetch_remote_data(self) -> List[Dict[str, Any]]:
        """从远程数据库获取股票基础信息"""
        connection = None
        try:
            connection = self.get_remote_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # 先检查表结构
            available_columns = self.check_remote_table_structure()
            
            # 根据实际可用的列构建查询
            base_columns = ['id']
            optional_columns = {
                'stock_code': 'code',  # 可能的字段名映射
                'stock_name': 'name',
                'market': 'market',
                'industry': 'industry',
                'concept': 'concept',
                'list_date': 'list_date',
                'total_share': 'total_share',
                'float_share': 'float_share',
                'market_cap': 'market_cap',
                'is_active': 'is_active',
                'created_at': 'created_at',
                'updated_at': 'updated_at'
            }
            
            # 构建实际可用的列
            select_columns = []
            column_mapping = {}
            
            for target_col, possible_names in optional_columns.items():
                if isinstance(possible_names, str):
                    possible_names = [possible_names]
                elif isinstance(possible_names, str):
                    possible_names = [possible_names]
                else:
                    possible_names = [target_col]  # 默认使用目标列名
                
                for possible_name in possible_names:
                    if possible_name in available_columns:
                        select_columns.append(possible_name)
                        column_mapping[possible_name] = target_col
                        break
                else:
                    # 尝试其他可能的列名
                    common_mappings = {
                        'stock_code': ['code', 'symbol', 'ts_code'],
                        'stock_name': ['name', 'stock_name', 'symbol_name'],
                        'list_date': ['list_date', 'listing_date', 'ipo_date']
                    }
                    if target_col in common_mappings:
                        for alt_name in common_mappings[target_col]:
                            if alt_name in available_columns:
                                select_columns.append(alt_name)
                                column_mapping[alt_name] = target_col
                                break
            
            if not select_columns:
                # 如果没有找到匹配的列，就查询所有列
                select_columns = ['*']
                logger.warning("未找到预期的列，将查询所有列")
            
            query = f"SELECT {', '.join(select_columns)} FROM stock_basic_info LIMIT 10"
            logger.info(f"执行查询: {query}")
            
            cursor.execute(query)
            data = cursor.fetchall()
            logger.info(f"从远程数据库获取到 {len(data)} 条股票基础信息（示例数据）")
            
            # 显示示例数据
            if data:
                logger.info("示例数据:")
                for i, row in enumerate(data[:3]):
                    logger.info(f"  行{i+1}: {dict(row)}")
            
            return data, column_mapping
            
        except Exception as e:
            logger.error(f"获取远程数据失败: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def determine_market(self, stock_code: str) -> str:
        """根据股票代码确定交易所"""
        if stock_code.startswith(('60', '68', '11', '50', '51')):
            return 'SH'  # 上海证券交易所
        elif stock_code.startswith(('00', '30', '12', '15')):
            return 'SZ'  # 深圳证券交易所
        elif stock_code.startswith(('8', '4')):
            return 'BJ'  # 北京证券交易所
        else:
            # 根据原始数据的market字段判断
            return 'SH'  # 默认上海
    
    def clear_local_data(self):
        """清空本地股票基础信息表"""
        try:
            # 分批删除，避免长时间锁定
            batch_size = 1000
            total_deleted = 0
            
            while True:
                with transaction.atomic():
                    # 获取一批要删除的记录的ID
                    ids = list(StockBasicInfo.objects.values_list('id', flat=True)[:batch_size])
                    if not ids:
                        break
                    
                    # 删除这批记录
                    deleted_count = StockBasicInfo.objects.filter(id__in=ids).delete()[0]
                    total_deleted += deleted_count
                    logger.info(f"已删除 {deleted_count} 条记录，总计删除 {total_deleted} 条")
                    
                    # 如果删除的记录数少于批次大小，说明已经删除完毕
                    if len(ids) < batch_size:
                        break
            
            logger.info(f"清空本地数据表，删除了 {total_deleted} 条记录")
        except Exception as e:
            logger.error(f"清空本地数据失败: {e}")
            raise
    
    def batch_insert_data(self, data: List[Dict[str, Any]], column_mapping: Dict[str, str]):
        """批量插入数据到本地数据库"""
        try:
            batch_size = 1000
            total_inserted = 0
            
            with transaction.atomic():
                stock_objects = []
                
                for i, item in enumerate(data):
                    # 根据列映射关系获取数据
                    stock_code = ''
                    stock_name = ''
                    list_date = None
                    industry = ''
                    market_field = ''
                    
                    # 根据column_mapping获取实际字段值
                    for db_col, target_col in column_mapping.items():
                        if target_col == 'stock_code':
                            stock_code = item.get(db_col, '')
                        elif target_col == 'stock_name':
                            stock_name = item.get(db_col, '')
                        elif target_col == 'list_date':
                            if item.get(db_col):
                                if isinstance(item[db_col], str):
                                    try:
                                        list_date = datetime.strptime(item[db_col], '%Y-%m-%d').date()
                                    except:
                                        list_date = None
                                else:
                                    list_date = item[db_col]
                        elif target_col == 'industry':
                            industry = item.get(db_col, '')
                        elif target_col == 'market':
                            market_field = item.get(db_col, '')
                    
                    # 处理市场字段
                    market = self.determine_market(stock_code)
                    if market_field:
                        # 如果远程数据有market字段，优先使用
                        market_mapping = {
                            'SH': 'SH', 'sh': 'SH', '上海': 'SH', '上交所': 'SH',
                            'SZ': 'SZ', 'sz': 'SZ', '深圳': 'SZ', '深交所': 'SZ',
                            'BJ': 'BJ', 'bj': 'BJ', '北京': 'BJ', '北交所': 'BJ'
                        }
                        market = market_mapping.get(str(market_field).upper(), market)
                    
                    # 创建StockBasicInfo对象
                    stock_obj = StockBasicInfo(
                        stock_code=stock_code,
                        stock_name=stock_name or '',
                        market=market,
                        industry=industry or '',
                        concept=item.get('concept', ''),
                        list_date=list_date,
                        total_share=item.get('total_share'),
                        float_share=item.get('float_share'),
                        market_cap=item.get('market_cap'),
                        is_active=bool(item.get('is_active', True))
                    )
                    stock_objects.append(stock_obj)
                    
                    # 批量插入
                    if len(stock_objects) >= batch_size or i == len(data) - 1:
                        StockBasicInfo.objects.bulk_create(stock_objects, ignore_conflicts=True)
                        total_inserted += len(stock_objects)
                        logger.info(f"已插入 {total_inserted}/{len(data)} 条记录")
                        stock_objects = []
                
                logger.info(f"批量插入完成，共插入 {total_inserted} 条记录")
                
        except Exception as e:
            logger.error(f"批量插入数据失败: {e}")
            raise
    
    def sync_data(self):
        """执行数据同步"""
        try:
            logger.info("开始同步股票基础信息数据")
            start_time = datetime.now()
            
            # 1. 获取远程数据
            logger.info("步骤1: 获取远程数据")
            remote_data, column_mapping = self.fetch_remote_data()
            
            if not remote_data:
                logger.warning("远程数据为空，同步终止")
                return
            
            logger.info(f"列映射关系: {column_mapping}")
            
            # 获取完整的远程数据
            logger.info("获取完整的远程数据...")
            connection = self.get_remote_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            
            # 构建完整查询 - 使用已知的可用列
            available_columns = ['code', 'name', 'industry', 'listing_date']
            query = f"SELECT {', '.join(available_columns)} FROM stock_basic_info"
            
            cursor.execute(query)
            full_remote_data = cursor.fetchall()
            connection.close()
            
            logger.info(f"获取到完整数据 {len(full_remote_data)} 条记录")
            
            # 2. 清空本地数据
            logger.info("步骤2: 清空本地数据")
            self.clear_local_data()
            
            # 3. 批量插入新数据
            logger.info("步骤3: 批量插入新数据")
            self.batch_insert_data(full_remote_data, column_mapping)
            
            # 4. 验证同步结果
            local_count = StockBasicInfo.objects.count()
            logger.info(f"同步完成，本地数据库现有 {local_count} 条记录")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"数据同步完成，耗时: {duration:.2f} 秒")
            
        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            raise
    
    def verify_sync(self):
        """验证同步结果"""
        try:
            # 统计本地数据
            total_count = StockBasicInfo.objects.count()
            active_count = StockBasicInfo.objects.filter(is_active=True).count()
            
            # 按市场统计
            sh_count = StockBasicInfo.objects.filter(market='SH').count()
            sz_count = StockBasicInfo.objects.filter(market='SZ').count()
            bj_count = StockBasicInfo.objects.filter(market='BJ').count()
            
            logger.info(f"同步验证结果:")
            logger.info(f"  总记录数: {total_count}")
            logger.info(f"  有效记录数: {active_count}")
            logger.info(f"  上海交易所: {sh_count}")
            logger.info(f"  深圳交易所: {sz_count}")
            logger.info(f"  北京交易所: {bj_count}")
            
            # 检查是否有重复的股票代码
            duplicate_codes = StockBasicInfo.objects.values('stock_code').annotate(
                count=models.Count('stock_code')
            ).filter(count__gt=1)
            
            if duplicate_codes.exists():
                logger.warning(f"发现重复的股票代码: {list(duplicate_codes)}")
            else:
                logger.info("未发现重复的股票代码")
                
        except Exception as e:
            logger.error(f"验证同步结果失败: {e}")

def main():
    """主函数"""
    try:
        syncer = StockBasicInfoSyncer()
        
        # 执行同步
        syncer.sync_data()
        
        # 验证结果
        syncer.verify_sync()
        
        logger.info("股票基础信息同步任务完成")
        
    except Exception as e:
        logger.error(f"同步任务执行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()