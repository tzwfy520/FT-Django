import pymysql
import redis
import logging
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from django.conf import settings
import pandas as pd
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self._mysql_pool = None
        self._redis_client = None
        self._init_connections()
    
    def _init_connections(self):
        """初始化数据库连接"""
        try:
            # 初始化MySQL连接池
            self._mysql_config = {
                'host': getattr(settings, 'MYSQL_HOST', '115.190.80.219'),
                'port': getattr(settings, 'MYSQL_PORT', 3306),
                'user': getattr(settings, 'MYSQL_USER', 'root'),
                'password': getattr(settings, 'MYSQL_PASSWORD', 'Eccom@12345'),
                'database': getattr(settings, 'MYSQL_DATABASE', 'django_stock'),
                'charset': 'utf8mb4',
                'autocommit': True,
                'cursorclass': pymysql.cursors.DictCursor
            }
            
            # 初始化Redis连接
            self._redis_config = {
                'host': getattr(settings, 'REDIS_HOST', 'localhost'),
                'port': getattr(settings, 'REDIS_PORT', 6379),
                'db': getattr(settings, 'REDIS_DB', 0),
                'password': getattr(settings, 'REDIS_PASSWORD', None),
                'decode_responses': True
            }
            
            logger.info("Database connections initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database connections: {str(e)}")
    
    @contextmanager
    def get_mysql_connection(self):
        """获取MySQL连接上下文管理器"""
        connection = None
        try:
            connection = pymysql.connect(**self._mysql_config)
            yield connection
        except Exception as e:
            logger.error(f"MySQL connection error: {str(e)}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def get_redis_client(self) -> redis.Redis:
        """获取Redis客户端"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(**self._redis_config)
                # 测试连接
                self._redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Redis connection error: {str(e)}")
                self._redis_client = None
        
        return self._redis_client
    
    def execute_query(self, query: str, params: Tuple = None, fetch_all: bool = True) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_all: 是否获取所有结果
        
        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        try:
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    if fetch_all:
                        return cursor.fetchall()
                    else:
                        return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return []
    
    def execute_insert(self, table: str, data: Dict[str, Any]) -> bool:
        """
        执行插入语句
        
        Args:
            table: 表名
            data: 插入数据
        
        Returns:
            bool: 是否成功
        """
        try:
            columns = list(data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, list(data.values()))
                    connection.commit()
                    return True
        except Exception as e:
            logger.error(f"Error executing insert: {str(e)}")
            return False
    
    def execute_batch_insert(self, table: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        执行批量插入
        
        Args:
            table: 表名
            data_list: 插入数据列表
        
        Returns:
            bool: 是否成功
        """
        if not data_list:
            return True
        
        try:
            columns = list(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            values_list = [list(data.values()) for data in data_list]
            
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(query, values_list)
                    connection.commit()
                    return True
        except Exception as e:
            logger.error(f"Error executing batch insert: {str(e)}")
            return False
    
    def execute_upsert(self, table: str, data: Dict[str, Any], unique_keys: List[str]) -> bool:
        """
        执行插入或更新语句
        
        Args:
            table: 表名
            data: 数据
            unique_keys: 唯一键列表
        
        Returns:
            bool: 是否成功
        """
        try:
            columns = list(data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            
            # 构建ON DUPLICATE KEY UPDATE子句
            update_clauses = []
            for col in columns:
                if col not in unique_keys:
                    update_clauses.append(f"{col} = VALUES({col})")
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)}) 
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {', '.join(update_clauses)}
            """
            
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, list(data.values()))
                    connection.commit()
                    return True
        except Exception as e:
            logger.error(f"Error executing upsert: {str(e)}")
            return False
    
    def execute_batch_upsert(self, table: str, data_list: List[Dict[str, Any]], unique_keys: List[str]) -> bool:
        """
        执行批量插入或更新
        
        Args:
            table: 表名
            data_list: 数据列表
            unique_keys: 唯一键列表
        
        Returns:
            bool: 是否成功
        """
        if not data_list:
            return True
        
        try:
            columns = list(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            
            # 构建ON DUPLICATE KEY UPDATE子句
            update_clauses = []
            for col in columns:
                if col not in unique_keys:
                    update_clauses.append(f"{col} = VALUES({col})")
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)}) 
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {', '.join(update_clauses)}
            """
            
            values_list = [list(data.values()) for data in data_list]
            
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(query, values_list)
                    connection.commit()
                    return True
        except Exception as e:
            logger.error(f"Error executing batch upsert: {str(e)}")
            return False
    
    def get_table_info(self, table: str) -> Dict[str, Any]:
        """
        获取表信息
        
        Args:
            table: 表名
        
        Returns:
            Dict[str, Any]: 表信息
        """
        try:
            # 获取表结构
            structure_query = f"DESCRIBE {table}"
            structure = self.execute_query(structure_query)
            
            # 获取表统计信息
            stats_query = f"""
                SELECT 
                    table_rows as row_count,
                    data_length as data_size,
                    index_length as index_size,
                    (data_length + index_length) as total_size
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """
            stats = self.execute_query(stats_query, (self._mysql_config['database'], table), fetch_all=False)
            
            return {
                'structure': structure,
                'statistics': stats or {}
            }
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return {}
    
    def get_database_tables(self) -> List[Dict[str, Any]]:
        """
        获取数据库所有表信息
        
        Returns:
            List[Dict[str, Any]]: 表信息列表
        """
        try:
            query = f"""
                SELECT 
                    table_name,
                    table_rows as row_count,
                    data_length as data_size,
                    index_length as index_size,
                    (data_length + index_length) as total_size,
                    create_time,
                    update_time
                FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name
            """
            return self.execute_query(query, (self._mysql_config['database'],))
        except Exception as e:
            logger.error(f"Error getting database tables: {str(e)}")
            return []
    
    def cache_set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
        
        Returns:
            bool: 是否成功
        """
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                # 序列化复杂对象
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, default=str)
                
                redis_client.setex(key, expire, value)
                return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
        return False
    
    def cache_get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
        
        Returns:
            Any: 缓存值
        """
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                value = redis_client.get(key)
                if value:
                    # 尝试反序列化JSON
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
        return default
    
    def cache_delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否成功
        """
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                redis_client.delete(key)
                return True
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
        return False
    
    def cache_exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否存在
        """
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {str(e)}")
        return False
    
    def get_stock_basic_info_from_external(self) -> List[Dict[str, Any]]:
        """
        从外部数据库获取股票基础信息
        
        Returns:
            List[Dict[str, Any]]: 股票基础信息列表
        """
        try:
            # 连接外部数据库
            external_config = {
                'host': '115.190.90.219',
                'port': 3306,
                'user': 'root',
                'password': 'Eccom@12345',
                'database': 'flask_stock',
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
            
            connection = pymysql.connect(**external_config)
            try:
                with connection.cursor() as cursor:
                    query = """
                        SELECT 
                            stock_code as code,
                            stock_name as name,
                            list_date,
                            industry,
                            market
                        FROM stock_basic_info
                        WHERE stock_code IS NOT NULL AND stock_name IS NOT NULL
                        ORDER BY stock_code
                    """
                    cursor.execute(query)
                    return cursor.fetchall()
            finally:
                connection.close()
                
        except Exception as e:
            logger.error(f"Error getting stock basic info from external database: {str(e)}")
            return []
    
    def test_connections(self) -> Dict[str, bool]:
        """
        测试数据库连接
        
        Returns:
            Dict[str, bool]: 连接测试结果
        """
        results = {
            'mysql': False,
            'redis': False
        }
        
        # 测试MySQL连接
        try:
            with self.get_mysql_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    results['mysql'] = True
        except Exception as e:
            logger.error(f"MySQL connection test failed: {str(e)}")
        
        # 测试Redis连接
        try:
            redis_client = self.get_redis_client()
            if redis_client:
                redis_client.ping()
                results['redis'] = True
        except Exception as e:
            logger.error(f"Redis connection test failed: {str(e)}")
        
        return results


class StockDataManager:
    """股票数据管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_stock_realtime_data(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        保存股票实时数据
        
        Args:
            data_list: 实时数据列表
        
        Returns:
            bool: 是否成功
        """
        if not data_list:
            return True
        
        try:
            # 添加更新时间
            current_time = datetime.now()
            for data in data_list:
                data['update_time'] = current_time
            
            # 批量插入或更新
            return self.db.execute_batch_upsert(
                'stocks_stockrealtimedata',
                data_list,
                ['stock_code']
            )
        except Exception as e:
            logger.error(f"Error saving stock realtime data: {str(e)}")
            return False
    
    def save_stock_history_data(self, stock_code: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        保存股票历史数据
        
        Args:
            stock_code: 股票代码
            data_list: 历史数据列表
        
        Returns:
            bool: 是否成功
        """
        if not data_list:
            return True
        
        try:
            # 添加股票代码
            for data in data_list:
                data['stock_code'] = stock_code
            
            # 批量插入或更新
            return self.db.execute_batch_upsert(
                'stocks_stockhistorydata',
                data_list,
                ['stock_code', 'date']
            )
        except Exception as e:
            logger.error(f"Error saving stock history data: {str(e)}")
            return False
    
    def get_stock_realtime_data(self, stock_codes: List[str] = None) -> List[Dict[str, Any]]:
        """
        获取股票实时数据
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            List[Dict[str, Any]]: 实时数据列表
        """
        try:
            if stock_codes:
                placeholders = ', '.join(['%s'] * len(stock_codes))
                query = f"""
                    SELECT * FROM stocks_stockrealtimedata 
                    WHERE stock_code IN ({placeholders})
                    ORDER BY stock_code
                """
                return self.db.execute_query(query, stock_codes)
            else:
                query = "SELECT * FROM stocks_stockrealtimedata ORDER BY stock_code"
                return self.db.execute_query(query)
        except Exception as e:
            logger.error(f"Error getting stock realtime data: {str(e)}")
            return []
    
    def get_stock_history_data(self, stock_code: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            List[Dict[str, Any]]: 历史数据列表
        """
        try:
            query = "SELECT * FROM stocks_stockhistorydata WHERE stock_code = %s"
            params = [stock_code]
            
            if start_date:
                query += " AND date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= %s"
                params.append(end_date)
            
            query += " ORDER BY date"
            
            return self.db.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error getting stock history data: {str(e)}")
            return []


# 创建全局实例
db_manager = DatabaseManager()
stock_data_manager = StockDataManager(db_manager)