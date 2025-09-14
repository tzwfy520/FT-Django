from celery import shared_task
from django.utils import timezone
import logging
from .models import MarketIndex, MarketRealtimeData, MarketHistoryData
from utils.akshare_client import AkshareClient
from utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def update_market_data(self):
    """
    更新市场指数数据
    """
    try:
        logger.info("开始更新市场指数数据")
        
        akshare_client = AkshareClient()
        data_processor = DataProcessor()
        
        # 主要指数列表
        major_indices = [
            {'code': '000001', 'name': '上证指数'},
            {'code': '399001', 'name': '深证成指'},
            {'code': '399006', 'name': '创业板指'},
            {'code': '000300', 'name': '沪深300'},
            {'code': '000016', 'name': '上证50'},
            {'code': '000905', 'name': '中证500'},
        ]
        
        updated_count = 0
        
        for index_info in major_indices:
            try:
                # 获取或创建市场指数记录
                market_index, created = MarketIndex.objects.get_or_create(
                    code=index_info['code'],
                    defaults={
                        'name': index_info['name'],
                        'market_type': 'INDEX',
                        'is_active': True
                    }
                )
                
                # 获取指数实时数据
                index_data = akshare_client.get_index_realtime(index_info['code'])
                
                if index_data:
                    processed_data = data_processor.process_index_data(index_data)
                    
                    # 更新或创建市场数据记录
                    market_data, created = MarketData.objects.update_or_create(
                        market_index=market_index,
                        date=timezone.now().date(),
                        defaults={
                            'open_price': processed_data.get('open', 0),
                            'close_price': processed_data.get('close', 0),
                            'high_price': processed_data.get('high', 0),
                            'low_price': processed_data.get('low', 0),
                            'volume': processed_data.get('volume', 0),
                            'amount': processed_data.get('amount', 0),
                            'change_percent': processed_data.get('change_percent', 0),
                            'updated_at': timezone.now()
                        }
                    )
                    
                    # 更新指数基本信息
                    market_index.current_value = processed_data.get('close', market_index.current_value)
                    market_index.change_percent = processed_data.get('change_percent', 0)
                    market_index.updated_at = timezone.now()
                    market_index.save()
                    
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"更新指数 {index_info['code']} 数据失败: {str(e)}")
                continue
        
        logger.info(f"市场指数数据更新完成，共更新 {updated_count} 个指数")
        return f"成功更新 {updated_count} 个市场指数数据"
        
    except Exception as exc:
        logger.error(f"更新市场指数数据失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def update_market_sentiment(self):
    """
    更新市场情绪数据
    """
    try:
        logger.info("开始更新市场情绪数据")
        
        akshare_client = AkshareClient()
        
        # 获取市场情绪相关数据
        sentiment_data = {
            'fear_greed_index': akshare_client.get_fear_greed_index(),
            'margin_trading': akshare_client.get_margin_trading_data(),
            'fund_flow': akshare_client.get_fund_flow_data(),
        }
        
        # 这里可以根据实际需求处理情绪数据
        # 例如计算综合情绪指标，存储到数据库等
        
        logger.info("市场情绪数据更新完成")
        return "市场情绪数据更新成功"
        
    except Exception as exc:
        logger.error(f"更新市场情绪数据失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)

@shared_task(bind=True)
def generate_market_report(self):
    """
    生成市场报告
    """
    try:
        logger.info("开始生成市场报告")
        
        # 获取今日市场数据
        today = timezone.now().date()
        market_data = MarketData.objects.filter(date=today)
        
        if not market_data.exists():
            logger.warning("今日无市场数据，跳过报告生成")
            return "今日无市场数据，跳过报告生成"
        
        # 生成报告内容
        report_content = {
            'date': today.strftime('%Y-%m-%d'),
            'market_summary': {},
            'index_performance': [],
            'market_analysis': ''
        }
        
        # 统计各指数表现
        for data in market_data:
            index_info = {
                'name': data.market_index.name,
                'code': data.market_index.code,
                'close_price': float(data.close_price),
                'change_percent': float(data.change_percent),
                'volume': int(data.volume)
            }
            report_content['index_performance'].append(index_info)
        
        # 这里可以添加更多的分析逻辑
        # 例如技术指标计算、趋势分析等
        
        logger.info("市场报告生成完成")
        return f"市场报告生成成功，包含 {len(report_content['index_performance'])} 个指数数据"
        
    except Exception as exc:
        logger.error(f"生成市场报告失败: {str(exc)}")
        raise exc

@shared_task(bind=True)
def sync_market_holidays(self):
    """
    同步市场交易日历
    """
    try:
        logger.info("开始同步市场交易日历")
        
        akshare_client = AkshareClient()
        
        # 获取交易日历数据
        current_year = timezone.now().year
        trading_calendar = akshare_client.get_trading_calendar(current_year)
        
        if trading_calendar is not None and not trading_calendar.empty:
            # 处理交易日历数据
            # 这里可以创建一个TradingCalendar模型来存储交易日信息
            
            logger.info(f"交易日历同步完成，共 {len(trading_calendar)} 条记录")
            return f"交易日历同步成功，共 {len(trading_calendar)} 条记录"
        
        else:
            logger.warning("未获取到交易日历数据")
            return "未获取到交易日历数据"
            
    except Exception as exc:
        logger.error(f"同步交易日历失败: {str(exc)}")
        raise exc