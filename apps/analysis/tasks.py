from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
import pandas as pd
import numpy as np
from .models import StockAnalysisResult, TechnicalIndicator
from apps.stocks.models import StockBasicInfo, StockRealtimeData
from utils.data_processor import DataProcessor
from utils.akshare_client import AkshareClient

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def daily_stock_analysis(self):
    """
    每日股票分析任务
    """
    try:
        logger.info("开始执行每日股票分析")
        
        # 获取活跃股票
        active_stocks = Stock.objects.filter(is_active=True)[:100]  # 限制分析数量
        data_processor = DataProcessor()
        
        analyzed_count = 0
        
        for stock in active_stocks:
            try:
                # 获取股票最近30天的数据
                end_date = timezone.now().date()
                start_date = end_date - timezone.timedelta(days=30)
                
                stock_data = StockData.objects.filter(
                    stock=stock,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date')
                
                if stock_data.count() < 10:  # 数据不足，跳过分析
                    continue
                
                # 转换为DataFrame进行分析
                df = pd.DataFrame(list(stock_data.values(
                    'date', 'open_price', 'close_price', 'high_price', 'low_price', 'volume'
                )))
                
                if df.empty:
                    continue
                
                # 执行技术分析
                analysis_result = perform_technical_analysis(df, stock)
                
                # 保存分析结果
                AnalysisResult.objects.update_or_create(
                    stock=stock,
                    analysis_date=timezone.now().date(),
                    defaults={
                        'analysis_type': 'TECHNICAL',
                        'result_data': analysis_result,
                        'confidence_score': analysis_result.get('confidence', 0.5),
                        'recommendation': analysis_result.get('recommendation', 'HOLD'),
                        'created_at': timezone.now()
                    }
                )
                
                analyzed_count += 1
                
            except Exception as e:
                logger.error(f"分析股票 {stock.code} 失败: {str(e)}")
                continue
        
        logger.info(f"每日股票分析完成，共分析 {analyzed_count} 只股票")
        return f"成功分析 {analyzed_count} 只股票"
        
    except Exception as exc:
        logger.error(f"每日股票分析失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)

def perform_technical_analysis(df, stock):
    """
    执行技术分析
    """
    try:
        # 计算技术指标
        indicators = {}
        
        # 移动平均线
        df['MA5'] = df['close_price'].rolling(window=5).mean()
        df['MA10'] = df['close_price'].rolling(window=10).mean()
        df['MA20'] = df['close_price'].rolling(window=20).mean()
        
        # RSI指标
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD指标
        exp1 = df['close_price'].ewm(span=12).mean()
        exp2 = df['close_price'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # 布林带
        df['BB_middle'] = df['close_price'].rolling(window=20).mean()
        bb_std = df['close_price'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # 获取最新值
        latest = df.iloc[-1]
        
        indicators = {
            'MA5': float(latest['MA5']) if not pd.isna(latest['MA5']) else 0,
            'MA10': float(latest['MA10']) if not pd.isna(latest['MA10']) else 0,
            'MA20': float(latest['MA20']) if not pd.isna(latest['MA20']) else 0,
            'RSI': float(latest['RSI']) if not pd.isna(latest['RSI']) else 50,
            'MACD': float(latest['MACD']) if not pd.isna(latest['MACD']) else 0,
            'MACD_signal': float(latest['MACD_signal']) if not pd.isna(latest['MACD_signal']) else 0,
            'BB_position': 0  # 布林带位置
        }
        
        # 计算布林带位置
        if not pd.isna(latest['BB_upper']) and not pd.isna(latest['BB_lower']):
            bb_range = latest['BB_upper'] - latest['BB_lower']
            if bb_range > 0:
                indicators['BB_position'] = (latest['close_price'] - latest['BB_lower']) / bb_range
        
        # 生成交易信号
        signals = generate_trading_signals(indicators, latest)
        
        # 计算置信度
        confidence = calculate_confidence(indicators, signals)
        
        # 生成推荐
        recommendation = generate_recommendation(signals, confidence)
        
        return {
            'indicators': indicators,
            'signals': signals,
            'confidence': confidence,
            'recommendation': recommendation,
            'analysis_time': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"技术分析执行失败: {str(e)}")
        return {
            'error': str(e),
            'indicators': {},
            'signals': {},
            'confidence': 0,
            'recommendation': 'HOLD'
        }

def generate_trading_signals(indicators, latest_data):
    """
    生成交易信号
    """
    signals = {
        'ma_signal': 'NEUTRAL',
        'rsi_signal': 'NEUTRAL',
        'macd_signal': 'NEUTRAL',
        'bb_signal': 'NEUTRAL'
    }
    
    # 移动平均线信号
    if indicators['MA5'] > indicators['MA10'] > indicators['MA20']:
        signals['ma_signal'] = 'BUY'
    elif indicators['MA5'] < indicators['MA10'] < indicators['MA20']:
        signals['ma_signal'] = 'SELL'
    
    # RSI信号
    rsi = indicators['RSI']
    if rsi < 30:
        signals['rsi_signal'] = 'BUY'  # 超卖
    elif rsi > 70:
        signals['rsi_signal'] = 'SELL'  # 超买
    
    # MACD信号
    if indicators['MACD'] > indicators['MACD_signal']:
        signals['macd_signal'] = 'BUY'
    elif indicators['MACD'] < indicators['MACD_signal']:
        signals['macd_signal'] = 'SELL'
    
    # 布林带信号
    bb_pos = indicators['BB_position']
    if bb_pos < 0.2:
        signals['bb_signal'] = 'BUY'  # 接近下轨
    elif bb_pos > 0.8:
        signals['bb_signal'] = 'SELL'  # 接近上轨
    
    return signals

def calculate_confidence(indicators, signals):
    """
    计算分析置信度
    """
    # 统计买入和卖出信号数量
    buy_signals = sum(1 for signal in signals.values() if signal == 'BUY')
    sell_signals = sum(1 for signal in signals.values() if signal == 'SELL')
    total_signals = len(signals)
    
    # 计算信号一致性
    if buy_signals > sell_signals:
        consistency = buy_signals / total_signals
    elif sell_signals > buy_signals:
        consistency = sell_signals / total_signals
    else:
        consistency = 0.5  # 信号分歧
    
    # 基础置信度
    base_confidence = consistency
    
    # 根据RSI调整置信度
    rsi = indicators['RSI']
    if rsi < 20 or rsi > 80:  # 极端超买超卖
        base_confidence += 0.1
    
    return min(base_confidence, 1.0)

def generate_recommendation(signals, confidence):
    """
    生成投资建议
    """
    buy_signals = sum(1 for signal in signals.values() if signal == 'BUY')
    sell_signals = sum(1 for signal in signals.values() if signal == 'SELL')
    
    if confidence < 0.3:
        return 'HOLD'  # 置信度太低
    
    if buy_signals > sell_signals and confidence > 0.6:
        return 'BUY'
    elif sell_signals > buy_signals and confidence > 0.6:
        return 'SELL'
    else:
        return 'HOLD'

@shared_task(bind=True)
def update_technical_indicators(self):
    """
    更新技术指标
    """
    try:
        logger.info("开始更新技术指标")
        
        # 获取需要更新指标的股票
        stocks_to_update = Stock.objects.filter(is_active=True)[:50]
        
        updated_count = 0
        
        for stock in stocks_to_update:
            try:
                # 获取最近数据
                recent_data = StockData.objects.filter(
                    stock=stock
                ).order_by('-date')[:30]
                
                if recent_data.count() < 10:
                    continue
                
                # 计算并保存技术指标
                df = pd.DataFrame(list(recent_data.values(
                    'date', 'close_price', 'volume'
                )))
                
                # 计算各种技术指标
                latest_indicators = calculate_latest_indicators(df)
                
                # 保存到数据库
                TechnicalIndicator.objects.update_or_create(
                    stock=stock,
                    date=timezone.now().date(),
                    defaults={
                        'indicator_data': latest_indicators,
                        'updated_at': timezone.now()
                    }
                )
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"更新股票 {stock.code} 技术指标失败: {str(e)}")
                continue
        
        logger.info(f"技术指标更新完成，共更新 {updated_count} 只股票")
        return f"成功更新 {updated_count} 只股票的技术指标"
        
    except Exception as exc:
        logger.error(f"更新技术指标失败: {str(exc)}")
        raise exc

def calculate_latest_indicators(df):
    """
    计算最新的技术指标
    """
    try:
        # 确保数据按日期排序
        df = df.sort_values('date')
        
        # 计算各种技术指标
        indicators = {}
        
        # 移动平均线
        for period in [5, 10, 20, 30]:
            if len(df) >= period:
                indicators[f'MA{period}'] = float(df['close_price'].tail(period).mean())
        
        # 价格变化率
        if len(df) >= 2:
            indicators['price_change'] = float(
                (df['close_price'].iloc[-1] - df['close_price'].iloc[-2]) / df['close_price'].iloc[-2] * 100
            )
        
        # 成交量变化
        if len(df) >= 2:
            indicators['volume_change'] = float(
                (df['volume'].iloc[-1] - df['volume'].iloc[-2]) / df['volume'].iloc[-2] * 100
            )
        
        return indicators
        
    except Exception as e:
        logger.error(f"计算技术指标失败: {str(e)}")
        return {}

@shared_task(bind=True)
def generate_analysis_report(self):
    """
    生成分析报告
    """
    try:
        logger.info("开始生成分析报告")
        
        today = timezone.now().date()
        
        # 获取今日分析结果
        analysis_results = AnalysisResult.objects.filter(
            analysis_date=today
        ).select_related('stock')
        
        if not analysis_results.exists():
            return "今日无分析数据，跳过报告生成"
        
        # 统计分析结果
        recommendations = {
            'BUY': 0,
            'SELL': 0,
            'HOLD': 0
        }
        
        high_confidence_stocks = []
        
        for result in analysis_results:
            rec = result.recommendation
            if rec in recommendations:
                recommendations[rec] += 1
            
            if result.confidence_score > 0.7:
                high_confidence_stocks.append({
                    'code': result.stock.code,
                    'name': result.stock.name,
                    'recommendation': result.recommendation,
                    'confidence': result.confidence_score
                })
        
        report = {
            'date': today.strftime('%Y-%m-%d'),
            'total_analyzed': analysis_results.count(),
            'recommendations': recommendations,
            'high_confidence_count': len(high_confidence_stocks),
            'high_confidence_stocks': high_confidence_stocks[:10]  # 只取前10个
        }
        
        logger.info(f"分析报告生成完成: {report}")
        return f"分析报告生成成功，共分析 {report['total_analyzed']} 只股票"
        
    except Exception as exc:
        logger.error(f"生成分析报告失败: {str(exc)}")
        raise exc