import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone
from django.db import transaction

from utils.akshare_client import AkshareClient
from ..models import (
    StockBasicInfo, 
    StockDailyHistoryData, 
    StockWeeklyHistoryData, 
    StockMonthlyHistoryData
)

logger = logging.getLogger(__name__)


class HistoryDataService:
    """历史数据采集服务"""
    
    def __init__(self):
        self.akshare_client = AkshareClient()
        self.period_model_mapping = {
            'daily': StockDailyHistoryData,
            'weekly': StockWeeklyHistoryData,
            'monthly': StockMonthlyHistoryData
        }
    
    def get_last_trading_date(self) -> str:
        """
        获取最近的交易日期
        
        Returns:
            str: 最近交易日期，格式为YYYYMMDD
        """
        today = datetime.now()
        
        # 如果是周末，往前推到周五
        if today.weekday() == 5:  # 周六
            today = today - timedelta(days=1)
        elif today.weekday() == 6:  # 周日
            today = today - timedelta(days=2)
        
        # 如果当前时间在16:00之前，使用前一个交易日
        if today.hour < 16:
            today = today - timedelta(days=1)
            # 再次检查是否是周末
            if today.weekday() == 5:  # 周六
                today = today - timedelta(days=1)
            elif today.weekday() == 6:  # 周日
                today = today - timedelta(days=2)
        
        return today.strftime('%Y%m%d')
    
    def get_stock_listing_date(self, symbol: str) -> Optional[str]:
        """
        获取股票上市日期
        
        Args:
            symbol: 股票代码
            
        Returns:
            Optional[str]: 上市日期，格式为YYYYMMDD，如果获取失败返回None
        """
        try:
            # 先从数据库中查找
            stock_info = StockBasicInfo.objects.filter(stock_code=symbol).first()
            if stock_info and stock_info.list_date:
                return stock_info.list_date.strftime('%Y%m%d')
            
            # 如果数据库中没有，尝试从akshare获取
            stock_detail = self.akshare_client.get_stock_info(symbol)
            if stock_detail is not None and not stock_detail.empty:
                # 查找上市日期相关字段
                for col in stock_detail.columns:
                    if '上市' in col or 'listing' in col.lower() or '日期' in col:
                        listing_date = stock_detail[col].iloc[0]
                        if pd.notna(listing_date):
                            # 尝试解析日期
                            try:
                                if isinstance(listing_date, str):
                                    # 处理各种日期格式
                                    listing_date = listing_date.replace('-', '').replace('/', '')
                                    if len(listing_date) == 8 and listing_date.isdigit():
                                        return listing_date
                                elif hasattr(listing_date, 'strftime'):
                                    return listing_date.strftime('%Y%m%d')
                            except Exception as e:
                                logger.warning(f"解析上市日期失败 {symbol}: {e}")
                                continue
            
            # 如果都获取不到，返回默认日期（5年前）
            default_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y%m%d')
            logger.warning(f"无法获取股票 {symbol} 的上市日期，使用默认日期: {default_date}")
            return default_date
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 上市日期失败: {e}")
            return None
    
    def get_last_data_date(self, symbol: str, period: str) -> Optional[str]:
        """
        获取数据库中该股票最后的数据日期
        
        Args:
            symbol: 股票代码
            period: 数据周期
            
        Returns:
            Optional[str]: 最后数据日期，格式为YYYYMMDD
        """
        try:
            model = self.period_model_mapping.get(period)
            if not model:
                return None
            
            last_record = model.objects.filter(stock_code=symbol).order_by('-trade_date').first()
            if last_record:
                return last_record.trade_date.strftime('%Y%m%d')
            return None
            
        except Exception as e:
            logger.error(f"获取最后数据日期失败 {symbol}-{period}: {e}")
            return None
    
    def determine_date_range(self, symbol: str, period: str, end_date: str) -> Tuple[Optional[str], str]:
        """
        确定数据采集的日期范围
        
        Args:
            symbol: 股票代码
            period: 数据周期
            end_date: 结束日期
            
        Returns:
            Tuple[Optional[str], str]: (开始日期, 结束日期)，如果不需要更新返回(None, end_date)
        """
        # 获取数据库中最后的数据日期
        last_data_date = self.get_last_data_date(symbol, period)
        
        if last_data_date is None:
            # 历史数据中不存在该symbol信息，使用上市日期
            start_date = self.get_stock_listing_date(symbol)
            return start_date, end_date
        
        # 检查最后数据日期是否与结束日期一致
        if last_data_date == end_date:
            # 不需要更新
            return None, end_date
        
        # 需要更新，从最后数据日期的下一天开始
        try:
            last_date = datetime.strptime(last_data_date, '%Y%m%d')
            start_date = (last_date + timedelta(days=1)).strftime('%Y%m%d')
            return start_date, end_date
        except Exception as e:
            logger.error(f"解析最后数据日期失败 {symbol}: {e}")
            return self.get_stock_listing_date(symbol), end_date
    
    def fetch_history_data(self, symbol: str, period: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码
            period: 数据周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Optional[pd.DataFrame]: 历史数据
        """
        try:
            data = self.akshare_client.get_stock_history_data(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust='qfq'  # 前复权
            )
            
            if data is not None and not data.empty:
                logger.info(f"成功获取 {symbol} {period} 数据: {len(data)} 条记录")
                return data
            else:
                logger.warning(f"未获取到 {symbol} {period} 数据")
                return None
                
        except Exception as e:
            logger.error(f"获取历史数据失败 {symbol}-{period}: {e}")
            return None
    
    def save_history_data(self, symbol: str, period: str, data: pd.DataFrame, 
                         task_start_time: datetime, task_end_time: datetime) -> int:
        """
        保存历史数据到数据库
        
        Args:
            symbol: 股票代码
            period: 数据周期
            data: 历史数据
            task_start_time: 任务开始时间
            task_end_time: 任务结束时间
            
        Returns:
            int: 保存的记录数
        """
        model = self.period_model_mapping.get(period)
        if not model:
            logger.error(f"未知的数据周期: {period}")
            return 0
        
        saved_count = 0
        
        try:
            with transaction.atomic():
                for _, row in data.iterrows():
                    try:
                        # 解析日期
                        date_str = str(row['日期'])
                        if len(date_str) == 10:  # YYYY-MM-DD格式
                            trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        elif len(date_str) == 8:  # YYYYMMDD格式
                            trade_date = datetime.strptime(date_str, '%Y%m%d').date()
                        else:
                            logger.warning(f"无法解析日期格式: {date_str}")
                            continue
                        
                        # 创建或更新记录
                        record, created = model.objects.update_or_create(
                            stock_code=symbol,
                            trade_date=trade_date,
                            defaults={
                                'open_price': float(row.get('开盘', 0)),
                                'close_price': float(row.get('收盘', 0)),
                                'high_price': float(row.get('最高', 0)),
                                'low_price': float(row.get('最低', 0)),
                                'volume': int(row.get('成交量', 0)),
                                'amount': float(row.get('成交额', 0)),
                                'amplitude': float(row.get('振幅', 0)),
                                'change_pct': float(row.get('涨跌幅', 0)),
                                'change_amount': float(row.get('涨跌额', 0)),
                                'turnover_rate': float(row.get('换手率', 0)),
                                'task_start_time': task_start_time,
                                'task_end_time': task_end_time
                            }
                        )
                        
                        if created:
                            saved_count += 1
                            
                    except Exception as e:
                        logger.error(f"保存单条记录失败 {symbol}-{period}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"保存历史数据失败 {symbol}-{period}: {e}")
            return 0
        
        logger.info(f"成功保存 {symbol} {period} 数据: {saved_count} 条新记录")
        return saved_count
    
    def collect_stock_history_data(self, symbols: List[str], periods: List[str] = None) -> Dict[str, Dict[str, int]]:
        """
        采集股票历史数据
        
        Args:
            symbols: 股票代码列表
            periods: 数据周期列表，默认为['daily', 'weekly', 'monthly']
            
        Returns:
            Dict[str, Dict[str, int]]: 采集结果统计
        """
        if periods is None:
            periods = ['daily', 'weekly', 'monthly']
        
        task_start_time = timezone.now()
        end_date = self.get_last_trading_date()
        
        results = {}
        
        for symbol in symbols:
            results[symbol] = {}
            
            for period in periods:
                try:
                    logger.info(f"开始采集 {symbol} {period} 历史数据")
                    
                    # 确定日期范围
                    start_date, _ = self.determine_date_range(symbol, period, end_date)
                    
                    if start_date is None:
                        logger.info(f"{symbol} {period} 数据已是最新，无需更新")
                        results[symbol][period] = 0
                        continue
                    
                    # 获取历史数据
                    data = self.fetch_history_data(symbol, period, start_date, end_date)
                    
                    if data is None or data.empty:
                        logger.warning(f"未获取到 {symbol} {period} 数据")
                        results[symbol][period] = 0
                        continue
                    
                    # 保存数据
                    task_end_time = timezone.now()
                    saved_count = self.save_history_data(
                        symbol, period, data, task_start_time, task_end_time
                    )
                    
                    results[symbol][period] = saved_count
                    
                except Exception as e:
                    logger.error(f"采集 {symbol} {period} 数据失败: {e}")
                    results[symbol][period] = 0
        
        return results
    
    def collect_all_stocks_history_data(self, periods: List[str] = None) -> Dict[str, Dict[str, int]]:
        """
        采集所有活跃股票的历史数据
        
        Args:
            periods: 数据周期列表
            
        Returns:
            Dict[str, Dict[str, int]]: 采集结果统计
        """
        # 获取所有活跃股票代码
        active_stocks = StockBasicInfo.objects.filter(is_active=True).values_list('stock_code', flat=True)
        symbols = list(active_stocks)
        
        logger.info(f"开始采集 {len(symbols)} 只股票的历史数据")
        
        return self.collect_stock_history_data(symbols, periods)