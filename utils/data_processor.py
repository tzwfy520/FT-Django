import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import re
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理工具类"""
    
    @staticmethod
    def clean_stock_code(code: str) -> str:
        """
        清洗股票代码
        
        Args:
            code: 原始股票代码
        
        Returns:
            str: 清洗后的股票代码
        """
        if not code:
            return ""
        
        # 移除非数字字符
        code = re.sub(r'[^0-9]', '', str(code))
        
        # 确保6位数字
        if len(code) < 6:
            code = code.zfill(6)
        elif len(code) > 6:
            code = code[:6]
        
        return code
    
    @staticmethod
    def clean_stock_name(name: str) -> str:
        """
        清洗股票名称
        
        Args:
            name: 原始股票名称
        
        Returns:
            str: 清洗后的股票名称
        """
        if not name:
            return ""
        
        # 移除特殊字符和多余空格
        name = str(name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    @staticmethod
    def clean_numeric_value(value: Any, default: float = 0.0) -> float:
        """
        清洗数值数据
        
        Args:
            value: 原始数值
            default: 默认值
        
        Returns:
            float: 清洗后的数值
        """
        if pd.isna(value) or value is None:
            return default
        
        try:
            # 处理字符串类型的数值
            if isinstance(value, str):
                # 移除逗号、百分号等
                value = value.replace(',', '').replace('%', '').replace('万', '').replace('亿', '')
                # 处理负号
                value = value.replace('−', '-')
                # 移除其他非数字字符（保留小数点和负号）
                value = re.sub(r'[^0-9.-]', '', value)
            
            return float(value) if value != '' else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def clean_percentage_value(value: Any, default: float = 0.0) -> float:
        """
        清洗百分比数据
        
        Args:
            value: 原始百分比值
            default: 默认值
        
        Returns:
            float: 清洗后的百分比值（小数形式）
        """
        if pd.isna(value) or value is None:
            return default
        
        try:
            if isinstance(value, str):
                # 移除百分号
                value = value.replace('%', '')
                # 清洗数值
                value = DataProcessor.clean_numeric_value(value, default * 100)
                # 转换为小数形式
                return value / 100
            else:
                return DataProcessor.clean_numeric_value(value, default)
        except Exception:
            return default
    
    @staticmethod
    def clean_volume_value(value: Any, default: int = 0) -> int:
        """
        清洗成交量数据
        
        Args:
            value: 原始成交量值
            default: 默认值
        
        Returns:
            int: 清洗后的成交量值
        """
        if pd.isna(value) or value is None:
            return default
        
        try:
            if isinstance(value, str):
                # 处理万、亿等单位
                multiplier = 1
                if '万' in value:
                    multiplier = 10000
                    value = value.replace('万', '')
                elif '亿' in value:
                    multiplier = 100000000
                    value = value.replace('亿', '')
                
                # 清洗数值
                numeric_value = DataProcessor.clean_numeric_value(value, default)
                return int(numeric_value * multiplier)
            else:
                return int(DataProcessor.clean_numeric_value(value, default))
        except Exception:
            return default
    
    @staticmethod
    def clean_date_value(value: Any, default_format: str = '%Y-%m-%d') -> Optional[datetime]:
        """
        清洗日期数据
        
        Args:
            value: 原始日期值
            default_format: 默认日期格式
        
        Returns:
            Optional[datetime]: 清洗后的日期对象
        """
        if pd.isna(value) or value is None:
            return None
        
        try:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                # 尝试多种日期格式
                formats = [
                    '%Y-%m-%d',
                    '%Y/%m/%d',
                    '%Y%m%d',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y/%m/%d %H:%M:%S',
                    default_format
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                
                # 如果都失败了，尝试pandas的日期解析
                return pd.to_datetime(value)
            else:
                return pd.to_datetime(value)
        except Exception:
            return None
    
    @staticmethod
    def process_stock_realtime_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理股票实时数据
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            pd.DataFrame: 处理后的数据
        """
        if df is None or df.empty:
            return df
        
        processed_df = df.copy()
        
        try:
            # 标准化列名映射
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'current_price',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '最高': 'high',
                '最低': 'low',
                '今开': 'open',
                '昨收': 'prev_close',
                '量比': 'volume_ratio',
                '换手率': 'turnover_rate',
                '市盈率-动态': 'pe_ratio',
                '市净率': 'pb_ratio',
                '总市值': 'market_cap',
                '流通市值': 'circulating_market_cap',
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in processed_df.columns:
                    processed_df = processed_df.rename(columns={old_name: new_name})
            
            # 清洗数据
            if 'code' in processed_df.columns:
                processed_df['code'] = processed_df['code'].apply(DataProcessor.clean_stock_code)
            
            if 'name' in processed_df.columns:
                processed_df['name'] = processed_df['name'].apply(DataProcessor.clean_stock_name)
            
            # 清洗数值列
            numeric_columns = ['current_price', 'change_amount', 'high', 'low', 'open', 'prev_close']
            for col in numeric_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_numeric_value)
            
            # 清洗百分比列
            percentage_columns = ['change_percent', 'amplitude', 'volume_ratio', 'turnover_rate']
            for col in percentage_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_percentage_value)
            
            # 清洗成交量列
            volume_columns = ['volume', 'turnover', 'market_cap', 'circulating_market_cap']
            for col in volume_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_volume_value)
            
            # 清洗比率列
            ratio_columns = ['pe_ratio', 'pb_ratio']
            for col in ratio_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_numeric_value)
            
        except Exception as e:
            logger.error(f"Error processing stock realtime data: {str(e)}")
        
        return processed_df
    
    @staticmethod
    def process_stock_history_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理股票历史数据
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            pd.DataFrame: 处理后的数据
        """
        if df is None or df.empty:
            return df
        
        processed_df = df.copy()
        
        try:
            # 标准化列名映射
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate',
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in processed_df.columns:
                    processed_df = processed_df.rename(columns={old_name: new_name})
            
            # 清洗日期列
            if 'date' in processed_df.columns:
                processed_df['date'] = processed_df['date'].apply(DataProcessor.clean_date_value)
                processed_df = processed_df.dropna(subset=['date'])
            
            # 清洗数值列
            numeric_columns = ['open', 'close', 'high', 'low', 'change_amount']
            for col in numeric_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_numeric_value)
            
            # 清洗百分比列
            percentage_columns = ['change_percent', 'amplitude', 'turnover_rate']
            for col in percentage_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_percentage_value)
            
            # 清洗成交量列
            volume_columns = ['volume', 'turnover']
            for col in volume_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_volume_value)
            
            # 按日期排序
            if 'date' in processed_df.columns:
                processed_df = processed_df.sort_values('date')
            
        except Exception as e:
            logger.error(f"Error processing stock history data: {str(e)}")
        
        return processed_df
    
    @staticmethod
    def process_market_index_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理市场指数数据
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            pd.DataFrame: 处理后的数据
        """
        if df is None or df.empty:
            return df
        
        processed_df = df.copy()
        
        try:
            # 标准化列名映射
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'current_price',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'turnover',
                '开盘价': 'open',
                '最高价': 'high',
                '最低价': 'low',
                '昨收价': 'prev_close',
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in processed_df.columns:
                    processed_df = processed_df.rename(columns={old_name: new_name})
            
            # 清洗数据
            if 'code' in processed_df.columns:
                processed_df['code'] = processed_df['code'].apply(DataProcessor.clean_stock_code)
            
            if 'name' in processed_df.columns:
                processed_df['name'] = processed_df['name'].apply(DataProcessor.clean_stock_name)
            
            # 清洗数值列
            numeric_columns = ['current_price', 'change_amount', 'open', 'high', 'low', 'prev_close']
            for col in numeric_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_numeric_value)
            
            # 清洗百分比列
            if 'change_percent' in processed_df.columns:
                processed_df['change_percent'] = processed_df['change_percent'].apply(DataProcessor.clean_percentage_value)
            
            # 清洗成交量列
            volume_columns = ['volume', 'turnover']
            for col in volume_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_volume_value)
            
        except Exception as e:
            logger.error(f"Error processing market index data: {str(e)}")
        
        return processed_df
    
    @staticmethod
    def process_industry_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理行业板块数据
        
        Args:
            df: 原始数据DataFrame
        
        Returns:
            pd.DataFrame: 处理后的数据
        """
        if df is None or df.empty:
            return df
        
        processed_df = df.copy()
        
        try:
            # 标准化列名映射
            column_mapping = {
                '板块名称': 'name',
                '板块代码': 'code',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '总市值': 'market_cap',
                '换手率': 'turnover_rate',
                '上涨家数': 'up_count',
                '下跌家数': 'down_count',
                '平盘家数': 'flat_count',
                '总家数': 'total_count',
                '领涨股票': 'leading_stock',
                '领涨股票-涨跌幅': 'leading_stock_change',
            }
            
            # 重命名列
            for old_name, new_name in column_mapping.items():
                if old_name in processed_df.columns:
                    processed_df = processed_df.rename(columns={old_name: new_name})
            
            # 清洗数据
            if 'name' in processed_df.columns:
                processed_df['name'] = processed_df['name'].apply(DataProcessor.clean_stock_name)
            
            # 清洗数值列
            numeric_columns = ['change_amount']
            for col in numeric_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_numeric_value)
            
            # 清洗百分比列
            percentage_columns = ['change_percent', 'turnover_rate', 'leading_stock_change']
            for col in percentage_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(DataProcessor.clean_percentage_value)
            
            # 清洗整数列
            integer_columns = ['up_count', 'down_count', 'flat_count', 'total_count']
            for col in integer_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].apply(lambda x: int(DataProcessor.clean_numeric_value(x)))
            
            # 清洗成交量列
            if 'market_cap' in processed_df.columns:
                processed_df['market_cap'] = processed_df['market_cap'].apply(DataProcessor.clean_volume_value)
            
        except Exception as e:
            logger.error(f"Error processing industry data: {str(e)}")
        
        return processed_df
    
    @staticmethod
    def validate_data_quality(df: pd.DataFrame, required_columns: List[str] = None) -> Dict[str, Any]:
        """
        验证数据质量
        
        Args:
            df: 数据DataFrame
            required_columns: 必需的列名列表
        
        Returns:
            Dict[str, Any]: 数据质量报告
        """
        if df is None or df.empty:
            return {
                'is_valid': False,
                'error': 'DataFrame is None or empty',
                'row_count': 0,
                'column_count': 0
            }
        
        report = {
            'is_valid': True,
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_data': {},
            'duplicate_rows': 0,
            'data_types': {},
            'warnings': []
        }
        
        try:
            # 检查必需列
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    report['is_valid'] = False
                    report['warnings'].append(f"Missing required columns: {list(missing_columns)}")
            
            # 检查缺失数据
            for col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    report['missing_data'][col] = {
                        'count': int(missing_count),
                        'percentage': round(missing_count / len(df) * 100, 2)
                    }
            
            # 检查重复行
            report['duplicate_rows'] = int(df.duplicated().sum())
            
            # 检查数据类型
            for col in df.columns:
                report['data_types'][col] = str(df[col].dtype)
            
            # 数据质量警告
            if report['duplicate_rows'] > 0:
                report['warnings'].append(f"Found {report['duplicate_rows']} duplicate rows")
            
            missing_percentage = sum([info['percentage'] for info in report['missing_data'].values()])
            if missing_percentage > 10:
                report['warnings'].append(f"High missing data percentage: {missing_percentage:.2f}%")
            
        except Exception as e:
            report['is_valid'] = False
            report['error'] = str(e)
        
        return report
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame, indicators: List[str] = None) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
            indicators: 要计算的指标列表
        
        Returns:
            pd.DataFrame: 包含技术指标的DataFrame
        """
        if df is None or df.empty:
            return df
        
        if indicators is None:
            indicators = ['SMA_5', 'SMA_10', 'SMA_20', 'EMA_12', 'EMA_26', 'MACD', 'RSI']
        
        result_df = df.copy()
        
        try:
            # 确保有必要的列
            required_columns = ['close']
            if not all(col in result_df.columns for col in required_columns):
                logger.warning("Missing required columns for technical indicators")
                return result_df
            
            # 简单移动平均线 (SMA)
            if 'SMA_5' in indicators:
                result_df['SMA_5'] = result_df['close'].rolling(window=5).mean()
            if 'SMA_10' in indicators:
                result_df['SMA_10'] = result_df['close'].rolling(window=10).mean()
            if 'SMA_20' in indicators:
                result_df['SMA_20'] = result_df['close'].rolling(window=20).mean()
            
            # 指数移动平均线 (EMA)
            if 'EMA_12' in indicators:
                result_df['EMA_12'] = result_df['close'].ewm(span=12).mean()
            if 'EMA_26' in indicators:
                result_df['EMA_26'] = result_df['close'].ewm(span=26).mean()
            
            # MACD
            if 'MACD' in indicators and 'EMA_12' in result_df.columns and 'EMA_26' in result_df.columns:
                result_df['MACD'] = result_df['EMA_12'] - result_df['EMA_26']
                result_df['MACD_Signal'] = result_df['MACD'].ewm(span=9).mean()
                result_df['MACD_Histogram'] = result_df['MACD'] - result_df['MACD_Signal']
            
            # RSI
            if 'RSI' in indicators:
                delta = result_df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                result_df['RSI'] = 100 - (100 / (1 + rs))
            
            # 布林带
            if 'BOLL' in indicators:
                result_df['BOLL_MID'] = result_df['close'].rolling(window=20).mean()
                std = result_df['close'].rolling(window=20).std()
                result_df['BOLL_UPPER'] = result_df['BOLL_MID'] + (std * 2)
                result_df['BOLL_LOWER'] = result_df['BOLL_MID'] - (std * 2)
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
        
        return result_df
    
    @staticmethod
    def format_data_for_database(df: pd.DataFrame, table_type: str) -> List[Dict[str, Any]]:
        """
        格式化数据用于数据库存储
        
        Args:
            df: 数据DataFrame
            table_type: 表类型
        
        Returns:
            List[Dict[str, Any]]: 格式化后的数据列表
        """
        if df is None or df.empty:
            return []
        
        try:
            # 转换为字典列表
            records = df.to_dict('records')
            
            # 根据表类型进行特殊处理
            if table_type == 'stock_realtime':
                for record in records:
                    # 添加时间戳
                    record['update_time'] = datetime.now()
                    # 处理None值
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
            
            elif table_type == 'stock_history':
                for record in records:
                    # 确保日期格式正确
                    if 'date' in record and isinstance(record['date'], datetime):
                        record['date'] = record['date'].date()
                    # 处理None值
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
            
            return records
            
        except Exception as e:
            logger.error(f"Error formatting data for database: {str(e)}")
            return []


# 创建全局实例
data_processor = DataProcessor()