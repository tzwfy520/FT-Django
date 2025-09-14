import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, List, Any
import time
import random

logger = logging.getLogger(__name__)


class AkshareClient:
    """Akshare数据接口封装类"""
    
    def __init__(self, rate_limit: float = 0.5):
        """
        初始化Akshare客户端
        
        Args:
            rate_limit: 请求间隔时间(秒)，避免频繁请求
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """请求频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last + random.uniform(0.1, 0.3)
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _safe_request(self, func, *args, **kwargs) -> Optional[pd.DataFrame]:
        """安全的请求包装器"""
        try:
            self._rate_limit_wait()
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame) and not result.empty:
                return result
            else:
                logger.warning(f"Empty result from {func.__name__}")
                return None
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    
    # ==================== 股票基础信息 ====================
    
    def get_stock_basic_info(self) -> Optional[pd.DataFrame]:
        """获取股票基础信息"""
        return self._safe_request(ak.stock_info_a_code_name)
    
    def get_stock_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取单只股票详细信息"""
        return self._safe_request(ak.stock_individual_info_em, symbol=symbol)
    
    # ==================== 股票实时数据 ====================
    
    def get_stock_realtime_data(self) -> Optional[pd.DataFrame]:
        """获取A股实时行情数据"""
        return self._safe_request(ak.stock_zh_a_spot_em)
    
    def get_stock_realtime_single(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取单只股票实时数据"""
        return self._safe_request(ak.stock_zh_a_hist, symbol=symbol, period="daily", start_date="2024-01-01", end_date="2024-01-01", adjust="")
    
    # ==================== 股票历史数据 ====================
    
    def get_stock_history_data(self, symbol: str, start_date: str = None, end_date: str = None, 
                              period: str = "daily", adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            period: 周期 daily/weekly/monthly
            adjust: 复权类型 qfq前复权/hfq后复权/空字符串不复权
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        return self._safe_request(
            ak.stock_zh_a_hist,
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
    
    def get_stock_minute_data(self, symbol: str, period: str = "1") -> Optional[pd.DataFrame]:
        """
        获取股票分钟级数据
        
        Args:
            symbol: 股票代码
            period: 分钟周期 1/5/15/30/60
        """
        return self._safe_request(ak.stock_zh_a_hist_min_em, symbol=symbol, period=period)
    
    # ==================== 大盘指数数据 ====================
    
    def get_market_index_realtime(self) -> Optional[pd.DataFrame]:
        """获取大盘指数实时数据"""
        return self._safe_request(ak.stock_zh_index_spot_em)
    
    def get_market_index_history(self, symbol: str = "000001", start_date: str = None, 
                                end_date: str = None) -> Optional[pd.DataFrame]:
        """
        获取大盘指数历史数据
        
        Args:
            symbol: 指数代码，默认上证指数
            start_date: 开始日期
            end_date: 结束日期
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        return self._safe_request(
            ak.stock_zh_index_daily_em,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    
    # ==================== 行业板块数据 ====================
    
    def get_industry_info(self) -> Optional[pd.DataFrame]:
        """获取行业板块信息"""
        return self._safe_request(ak.stock_board_industry_name_em)
    
    def get_industry_realtime_data(self) -> Optional[pd.DataFrame]:
        """获取行业板块实时数据"""
        return self._safe_request(ak.stock_board_industry_spot_em)
    
    def get_industry_stocks(self, industry_name: str) -> Optional[pd.DataFrame]:
        """获取行业板块成分股"""
        return self._safe_request(ak.stock_board_industry_cons_em, symbol=industry_name)
    
    # ==================== 概念板块数据 ====================
    
    def get_concept_info(self) -> Optional[pd.DataFrame]:
        """获取概念板块信息"""
        return self._safe_request(ak.stock_board_concept_name_em)
    
    def get_concept_realtime_data(self) -> Optional[pd.DataFrame]:
        """获取概念板块实时数据"""
        return self._safe_request(ak.stock_board_concept_spot_em)
    
    def get_concept_stocks(self, concept_name: str) -> Optional[pd.DataFrame]:
        """获取概念板块成分股"""
        return self._safe_request(ak.stock_board_concept_cons_em, symbol=concept_name)
    
    # ==================== 资金流向数据 ====================
    
    def get_money_flow_realtime(self) -> Optional[pd.DataFrame]:
        """获取实时资金流向数据"""
        return self._safe_request(ak.stock_individual_fund_flow_rank)
    
    def get_money_flow_history(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取个股历史资金流向"""
        return self._safe_request(ak.stock_individual_fund_flow, symbol=symbol)
    
    def get_market_money_flow(self) -> Optional[pd.DataFrame]:
        """获取大盘资金流向"""
        return self._safe_request(ak.stock_market_fund_flow)
    
    # ==================== 龙虎榜数据 ====================
    
    def get_dragon_tiger_list(self, date: str = None) -> Optional[pd.DataFrame]:
        """
        获取龙虎榜数据
        
        Args:
            date: 日期 YYYY-MM-DD，默认最新交易日
        """
        if not date:
            date = datetime.now().strftime('%Y%m%d')
        
        return self._safe_request(ak.stock_lhb_detail_daily_sina, date=date)
    
    # ==================== 融资融券数据 ====================
    
    def get_margin_trading_data(self, date: str = None) -> Optional[pd.DataFrame]:
        """
        获取融资融券数据
        
        Args:
            date: 日期 YYYY-MM-DD
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return self._safe_request(ak.stock_margin_underlying_info_szse, date=date)
    
    # ==================== 股票日历数据 ====================
    
    def get_stock_calendar(self, year: int = None) -> Optional[pd.DataFrame]:
        """
        获取股票交易日历
        
        Args:
            year: 年份，默认当前年份
        """
        if not year:
            year = datetime.now().year
        
        return self._safe_request(ak.tool_trade_date_hist_sina, year=str(year))
    
    # ==================== 新股数据 ====================
    
    def get_new_stock_info(self) -> Optional[pd.DataFrame]:
        """获取新股信息"""
        return self._safe_request(ak.stock_zh_a_new)
    
    # ==================== 股东信息 ====================
    
    def get_stock_holders(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取股票股东信息"""
        return self._safe_request(ak.stock_zh_a_gdhs, symbol=symbol)
    
    # ==================== 财务数据 ====================
    
    def get_financial_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取股票财务数据"""
        return self._safe_request(ak.stock_financial_em, symbol=symbol)
    
    def get_balance_sheet(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取资产负债表"""
        return self._safe_request(ak.stock_balance_sheet_by_report_em, symbol=symbol)
    
    def get_profit_statement(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取利润表"""
        return self._safe_request(ak.stock_profit_sheet_by_report_em, symbol=symbol)
    
    def get_cash_flow(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取现金流量表"""
        return self._safe_request(ak.stock_cash_flow_sheet_by_report_em, symbol=symbol)
    
    # ==================== 技术指标数据 ====================
    
    def get_technical_indicators(self, symbol: str, indicator: str = "MACD") -> Optional[pd.DataFrame]:
        """
        获取技术指标数据
        
        Args:
            symbol: 股票代码
            indicator: 技术指标类型
        """
        # 这里可以根据需要实现各种技术指标的计算
        # 由于akshare没有直接的技术指标接口，可以基于历史数据计算
        history_data = self.get_stock_history_data(symbol)
        if history_data is not None:
            # 这里可以添加技术指标计算逻辑
            return history_data
        return None
    
    # ==================== 数据验证和清洗 ====================
    
    def validate_stock_code(self, symbol: str) -> bool:
        """
        验证股票代码是否有效
        
        Args:
            symbol: 股票代码
        
        Returns:
            bool: 是否有效
        """
        try:
            # 简单的股票代码格式验证
            if len(symbol) != 6 or not symbol.isdigit():
                return False
            
            # 通过获取股票信息来验证代码是否存在
            info = self.get_stock_info(symbol)
            return info is not None and not info.empty
        except Exception:
            return False
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗DataFrame数据
        
        Args:
            df: 原始DataFrame
        
        Returns:
            pd.DataFrame: 清洗后的DataFrame
        """
        if df is None or df.empty:
            return df
        
        # 去除重复行
        df = df.drop_duplicates()
        
        # 处理缺失值
        df = df.dropna(how='all')  # 删除全为空的行
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        return df
    
    # ==================== 批量数据获取 ====================
    
    def get_multiple_stocks_data(self, symbols: List[str], data_type: str = "realtime") -> Dict[str, pd.DataFrame]:
        """
        批量获取多只股票数据
        
        Args:
            symbols: 股票代码列表
            data_type: 数据类型 realtime/history/minute
        
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到数据的映射
        """
        results = {}
        
        for symbol in symbols:
            try:
                if data_type == "realtime":
                    data = self.get_stock_realtime_single(symbol)
                elif data_type == "history":
                    data = self.get_stock_history_data(symbol)
                elif data_type == "minute":
                    data = self.get_stock_minute_data(symbol)
                else:
                    logger.warning(f"Unknown data type: {data_type}")
                    continue
                
                if data is not None:
                    results[symbol] = self.clean_dataframe(data)
                    logger.info(f"Successfully fetched {data_type} data for {symbol}")
                else:
                    logger.warning(f"No data found for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                continue
        
        return results
    
    # ==================== 数据统计和分析 ====================
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        获取市场概况统计
        
        Returns:
            Dict[str, Any]: 市场统计信息
        """
        summary = {}
        
        try:
            # 获取大盘指数数据
            index_data = self.get_market_index_realtime()
            if index_data is not None:
                summary['index_count'] = len(index_data)
                summary['index_data'] = index_data.head(10).to_dict('records')
            
            # 获取股票实时数据统计
            stock_data = self.get_stock_realtime_data()
            if stock_data is not None:
                summary['stock_count'] = len(stock_data)
                summary['up_count'] = len(stock_data[stock_data['涨跌幅'] > 0]) if '涨跌幅' in stock_data.columns else 0
                summary['down_count'] = len(stock_data[stock_data['涨跌幅'] < 0]) if '涨跌幅' in stock_data.columns else 0
                summary['flat_count'] = len(stock_data[stock_data['涨跌幅'] == 0]) if '涨跌幅' in stock_data.columns else 0
            
            # 获取行业板块统计
            industry_data = self.get_industry_realtime_data()
            if industry_data is not None:
                summary['industry_count'] = len(industry_data)
            
            # 获取概念板块统计
            concept_data = self.get_concept_realtime_data()
            if concept_data is not None:
                summary['concept_count'] = len(concept_data)
            
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
        
        return summary


# 创建全局实例
akshare_client = AkshareClient()


# 便捷函数
def get_stock_data(symbol: str, data_type: str = "realtime", **kwargs) -> Optional[pd.DataFrame]:
    """
    便捷的股票数据获取函数
    
    Args:
        symbol: 股票代码
        data_type: 数据类型
        **kwargs: 其他参数
    
    Returns:
        Optional[pd.DataFrame]: 股票数据
    """
    if data_type == "realtime":
        return akshare_client.get_stock_realtime_single(symbol)
    elif data_type == "history":
        return akshare_client.get_stock_history_data(symbol, **kwargs)
    elif data_type == "minute":
        return akshare_client.get_stock_minute_data(symbol, **kwargs)
    elif data_type == "info":
        return akshare_client.get_stock_info(symbol)
    else:
        logger.warning(f"Unknown data type: {data_type}")
        return None


def get_market_data(data_type: str = "realtime", **kwargs) -> Optional[pd.DataFrame]:
    """
    便捷的市场数据获取函数
    
    Args:
        data_type: 数据类型
        **kwargs: 其他参数
    
    Returns:
        Optional[pd.DataFrame]: 市场数据
    """
    if data_type == "realtime":
        return akshare_client.get_market_index_realtime()
    elif data_type == "history":
        return akshare_client.get_market_index_history(**kwargs)
    elif data_type == "money_flow":
        return akshare_client.get_market_money_flow()
    else:
        logger.warning(f"Unknown data type: {data_type}")
        return None