from celery import shared_task
from django.utils import timezone
from django.conf import settings
import logging
import akshare as ak
from .models import StockBasicInfo, StockRealtimeData, StockHistoryData
from utils.akshare_client import AkshareClient
from utils.data_processor import DataProcessor
from .services.history_data_service import HistoryDataService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def update_realtime_stock_data(self):
    """
    更新实时股票数据
    """
    try:
        logger.info("开始更新实时股票数据")
        
        # 获取所有活跃股票
        active_stocks = StockBasicInfo.objects.filter(is_active=True)
        
        akshare_client = AkshareClient()
        data_processor = DataProcessor()
        
        updated_count = 0
        
        for stock in active_stocks:
            try:
                # 获取实时数据
                realtime_data = akshare_client.get_realtime_data(stock.stock_code)
                
                if realtime_data:
                    # 处理数据
                    processed_data = data_processor.process_realtime_data(realtime_data)
                    
                    # 更新或创建股票数据记录
                    stock_data, created = StockRealtimeData.objects.update_or_create(
                        stock=stock,
                        date=timezone.now().date(),
                        defaults={
                            'open_price': processed_data.get('open', 0),
                            'close_price': processed_data.get('close', 0),
                            'high_price': processed_data.get('high', 0),
                            'low_price': processed_data.get('low', 0),
                            'volume': processed_data.get('volume', 0),
                            'amount': processed_data.get('amount', 0),
                            'updated_at': timezone.now()
                        }
                    )
                    
                    # 更新股票基本信息
                    stock.current_price = processed_data.get('close', stock.current_price)
                    stock.change_percent = processed_data.get('change_percent', 0)
                    stock.updated_at = timezone.now()
                    stock.save()
                    
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"更新股票 {stock.stock_code} 数据失败: {str(e)}")
                continue
        
        logger.info(f"实时股票数据更新完成，共更新 {updated_count} 只股票")
        return f"成功更新 {updated_count} 只股票的实时数据"
        
    except Exception as exc:
        logger.error(f"更新实时股票数据失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def update_stock_history(self):
    """
    更新股票历史数据
    """
    try:
        logger.info("开始更新股票历史数据")
        
        active_stocks = StockBasicInfo.objects.filter(is_active=True)
        akshare_client = AkshareClient()
        data_processor = DataProcessor()
        
        updated_count = 0
        
        for stock in active_stocks:
            try:
                # 获取最近30天的历史数据
                end_date = timezone.now().date()
                start_date = end_date - timezone.timedelta(days=30)
                
                history_data = akshare_client.get_stock_history(
                    stock.stock_code, 
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )
                
                if history_data is not None and not history_data.empty:
                    # 处理历史数据
                    processed_data = data_processor.process_history_data(history_data)
                    
                    # 批量创建或更新历史数据
                    for date_str, data in processed_data.items():
                        StockHistoryData.objects.update_or_create(
                            stock=stock,
                            date=data['date'],
                            defaults={
                                'open_price': data['open'],
                                'close_price': data['close'],
                                'high_price': data['high'],
                                'low_price': data['low'],
                                'volume': data['volume'],
                                'amount': data.get('amount', 0),
                                'updated_at': timezone.now()
                            }
                        )
                    
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"更新股票 {stock.stock_code} 历史数据失败: {str(e)}")
                continue
        
        logger.info(f"股票历史数据更新完成，共更新 {updated_count} 只股票")
        return f"成功更新 {updated_count} 只股票的历史数据"
        
    except Exception as exc:
        logger.error(f"更新股票历史数据失败: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)

@shared_task(bind=True)
def sync_stock_list(self):
    """
    同步股票列表
    """
    try:
        logger.info("开始同步股票列表")
        
        akshare_client = AkshareClient()
        
        # 获取A股股票列表
        stock_list = akshare_client.get_stock_basic_info()
        
        if stock_list is not None and not stock_list.empty:
            created_count = 0
            updated_count = 0
            
            for _, row in stock_list.iterrows():
                stock, created = StockBasicInfo.objects.update_or_create(
                    stock_code=row['code'],
                    defaults={
                        'stock_name': row['name'],
                        'market': row.get('market', 'A股'),
                        'industry': row.get('industry', ''),
                        'is_active': True,
                        'updated_at': timezone.now()
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            logger.info(f"股票列表同步完成，新增 {created_count} 只，更新 {updated_count} 只")
            return f"同步完成：新增 {created_count} 只股票，更新 {updated_count} 只股票"
        
        else:
            logger.warning("未获取到股票列表数据")
            return "未获取到股票列表数据"
            
    except Exception as exc:
        logger.error(f"同步股票列表失败: {str(exc)}")
        raise exc

@shared_task(bind=True)
def sync_stock_industry_info(self):
    """
    同步股票行业信息
    """
    try:
        logger.info("开始同步股票行业信息")
        
        akshare_client = AkshareClient()
        
        # 获取行业板块信息
        industry_info = akshare_client.get_industry_info()
        
        if industry_info is not None and not industry_info.empty:
            updated_count = 0
            
            # 遍历每个行业
            for _, industry_row in industry_info.iterrows():
                industry_name = industry_row.get('板块名称', '')
                if not industry_name:
                    continue
                    
                try:
                    # 获取该行业的成分股
                    industry_stocks = akshare_client.get_industry_stocks(industry_name)
                    
                    if industry_stocks is not None and not industry_stocks.empty:
                        # 更新股票的行业信息
                        for _, stock_row in industry_stocks.iterrows():
                            stock_code = stock_row.get('代码', '')
                            if stock_code:
                                # 更新股票的行业信息
                                updated = StockBasicInfo.objects.filter(
                                    stock_code=stock_code
                                ).update(
                                    industry=industry_name,
                                    updated_at=timezone.now()
                                )
                                if updated:
                                    updated_count += 1
                                    
                except Exception as e:
                    logger.warning(f"获取行业 {industry_name} 成分股失败: {str(e)}")
                    continue
            
            logger.info(f"股票行业信息同步完成，更新 {updated_count} 只股票")
            return f"同步完成：更新 {updated_count} 只股票的行业信息"
        
        else:
            logger.warning("未获取到行业板块数据")
            return "未获取到行业板块数据"
            
    except Exception as exc:
        logger.error(f"同步股票行业信息失败: {str(exc)}")
        raise exc

@shared_task(bind=True)
def cleanup_old_data(self):
    """
    清理过期数据
    """
    try:
        logger.info("开始清理过期数据")
        
        # 删除90天前的股票数据
        cutoff_date = timezone.now().date() - timezone.timedelta(days=90)
        deleted_count = StockHistoryData.objects.filter(date__lt=cutoff_date).delete()[0]
        
        logger.info(f"清理过期数据完成，删除 {deleted_count} 条记录")
        return f"清理完成，删除 {deleted_count} 条过期数据"
        
    except Exception as exc:
        logger.error(f"清理过期数据失败: {str(exc)}")
        raise exc


@shared_task(bind=True, max_retries=3)
def collect_stock_history_qfq_data(self, symbols=None, periods=None):
    """
    采集股票历史数据-前复权
    
    Args:
        symbols: 股票代码列表，如果为None则采集所有活跃股票
        periods: 数据周期列表，默认为['daily', 'weekly', 'monthly']
    """
    try:
        logger.info("开始执行历史数据-前复权采集任务")
        
        history_service = HistoryDataService()
        
        if symbols is None:
            # 采集所有活跃股票
            results = history_service.collect_all_stocks_history_data(periods)
        else:
            # 采集指定股票
            results = history_service.collect_stock_history_data(symbols, periods)
        
        # 统计结果
        total_stocks = len(results)
        total_records = 0
        success_count = 0
        
        for symbol, periods_result in results.items():
            stock_total = sum(periods_result.values())
            total_records += stock_total
            if stock_total > 0:
                success_count += 1
        
        logger.info(f"历史数据采集完成: 处理股票 {total_stocks} 只，成功 {success_count} 只，共采集 {total_records} 条记录")
        
        return {
            'status': 'success',
            'total_stocks': total_stocks,
            'success_stocks': success_count,
            'total_records': total_records,
            'details': results
        }
        
    except Exception as exc:
        logger.error(f"历史数据采集任务失败: {str(exc)}")
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"任务重试 {self.request.retries + 1}/{self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        else:
            logger.error("任务重试次数已达上限，任务失败")
            raise exc


@shared_task(bind=True)
def collect_specific_stocks_history_data(self, symbols, periods=None):
    """
    采集指定股票的历史数据
    
    Args:
        symbols: 股票代码列表
        periods: 数据周期列表
    """
    # 直接调用任务函数，而不是通过Celery异步调用
    return collect_stock_history_qfq_data(symbols, periods)