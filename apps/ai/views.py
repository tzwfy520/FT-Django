from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json
import logging

from .models import AIModel, AIAnalysisTemplate, AIAnalysisRecord, AIConversation, AIMessage, AIUsageStatistics
from apps.stocks.models import StockBasicInfo, StockRealtimeData, StockHistoryData

logger = logging.getLogger(__name__)


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
class AIModelListView(BaseAPIView):
    """AI模型列表API"""
    
    def get(self, request):
        """获取AI模型列表"""
        try:
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            model_type = request.GET.get('type', '').strip()
            is_active = request.GET.get('is_active', '').strip()
            
            # 构建查询条件
            queryset = AIModel.objects.all()
            
            if model_type:
                queryset = queryset.filter(model_type=model_type)
            
            if is_active:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            # 排序
            queryset = queryset.order_by('-created_at')
            
            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # 序列化数据
            models = []
            for model in page_obj:
                models.append({
                    'id': model.id,
                    'name': model.name,
                    'model_type': model.model_type,
                    'version': model.version,
                    'description': model.description,
                    'config': model.config,
                    'is_active': model.is_active,
                    'created_at': model.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': model.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return self.success_response({
                'models': models,
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
            logger.error(f"获取AI模型列表失败: {str(e)}")
            return self.error_response('获取模型列表失败')


@method_decorator(csrf_exempt, name='dispatch')
class AIAnalysisView(BaseAPIView):
    """AI分析API"""
    
    def post(self, request):
        """创建AI分析任务"""
        try:
            data = json.loads(request.body)
            
            stock_code = data.get('stock_code', '').strip()
            analysis_type = data.get('analysis_type', '').strip()
            template_id = data.get('template_id')
            parameters = data.get('parameters', {})
            
            if not stock_code:
                return self.error_response('请提供股票代码')
            
            if not analysis_type:
                return self.error_response('请提供分析类型')
            
            # 验证股票是否存在
            try:
                stock = StockInfo.objects.get(stock_code=stock_code, is_active=True)
            except StockInfo.DoesNotExist:
                return self.error_response('股票不存在或已停用')
            
            # 获取分析模板
            template = None
            if template_id:
                try:
                    template = AIAnalysisTemplate.objects.get(id=template_id, is_active=True)
                except AIAnalysisTemplate.DoesNotExist:
                    return self.error_response('分析模板不存在')
            
            # 创建分析记录
            analysis_record = AIAnalysisRecord.objects.create(
                stock_code=stock_code,
                analysis_type=analysis_type,
                template=template,
                parameters=parameters,
                status='pending'
            )
            
            # 这里应该触发异步分析任务
            # 暂时返回创建成功的响应
            
            return self.success_response({
                'analysis_id': analysis_record.id,
                'stock_code': stock_code,
                'analysis_type': analysis_type,
                'status': 'pending',
                'created_at': analysis_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '分析任务创建成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"创建AI分析任务失败: {str(e)}")
            return self.error_response('创建分析任务失败')
    
    def get(self, request):
        """获取分析结果"""
        try:
            analysis_id = request.GET.get('id')
            stock_code = request.GET.get('stock_code', '').strip()
            
            if analysis_id:
                # 获取特定分析结果
                try:
                    analysis = AIAnalysisRecord.objects.get(id=analysis_id)
                    return self.success_response({
                        'id': analysis.id,
                        'stock_code': analysis.stock_code,
                        'analysis_type': analysis.analysis_type,
                        'status': analysis.status,
                        'result': analysis.result,
                        'confidence_score': float(analysis.confidence_score) if analysis.confidence_score else None,
                        'parameters': analysis.parameters,
                        'error_message': analysis.error_message,
                        'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'completed_at': analysis.completed_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.completed_at else None
                    })
                except AIAnalysisRecord.DoesNotExist:
                    return self.error_response('分析记录不存在', 404)
            
            elif stock_code:
                # 获取股票的分析历史
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                
                queryset = AIAnalysisRecord.objects.filter(
                    stock_code=stock_code
                ).order_by('-created_at')
                
                paginator = Paginator(queryset, page_size)
                page_obj = paginator.get_page(page)
                
                analyses = []
                for analysis in page_obj:
                    analyses.append({
                        'id': analysis.id,
                        'analysis_type': analysis.analysis_type,
                        'status': analysis.status,
                        'confidence_score': float(analysis.confidence_score) if analysis.confidence_score else None,
                        'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'completed_at': analysis.completed_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.completed_at else None
                    })
                
                return self.success_response({
                    'stock_code': stock_code,
                    'analyses': analyses,
                    'pagination': {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'page_size': page_size
                    }
                })
            
            else:
                return self.error_response('请提供分析ID或股票代码')
                
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取分析结果失败: {str(e)}")
            return self.error_response('获取分析结果失败')


@method_decorator(csrf_exempt, name='dispatch')
class AIConversationView(BaseAPIView):
    """AI对话API"""
    
    def post(self, request):
        """创建对话或发送消息"""
        try:
            data = json.loads(request.body)
            
            conversation_id = data.get('conversation_id')
            message = data.get('message', '').strip()
            context = data.get('context', {})
            
            if not message:
                return self.error_response('请提供消息内容')
            
            # 获取或创建对话
            if conversation_id:
                try:
                    conversation = AIConversation.objects.get(id=conversation_id)
                except AIConversation.DoesNotExist:
                    return self.error_response('对话不存在', 404)
            else:
                # 创建新对话
                conversation = AIConversation.objects.create(
                    title=message[:50] + '...' if len(message) > 50 else message,
                    context=context
                )
            
            # 创建用户消息
            user_message = AIMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message
            )
            
            # 这里应该调用AI模型生成回复
            # 暂时返回模拟回复
            ai_response = self._generate_ai_response(message, context)
            
            # 创建AI回复消息
            ai_message = AIMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_response
            )
            
            # 更新对话的最后活动时间
            conversation.updated_at = datetime.now()
            conversation.save()
            
            return self.success_response({
                'conversation_id': conversation.id,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'created_at': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                'ai_message': {
                    'id': ai_message.id,
                    'content': ai_message.content,
                    'created_at': ai_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"处理对话失败: {str(e)}")
            return self.error_response('处理对话失败')
    
    def get(self, request):
        """获取对话历史"""
        try:
            conversation_id = request.GET.get('id')
            
            if not conversation_id:
                # 获取对话列表
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 20))
                
                queryset = AIConversation.objects.all().order_by('-updated_at')
                paginator = Paginator(queryset, page_size)
                page_obj = paginator.get_page(page)
                
                conversations = []
                for conv in page_obj:
                    # 获取最后一条消息
                    last_message = conv.messages.order_by('-created_at').first()
                    
                    conversations.append({
                        'id': conv.id,
                        'title': conv.title,
                        'last_message': last_message.content[:100] + '...' if last_message and len(last_message.content) > 100 else (last_message.content if last_message else ''),
                        'message_count': conv.messages.count(),
                        'created_at': conv.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                return self.success_response({
                    'conversations': conversations,
                    'pagination': {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'page_size': page_size
                    }
                })
            
            else:
                # 获取特定对话的消息
                try:
                    conversation = AIConversation.objects.get(id=conversation_id)
                except AIConversation.DoesNotExist:
                    return self.error_response('对话不存在', 404)
                
                messages = conversation.messages.order_by('created_at')
                
                message_list = []
                for msg in messages:
                    message_list.append({
                        'id': msg.id,
                        'role': msg.role,
                        'content': msg.content,
                        'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                return self.success_response({
                    'conversation': {
                        'id': conversation.id,
                        'title': conversation.title,
                        'context': conversation.context,
                        'created_at': conversation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    'messages': message_list
                })
                
        except ValueError as e:
            return self.error_response(f'参数错误: {str(e)}')
        except Exception as e:
            logger.error(f"获取对话历史失败: {str(e)}")
            return self.error_response('获取对话历史失败')
    
    def _generate_ai_response(self, message, context):
        """生成AI回复（模拟）"""
        # 这里应该调用实际的AI模型
        # 暂时返回模拟回复
        
        if '股票' in message or '分析' in message:
            return "我可以帮您分析股票数据。请提供具体的股票代码，我将为您提供详细的技术分析和投资建议。"
        elif '价格' in message or '涨跌' in message:
            return "股票价格受多种因素影响，包括市场情绪、公司基本面、宏观经济等。建议您关注相关指标进行综合判断。"
        else:
            return "感谢您的提问。我是股票分析AI助手，可以帮您分析股票数据、提供投资建议。请告诉我您想了解什么？"


@method_decorator(csrf_exempt, name='dispatch')
class AITemplateView(BaseAPIView):
    """AI分析模板API"""
    
    def get(self, request):
        """获取分析模板列表"""
        try:
            analysis_type = request.GET.get('type', '').strip()
            
            queryset = AIAnalysisTemplate.objects.filter(is_active=True)
            
            if analysis_type:
                queryset = queryset.filter(analysis_type=analysis_type)
            
            queryset = queryset.order_by('name')
            
            templates = []
            for template in queryset:
                templates.append({
                    'id': template.id,
                    'name': template.name,
                    'analysis_type': template.analysis_type,
                    'description': template.description,
                    'parameters': template.parameters,
                    'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return self.success_response(templates)
            
        except Exception as e:
            logger.error(f"获取分析模板失败: {str(e)}")
            return self.error_response('获取模板列表失败')


@require_http_methods(["GET"])
def ai_stats(request):
    """AI使用统计"""
    try:
        # 统计信息
        total_analyses = AIAnalysisRecord.objects.count()
        completed_analyses = AIAnalysisRecord.objects.filter(status='completed').count()
        total_conversations = AIConversation.objects.count()
        total_messages = AIMessage.objects.count()
        
        # 最近7天的分析数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_analyses = AIAnalysisRecord.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        # 按分析类型统计
        analysis_by_type = AIAnalysisRecord.objects.values('analysis_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        stats = {
            'total_analyses': total_analyses,
            'completed_analyses': completed_analyses,
            'success_rate': round(completed_analyses / total_analyses * 100, 2) if total_analyses > 0 else 0,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'recent_analyses': recent_analyses,
            'analysis_by_type': list(analysis_by_type)
        }
        
        return JsonResponse({
            'success': True,
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取AI统计信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取统计信息失败',
            'data': None
        }, status=500)