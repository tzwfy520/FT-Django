from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json
import logging
import hashlib

from .models import (
    StockBasicInfo, StockRealtimeData, StockHistoryData, StockMinuteData, WatchList,
    StockDailyHistoryData, StockWeeklyHistoryData, StockMonthlyHistoryData
)
from utils.akshare_client import akshare_client
from utils.data_processor import DataProcessor
from utils.database import stock_data_manager

logger = logging.getLogger(__name__)
data_processor = DataProcessor()


class BaseAPIView(View):
    """API视图基类"""
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"API请求处理异常: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'服务器内部错误: {str(e)}',
                'data': None
            }, status=500)
    
    def success_response(self, data=None, message='操作成功'):
        """成功响应"""
        return JsonResponse({
            'success': True,
            'message': message,
            'data': data
        })
    
    def error_response(self, message='操作失败', status=400):
        """错误响应"""
        return JsonResponse({
            'success': False,
            'message': message,
            'data': None
        }, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class IndustryListView(BaseAPIView):
    """行业板块列表API"""
    
    def get(self, request):
        """获取行业板块列表"""
        try:
            # 从akshare获取行业板块信息
            industry_data = akshare_client.get_industry_info()
            
            if industry_data is None or industry_data.empty:
                return self.error_response('暂无行业板块数据')
            
            # 处理数据格式
            industries = []
            for _, row in industry_data.iterrows():
                industries.append({
                    'code': row.get('板块代码', ''),
                    'name': row.get('板块名称', ''),
                    'stock_count': row.get('成份股数量', 0),
                    'latest_price': float(row.get('最新价', 0)),
                    'change_percent': float(row.get('涨跌幅', 0)),
                    'change_amount': float(row.get('涨跌额', 0)),
                    'turnover': float(row.get('成交额', 0)),
                    'market_cap': float(row.get('总市值', 0)),
                    'pe_ratio': float(row.get('市盈率', 0))
                })
            
            return self.success_response({
                'industries': industries,
                'total': len(industries)
            })
            
        except Exception as e:
            logger.error(f"获取行业板块列表失败: {str(e)}")
            return self.error_response('获取行业板块列表失败')


@method_decorator(csrf_exempt, name='dispatch')
class ConceptListView(BaseAPIView):
    """概念板块列表API"""
    
    def get(self, request):
        """获取概念板块列表"""
        try:
            # 从akshare获取概念板块信息
            concept_data = akshare_client.get_concept_info()
            
            if concept_data is None or concept_data.empty:
                return self.error_response('暂无概念板块数据')
            
            # 处理数据格式
            concepts = []
            for _, row in concept_data.iterrows():
                concepts.append({
                    'code': row.get('板块代码', ''),
                    'name': row.get('板块名称', ''),
                    'stock_count': row.get('成份股数量', 0),
                    'latest_price': float(row.get('最新价', 0)),
                    'change_percent': float(row.get('涨跌幅', 0)),
                    'change_amount': float(row.get('涨跌额', 0)),
                    'turnover': float(row.get('成交额', 0)),
                    'market_cap': float(row.get('总市值', 0)),
                    'pe_ratio': float(row.get('市盈率', 0))
                })
            
            return self.success_response({
                'concepts': concepts,
                'total': len(concepts)
            })
            
        except Exception as e:
            logger.error(f"获取概念板块列表失败: {str(e)}")
            return self.error_response('获取概念板块列表失败')


@method_decorator(csrf_exempt, name='dispatch')
class IndustryStocksView(BaseAPIView):
    """行业成分股API"""
    
    def get(self, request):
        """获取行业成分股列表"""
        try:
            industry_name = request.GET.get('industry_name', '').strip()
            if not industry_name:
                return self.error_response('请提供行业名称')
            
            # 从akshare获取行业成分股
            stocks_data = akshare_client.get_industry_stocks(industry_name)
            
            if stocks_data is None or stocks_data.empty:
                return self.error_response('暂无该行业成分股数据')
            
            # 处理数据格式
            stocks = []
            for _, row in stocks_data.iterrows():
                stocks.append({
                    'code': row.get('代码', ''),
                    'name': row.get('名称', ''),
                    'latest_price': float(row.get('最新价', 0)),
                    'change_percent': float(row.get('涨跌幅', 0)),
                    'change_amount': float(row.get('涨跌额', 0)),
                    'volume': int(row.get('成交量', 0)),
                    'turnover': float(row.get('成交额', 0)),
                    'market_cap': float(row.get('总市值', 0)),
                    'pe_ratio': float(row.get('市盈率', 0))
                })
            
            return self.success_response({
                'stocks': stocks,
                'industry_name': industry_name,
                'total': len(stocks)
            })
            
        except Exception as e:
            logger.error(f"获取行业成分股失败: {str(e)}")
            return self.error_response('获取行业成分股失败')


@method_decorator(csrf_exempt, name='dispatch')
class ConceptStocksView(BaseAPIView):
    """概念成分股API"""
    
    def get(self, request):
        """获取概念成分股列表"""
        try:
            concept_name = request.GET.get('concept_name', '').strip()
            if not concept_name:
                return self.error_response('请提供概念名称')
            
            # 从akshare获取概念成分股
            stocks_data = akshare_client.get_concept_stocks(concept_name)
            
            if stocks_data is None or stocks_data.empty:
                return self.error_response('暂无该概念成分股数据')
            
            # 处理数据格式
            stocks = []
            for _, row in stocks_data.iterrows():
                stocks.append({
                    'code': row.get('代码', ''),
                    'name': row.get('名称', ''),
                    'latest_price': float(row.get('最新价', 0)),
                    'change_percent': float(row.get('涨跌幅', 0)),
                    'change_amount': float(row.get('涨跌额', 0)),
                    'volume': int(row.get('成交量', 0)),
                    'turnover': float(row.get('成交额', 0)),
                    'market_cap': float(row.get('总市值', 0)),
                    'pe_ratio': float(row.get('市盈率', 0))
                })
            
            return self.success_response({
                'stocks': stocks,
                'concept_name': concept_name,
                'total': len(stocks)
            })
            
        except Exception as e:
            logger.error(f"获取概念成分股失败: {str(e)}")
            return self.error_response('获取概念成分股失败')
    

@method_decorator(csrf_exempt, name='dispatch')
class StockDailyHistoryView(BaseAPIView):
    """股票每日历史数据API"""
    
    def get(self, request):
        """获取股票每日历史数据"""
        try:
            stock_code = request.GET.get('stock_code', '').strip()
            start_date = request.GET.get('start_date', '').strip()
            end_date = request.GET.get('end_date', '').strip()
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 100))
            
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            # 构建查询条件
            queryset = StockDailyHistoryData.objects.filter(stock_code=stock_code)
            
            if start_date:
                queryset = queryset.filter(trade_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(trade_date__lte=end_date)
            
            # 按日期倒序排列
            queryset = queryset.order_by('-trade_date')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            data = []
            for item in page_obj:
                data.append({
                    'trade_date': item.trade_date.strftime('%Y-%m-%d'),
                    'open': float(item.open_price),
                    'high': float(item.high_price),
                    'low': float(item.low_price),
                    'close': float(item.close_price),
                    'volume': int(item.volume),
                    'amount': float(item.amount),
                    'change_pct': float(item.change_pct) if item.change_pct else 0,
                    'change_amount': float(item.change_amount) if item.change_amount else 0,
                    'turnover_rate': float(item.turnover_rate) if item.turnover_rate else 0
                })
            
            response_data = {
                'data': data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
            return self.success_response(response_data)
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取每日历史数据失败: {str(e)}")
            return self.error_response('获取每日历史数据失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockWeeklyHistoryView(BaseAPIView):
    """股票每周历史数据API"""
    
    def get(self, request):
        """获取股票每周历史数据"""
        try:
            stock_code = request.GET.get('stock_code', '').strip()
            start_date = request.GET.get('start_date', '').strip()
            end_date = request.GET.get('end_date', '').strip()
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 100))
            
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            # 构建查询条件
            queryset = StockWeeklyHistoryData.objects.filter(stock_code=stock_code)
            
            if start_date:
                queryset = queryset.filter(trade_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(trade_date__lte=end_date)
            
            # 按日期倒序排列
            queryset = queryset.order_by('-trade_date')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            data = []
            for item in page_obj:
                data.append({
                    'trade_date': item.trade_date.strftime('%Y-%m-%d'),
                    'open': float(item.open_price),
                    'high': float(item.high_price),
                    'low': float(item.low_price),
                    'close': float(item.close_price),
                    'volume': int(item.volume),
                    'amount': float(item.amount),
                    'change_pct': float(item.change_pct) if item.change_pct else 0,
                    'change_amount': float(item.change_amount) if item.change_amount else 0,
                    'turnover_rate': float(item.turnover_rate) if item.turnover_rate else 0
                })
            
            response_data = {
                'data': data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
            return self.success_response(response_data)
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取每周历史数据失败: {str(e)}")
            return self.error_response('获取每周历史数据失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockMonthlyHistoryView(BaseAPIView):
    """股票每月历史数据API"""
    
    def get(self, request):
        """获取股票每月历史数据"""
        try:
            stock_code = request.GET.get('stock_code', '').strip()
            start_date = request.GET.get('start_date', '').strip()
            end_date = request.GET.get('end_date', '').strip()
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 100))
            
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            # 构建查询条件
            queryset = StockMonthlyHistoryData.objects.filter(stock_code=stock_code)
            
            if start_date:
                queryset = queryset.filter(trade_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(trade_date__lte=end_date)
            
            # 按日期倒序排列
            queryset = queryset.order_by('-trade_date')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            data = []
            for item in page_obj:
                data.append({
                    'trade_date': item.trade_date.strftime('%Y-%m-%d'),
                    'open': float(item.open_price),
                    'high': float(item.high_price),
                    'low': float(item.low_price),
                    'close': float(item.close_price),
                    'volume': int(item.volume),
                    'amount': float(item.amount),
                    'change_pct': float(item.change_pct) if item.change_pct else 0,
                    'change_amount': float(item.change_amount) if item.change_amount else 0,
                    'turnover_rate': float(item.turnover_rate) if item.turnover_rate else 0
                })
            
            response_data = {
                'data': data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
            return self.success_response(response_data)
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取每月历史数据失败: {str(e)}")
            return self.error_response('获取每月历史数据失败')


@method_decorator(csrf_exempt, name='dispatch')
class HistoryDataTaskView(BaseAPIView):
    """历史数据采集任务管理API"""
    
    def get(self, request):
        """获取历史数据采集任务状态"""
        try:
            from apps.tasks.services import history_data_task_service
            from apps.tasks.models import DataUpdateTask
            
            task_type = request.GET.get('task_type', 'stock_history_qfq')
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            # 获取对应类型的任务
            try:
                task = DataUpdateTask.objects.get(data_type=task_type)
                # 获取任务执行记录
                records = history_data_task_service.get_recent_executions(
                    task_id=task.id,
                    limit=page_size
                )
            except DataUpdateTask.DoesNotExist:
                records = []
            
            # 获取总数（简化处理，实际应该从服务中获取）
            total_count = len(records) if len(records) < page_size else page_size * page + 1
            
            response_data = {
                'records': records,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'has_next': len(records) == page_size
                }
            }
            
            return self.success_response(response_data)
            
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            return self.error_response('获取任务状态失败')
    
    def post(self, request):
        """创建历史数据采集任务"""
        try:
            from apps.tasks.services import history_data_task_service
            
            data = json.loads(request.body)
            stock_codes = data.get('stock_codes', [])
            task_type = data.get('task_type', 'stock_history_qfq')
            
            if not stock_codes:
                return self.error_response('请提供股票代码列表')
            
            # 创建任务
            result = history_data_task_service.create_task(
                task_type=task_type,
                stock_codes=stock_codes,
                user_id=1  # 暂时使用固定用户ID
            )
            
            if result.get('success'):
                return self.success_response(
                    data=result.get('data'),
                    message=result.get('message', '任务创建成功，正在后台执行')
                )
            else:
                return self.error_response(result.get('message', '创建任务失败'))
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"创建任务失败: {str(e)}")
            return self.error_response('创建任务失败')
    



@method_decorator(csrf_exempt, name='dispatch')
class WatchListView(BaseAPIView):
    """自选股API - 重新设计，与股票概览数据保持一致"""
    
    def get(self, request):
        """获取用户自选股列表"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search = request.GET.get('search', '').strip()
            
            # 这里暂时使用模拟用户ID，实际应该从认证中获取
            user_id = 1
            
            # 构建查询条件
            queryset = WatchList.objects.filter(user_id=user_id, is_active=True).select_related('stock')
            
            # 搜索过滤
            if search:
                queryset = queryset.filter(
                    Q(stock__stock_code__icontains=search) |
                    Q(stock__stock_name__icontains=search)
                )
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据 - 与股票概览格式保持一致
            watchlist = []
            for item in page_obj:
                stock = item.stock
                watchlist.append({
                    'id': item.id,
                    'code': stock.stock_code,
                    'name': stock.stock_name,
                    'market': stock.market,
                    'industry': stock.industry or '--',
                    'listDate': stock.list_date.strftime('%Y-%m-%d') if stock.list_date else '--',
                    'addPrice': float(item.add_price) if item.add_price else None,
                    'notes': item.notes,
                    'addTime': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'isActive': stock.is_active
                })
            
            return self.success_response({
                'data': watchlist,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取自选股列表失败: {str(e)}")
            return self.error_response('获取自选股列表失败')
    
    def post(self, request):
        """添加股票到自选清单"""
        try:
            data = json.loads(request.body)
            stock_code = data.get('stock_code', '').strip()
            add_price = data.get('add_price')
            notes = data.get('notes', '').strip()
            
            if not stock_code:
                return self.error_response('股票代码不能为空')
            
            # 查找股票
            try:
                stock = StockBasicInfo.objects.get(stock_code=stock_code, is_active=True)
            except StockBasicInfo.DoesNotExist:
                return self.error_response('股票不存在或已停牌')
            
            # 检查是否已添加
            user_id = 1  # 暂时使用固定用户ID
            if WatchList.objects.filter(stock=stock, user_id=user_id, is_active=True).exists():
                return self.error_response('该股票已在自选清单中')
            
            # 创建自选股记录
            watchlist_item = WatchList.objects.create(
                stock=stock,
                user_id=user_id,
                add_price=add_price,
                notes=notes
            )
            
            return self.success_response({
                'message': f'{stock.stock_name} 已添加到自选清单',
                'data': {
                    'id': watchlist_item.id,
                    'code': stock.stock_code,
                    'name': stock.stock_name,
                    'addPrice': float(add_price) if add_price else None,
                    'addTime': watchlist_item.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"添加自选股失败: {str(e)}")
            return self.error_response('添加自选股失败')
    
    def delete(self, request):
        """从自选清单移除股票"""
        try:
            data = json.loads(request.body)
            watchlist_id = data.get('id')
            stock_code = data.get('stock_code')
            
            user_id = 1  # 暂时使用固定用户ID
            
            # 根据ID或股票代码查找记录
            if watchlist_id:
                watchlist_item = WatchList.objects.get(id=watchlist_id, user_id=user_id)
            elif stock_code:
                watchlist_item = WatchList.objects.get(stock__stock_code=stock_code, user_id=user_id)
            else:
                return self.error_response('请提供自选股ID或股票代码')
            
            stock_name = watchlist_item.stock.stock_name
            watchlist_item.delete()
            
            return self.success_response({
                'message': f'{stock_name} 已从自选清单移除'
            })
            
        except WatchList.DoesNotExist:
            return self.error_response('自选股记录不存在')
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"移除自选股失败: {str(e)}")
            return self.error_response('移除自选股失败')
    

    



@method_decorator(csrf_exempt, name='dispatch')
class StockListView(BaseAPIView):
    """股票列表API"""
    
    def get(self, request):
        """获取股票列表"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search = request.GET.get('search', '').strip()
            market = request.GET.get('market', '').strip()
            
            # 构建查询条件
            queryset = StockBasicInfo.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(stock_code__icontains=search) |
                    Q(stock_name__icontains=search)
                )
            
            if market:
                queryset = queryset.filter(market=market)
            
            # 排序
            queryset = queryset.order_by('stock_code')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 获取用户自选股列表（用于标记是否已添加）
            user_id = 1  # 暂时使用固定用户ID
            try:
                user_watchlist = set(WatchList.objects.filter(
                    user_id=user_id, is_active=True
                ).values_list('stock__stock_code', flat=True))
            except Exception as e:
                logger.warning(f'获取自选股列表失败: {str(e)}')
                user_watchlist = set()
            
            # 序列化数据 - 与前端格式保持一致
            stocks = []
            for stock in page_obj:
                stocks.append({
                    'id': stock.id,
                    'code': stock.stock_code,
                    'name': stock.stock_name,
                    'market': stock.market,
                    'industry': stock.industry or '--',
                    'listDate': stock.list_date.strftime('%Y-%m-%d') if stock.list_date else '--',
                    'isActive': stock.is_active,
                    'inWatchlist': stock.stock_code in user_watchlist,  # 是否已在自选清单
                    'createdAt': stock.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # 构建响应数据
            response_data = {
                'stocks': stocks,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                },
                'from_cache': False,
                'cache_time': datetime.now().isoformat()
            }
            
            return self.success_response(response_data)
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取股票列表失败: {str(e)}")
            return self.error_response('获取股票列表失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockRealTimeDataView(BaseAPIView):
    """股票实时数据API"""
    
    def get(self, request):
        """获取股票实时数据"""
        try:
            stock_codes = request.GET.get('codes', '').strip()
            if not stock_codes:
                return self.error_response('请提供股票代码')
            
            codes_list = [code.strip() for code in stock_codes.split(',')]
            
            # 尝试从数据库获取实时数据
            fresh_data = []
            try:
                realtime_data = StockRealtimeData.objects.filter(
                    stock_code__in=codes_list
                ).order_by('-update_time')
                
                # 如果数据库中没有数据或数据过期，从API获取
                current_time = datetime.now()
                
                for data in realtime_data:
                    if (current_time - data.update_time).seconds > 60:  # 数据超过1分钟认为过期
                        # 从API获取新数据
                        try:
                            api_data = akshare_client.get_stock_realtime_data([data.stock_code])
                            if api_data:
                                processed_data = data_processor.process_realtime_data(api_data)
                                # 保存到数据库
                                stock_data_manager.save_realtime_data(processed_data)
                                fresh_data.extend(processed_data)
                        except Exception as e:
                            logger.warning(f"获取股票 {data.stock_code} 实时数据失败: {str(e)}")
                            # 使用数据库中的旧数据
                            fresh_data.append({
                                'stock_code': data.stock_code,
                                'current_price': float(data.current_price),
                                'change_amount': float(data.change_amount),
                                'change_percent': float(data.change_percent),
                                'volume': data.volume,
                                'turnover': float(data.turnover),
                                'high_price': float(data.high_price),
                                'low_price': float(data.low_price),
                                'open_price': float(data.open_price),
                                'pre_close_price': float(data.pre_close_price),
                                'update_time': data.update_time.strftime('%Y-%m-%d %H:%M:%S')
                            })
                    else:
                        fresh_data.append({
                            'stock_code': data.stock_code,
                            'current_price': float(data.current_price),
                            'change_amount': float(data.change_amount),
                            'change_percent': float(data.change_percent),
                            'volume': data.volume,
                            'turnover': float(data.turnover),
                            'high_price': float(data.high_price),
                            'low_price': float(data.low_price),
                            'open_price': float(data.open_price),
                            'pre_close_price': float(data.pre_close_price),
                            'update_time': data.update_time.strftime('%Y-%m-%d %H:%M:%S')
                        })
            except Exception as e:
                logger.warning(f'实时数据表不存在或查询失败: {str(e)}')
                # 返回默认数据
                for code in codes_list:
                    fresh_data.append({
                        'stock_code': code,
                        'current_price': 0.0,
                        'change_amount': 0.0,
                        'change_percent': 0.0,
                        'volume': 0,
                        'turnover': 0.0,
                        'high_price': 0.0,
                        'low_price': 0.0,
                        'open_price': 0.0,
                        'pre_close_price': 0.0,
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return self.success_response(fresh_data)
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {str(e)}")
            return self.error_response('获取实时数据失败')
    
    def post(self, request):
        """刷新股票实时数据"""
        try:
            data = json.loads(request.body)
            stock_codes = data.get('codes', [])
            
            if not stock_codes:
                return self.error_response('请提供股票代码')
            
            # 从API获取实时数据
            api_data = akshare_client.get_stock_realtime_data(stock_codes)
            if not api_data:
                return self.error_response('获取数据失败')
            
            # 处理数据
            processed_data = data_processor.process_realtime_data(api_data)
            
            # 保存到数据库
            stock_data_manager.save_realtime_data(processed_data)
            
            return self.success_response(processed_data, '数据刷新成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"刷新实时数据失败: {str(e)}")
            return self.error_response('刷新数据失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockHistoryDataView(BaseAPIView):
    """股票历史数据API"""
    
    def get(self, request):
        """获取股票历史数据"""
        try:
            stock_code = request.GET.get('code', '').strip()
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            period = request.GET.get('period', 'daily')  # daily, weekly, monthly
            
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            # 设置默认日期范围
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 从数据库获取历史数据
            queryset = StockHistoryData.objects.filter(
                stock_code=stock_code,
                trade_date__gte=start_date,
                trade_date__lte=end_date
            ).order_by('trade_date')
            
            # 如果数据库中没有数据，从API获取
            if not queryset.exists():
                try:
                    api_data = akshare_client.get_stock_history_data(
                        stock_code, start_date, end_date, period
                    )
                    if api_data:
                        processed_data = data_processor.process_history_data(api_data)
                        stock_data_manager.save_history_data(processed_data)
                        # 重新查询
                        queryset = StockHistoryData.objects.filter(
                            stock_code=stock_code,
                            trade_date__gte=start_date,
                            trade_date__lte=end_date
                        ).order_by('trade_date')
                except Exception as e:
                    logger.warning(f"获取股票 {stock_code} 历史数据失败: {str(e)}")
            
            # 序列化数据
            history_data = []
            for data in queryset:
                history_data.append({
                    'trade_date': data.trade_date.strftime('%Y-%m-%d'),
                    'open_price': float(data.open_price),
                    'high_price': float(data.high_price),
                    'low_price': float(data.low_price),
                    'close_price': float(data.close_price),
                    'volume': data.volume,
                    'turnover': float(data.turnover),
                    'change_amount': float(data.change_amount),
                    'change_percent': float(data.change_percent)
                })
            
            return self.success_response({
                'stock_code': stock_code,
                'period': period,
                'start_date': start_date,
                'end_date': end_date,
                'data': history_data
            })
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {str(e)}")
            return self.error_response('获取历史数据失败')


@method_decorator(csrf_exempt, name='dispatch')
class MarketIndexView(BaseAPIView):
    """市场指数API"""
    
    def get(self, request):
        """获取市场指数数据"""
        try:
            # 获取主要指数的最新数据
            indices = ['000001', '399001', '399006']  # 上证指数、深证成指、创业板指
            
            index_data = []
            for index_code in indices:
                try:
                    # MarketIndex模型暂未定义，先返回模拟数据
                    # latest_data = MarketIndex.objects.filter(
                    #     index_code=index_code
                    # ).order_by('-trade_date').first()
                    
                    # 临时返回模拟数据
                    index_names = {'000001': '上证指数', '399001': '深证成指', '399006': '创业板指'}
                    index_data.append({
                        'index_code': index_code,
                        'index_name': index_names.get(index_code, '未知指数'),
                        'current_value': 3000.0,
                        'change_amount': 10.0,
                        'change_percent': 0.33,
                        'volume': 1000000,
                        'turnover': 50000000.0,
                        'trade_date': '2024-01-15',
                        'update_time': '2024-01-15 15:00:00'
                    })
                except Exception as e:
                    logger.warning(f"获取指数 {index_code} 数据失败: {str(e)}")
            
            return self.success_response(index_data)
            
        except Exception as e:
            logger.error(f"获取市场指数失败: {str(e)}")
            return self.error_response('获取市场指数失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockSearchView(BaseAPIView):
    """股票搜索API"""
    
    def get(self, request):
        """搜索股票"""
        try:
            keyword = request.GET.get('q', '').strip()
            limit = int(request.GET.get('limit', 10))
            
            if not keyword:
                return self.error_response('请提供搜索关键词')
            
            # 搜索股票
            stocks = StockBasicInfo.objects.filter(
                Q(stock_code__icontains=keyword) |
                Q(stock_name__icontains=keyword)
            ).filter(is_active=True)[:limit]
            
            results = []
            for stock in stocks:
                results.append({
                    'stock_code': stock.stock_code,
                    'stock_name': stock.stock_name,
                    'market': stock.market,
                    'industry': stock.industry
                })
            
            return self.success_response(results)
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"搜索股票失败: {str(e)}")
            return self.error_response('搜索失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockOverviewView(BaseAPIView):
    """股票概览API"""
    
    def _generate_cache_key(self, page, page_size, search, industry, market):
        """生成缓存键"""
        cache_data = f"stock_overview_{page}_{page_size}_{search}_{industry}_{market}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def get(self, request):
        """获取股票概览数据"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            search = request.GET.get('search', '').strip()
            industry = request.GET.get('industry', '').strip()
            market = request.GET.get('market', '').strip()
            
            # 生成缓存键
            cache_key = self._generate_cache_key(page, page_size, search, industry, market)
            
            # 尝试从缓存获取数据
            cached_data = cache.get(cache_key)
            if cached_data:
                # 添加缓存标识
                cached_data['from_cache'] = True
                cached_data['cache_time'] = datetime.now().isoformat()
                return self.success_response(cached_data)
            
            # 构建查询条件
            queryset = StockBasicInfo.objects.filter(is_active=True)
            
            if search:
                queryset = queryset.filter(
                    Q(stock_code__icontains=search) |
                    Q(stock_name__icontains=search)
                )
            
            if industry:
                queryset = queryset.filter(industry__icontains=industry)
                
            if market:
                queryset = queryset.filter(market=market)
            
            # 排序
            queryset = queryset.order_by('stock_code')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 获取用户自选股列表（用于标记是否已添加）
            user_id = 1  # 暂时使用固定用户ID
            user_watchlist = set(WatchList.objects.filter(
                user_id=user_id, is_active=True
            ).values_list('stock__stock_code', flat=True))
            
            # 序列化数据
            stocks = []
            for stock in page_obj:
                stocks.append({
                    'id': stock.id,
                    'code': stock.stock_code,
                    'name': stock.stock_name,
                    'industry': stock.industry or '未分类',
                    'listDate': stock.list_date.strftime('%Y-%m-%d') if stock.list_date else '未知',
                    'market': stock.get_market_display(),
                    'concept': stock.concept or '',
                    'totalShare': stock.total_share,
                    'marketCap': float(stock.market_cap) if stock.market_cap else None,
                    'inWatchlist': stock.stock_code in user_watchlist,  # 是否已在自选清单
                    # 添加模拟的实时数据字段
                    'currentPrice': 0.0,
                    'changeAmount': 0.0,
                    'changePercent': 0.0,
                    'volume': 0,
                    'turnover': 0.0,
                    'pe': 0.0,
                    'pb': 0.0,
                    'turnoverRate': 0.0,
                    'amplitude': 0.0
                })
            
            return self.success_response({
                'stocks': stocks,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'page_size': page_size,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取股票概览失败: {str(e)}")
            return self.error_response('获取股票概览失败')


@method_decorator(csrf_exempt, name='dispatch')
class StockBasicInfoView(BaseAPIView):
    """股票基本信息API"""
    
    def get(self, request):
        """获取股票基本信息"""
        try:
            stock_code = request.GET.get('stock_code', '').strip()
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            # 从数据库获取股票基本信息
            try:
                stock = StockBasicInfo.objects.get(stock_code=stock_code, is_active=True)
            except StockBasicInfo.DoesNotExist:
                return self.error_response('股票不存在')
            
            # 构建返回数据
            stock_info = {
                'code': stock.stock_code,
                'name': stock.stock_name,
                'market': stock.market,
                'industry': stock.industry,
                'list_date': stock.list_date.strftime('%Y-%m-%d') if stock.list_date else None,
                'is_active': stock.is_active,
                # 使用默认值，因为实时数据表可能不存在
                'price': 0.0,
                'changePercent': 0.0,
                'changeAmount': 0.0,
                'volume': 0,
                'turnover': 0.0,
                'turnoverRate': 0.0,
                'update_time': None
            }
            
            # 尝试获取最新的实时数据（如果表存在）
            try:
                realtime_data = StockRealtimeData.objects.filter(
                    stock__stock_code=stock_code
                ).order_by('-timestamp').first()
                
                # 如果有实时数据，更新实时信息
                if realtime_data:
                    stock_info.update({
                        'price': float(realtime_data.current_price),
                        'changePercent': float(realtime_data.change_pct),
                        'changeAmount': float(realtime_data.change),
                        'volume': int(realtime_data.volume),
                        'turnover': float(realtime_data.amount),
                        'turnoverRate': float(realtime_data.turnover_rate) if realtime_data.turnover_rate else 0.0,
                        'update_time': realtime_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
            except Exception as e:
                # 如果实时数据表不存在或查询失败，使用默认值
                logger.warning(f'获取实时数据失败: {str(e)}')
            
            return self.success_response(stock_info)
            
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {str(e)}")
            return self.error_response('获取股票基本信息失败')


@require_http_methods(["GET"])
def stock_stats(request):
    """股票统计信息"""
    try:
        # 统计信息
        total_stocks = StockBasicInfo.objects.filter(is_active=True).count()
        total_markets = StockBasicInfo.objects.values('market').distinct().count()
        
        # 最近更新时间
        try:
            latest_realtime = StockRealtimeData.objects.order_by('-timestamp').first()
            latest_realtime_update = latest_realtime.update_time.strftime('%Y-%m-%d %H:%M:%S') if latest_realtime else None
        except Exception as e:
            logger.warning(f'获取实时数据更新时间失败: {str(e)}')
            latest_realtime_update = None
            
        try:
            latest_history = StockHistoryData.objects.order_by('-created_at').first()
            latest_history_update = latest_history.created_at.strftime('%Y-%m-%d %H:%M:%S') if latest_history else None
        except Exception as e:
            logger.warning(f'获取历史数据更新时间失败: {str(e)}')
            latest_history_update = None
        
        stats = {
            'total_stocks': total_stocks,
            'total_markets': total_markets,
            'latest_realtime_update': latest_realtime_update,
            'latest_history_update': latest_history_update
        }
        
        return JsonResponse({
            'success': True,
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取统计信息失败',
            'data': None
        }, status=500)