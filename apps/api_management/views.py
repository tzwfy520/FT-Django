import time
import json
from django.shortcuts import get_object_or_404
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI
from .models import ApiProvider, ApiToken, ApiInterface, ApiCallLog
from .serializers import (
    ApiProviderSerializer, ApiTokenSerializer, ApiTokenListSerializer,
    ApiInterfaceSerializer, ApiCallLogSerializer, ApiCallRequest, ApiCallResponse
)


class ApiProviderViewSet(viewsets.ModelViewSet):
    """API提供商视图集"""
    queryset = ApiProvider.objects.all()
    serializer_class = ApiProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset


class ApiTokenViewSet(viewsets.ModelViewSet):
    """API Token视图集"""
    serializer_class = ApiTokenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApiToken.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ApiTokenListSerializer
        return ApiTokenSerializer
    
    @action(detail=False, methods=['post'])
    def set_token(self, request):
        """设置或更新API Token"""
        provider_id = request.data.get('provider')
        token = request.data.get('token')
        
        if not provider_id or not token:
            return Response(
                {'error': '提供商ID和Token不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provider = ApiProvider.objects.get(id=provider_id)
        except ApiProvider.DoesNotExist:
            return Response(
                {'error': '提供商不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 更新或创建Token
        api_token, created = ApiToken.objects.update_or_create(
            provider=provider,
            user=request.user,
            defaults={'token': token, 'is_active': True}
        )
        
        serializer = ApiTokenListSerializer(api_token)
        return Response({
            'message': '设置成功' if created else '更新成功',
            'data': serializer.data
        })


class ApiInterfaceViewSet(viewsets.ModelViewSet):
    """API接口配置视图集"""
    serializer_class = ApiInterfaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ApiInterface.objects.filter(user=self.request.user)
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['post'])
    def test_interface(self, request, pk=None):
        """测试接口配置"""
        interface = self.get_object()
        message = request.data.get('message', '你好')
        
        try:
            # 获取API Token
            api_token = ApiToken.objects.get(
                provider=interface.provider,
                user=request.user,
                is_active=True
            )
        except ApiToken.DoesNotExist:
            return Response(
                {'error': f'未找到{interface.provider.display_name}的有效Token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 调用API
        result = self._call_api(interface, api_token.token, message, request.user)
        return Response(result)
    
    def _call_api(self, interface, token, message, user):
        """调用API接口"""
        start_time = time.time()
        
        try:
            # 创建OpenAI客户端
            client = OpenAI(
                base_url=interface.provider.base_url,
                api_key=token,
                timeout=600.0  # 10分钟超时
            )
            
            # 准备请求参数
            request_params = {
                'model': interface.model,
                'messages': [{'role': 'user', 'content': message}]
            }
            
            # 添加可选参数
            if interface.temperature != 0.8:  # 默认值
                request_params['temperature'] = interface.temperature
            if interface.max_tokens != 1024:  # 默认值
                # 对于某些新模型（如gpt-5-nano），使用max_completion_tokens而不是max_tokens
                if 'gpt-5' in interface.model.lower() or 'nano' in interface.model.lower():
                    request_params['max_completion_tokens'] = interface.max_tokens
                else:
                    request_params['max_tokens'] = interface.max_tokens
            
            # 发送请求
            completion = client.chat.completions.create(**request_params)
            
            response_time = time.time() - start_time
            
            # 解析响应
            response_data = {
                'choices': [{
                    'message': {
                        'role': completion.choices[0].message.role,
                        'content': completion.choices[0].message.content
                    },
                    'finish_reason': completion.choices[0].finish_reason
                }],
                'usage': {
                    'prompt_tokens': completion.usage.prompt_tokens,
                    'completion_tokens': completion.usage.completion_tokens,
                    'total_tokens': completion.usage.total_tokens
                }
            }
            
            # 记录调用日志
            ApiCallLog.objects.create(
                interface=interface,
                user=user,
                request_data=request_params,
                response_data=response_data,
                status_code=200,
                response_time=response_time,
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens
            )
            
            return {
                'success': True,
                'data': response_data,
                'response_time': response_time
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = str(e)
            
            # 记录错误日志
            ApiCallLog.objects.create(
                interface=interface,
                user=user,
                request_data={'model': interface.model, 'messages': [{'role': 'user', 'content': message}]},
                response_data=None,
                status_code=500,
                response_time=response_time,
                error_message=error_message
            )
            
            return {
                'success': False,
                'error': error_message,
                'response_time': response_time
            }


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(View):
    """获取CSRF token的视图"""
    
    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})


class ApiCallLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API调用日志视图集"""
    serializer_class = ApiCallLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ApiCallLog.objects.filter(user=self.request.user)
        
        # 按接口过滤
        interface_id = self.request.query_params.get('interface')
        if interface_id:
            queryset = queryset.filter(interface_id=interface_id)
        
        # 按状态过滤
        success_only = self.request.query_params.get('success_only')
        if success_only == 'true':
            queryset = queryset.filter(status_code=200)
        elif success_only == 'false':
            queryset = queryset.exclude(status_code=200)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取调用统计信息"""
        queryset = self.get_queryset()
        
        total_calls = queryset.count()
        success_calls = queryset.filter(status_code=200).count()
        total_tokens = sum(log.total_tokens for log in queryset)
        avg_response_time = queryset.aggregate(
            avg_time=models.Avg('response_time')
        )['avg_time'] or 0
        
        return Response({
            'total_calls': total_calls,
            'success_calls': success_calls,
            'success_rate': (success_calls / total_calls * 100) if total_calls > 0 else 0,
            'total_tokens': total_tokens,
            'avg_response_time': round(avg_response_time, 3)
        })


class ApiCallViewSet(viewsets.ViewSet):
    """API调用视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def call(self, request):
        """调用API接口"""
        serializer = ApiCallRequest(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        interface_id = serializer.validated_data['interface_id']
        message = serializer.validated_data['message']
        
        try:
            interface = ApiInterface.objects.get(
                id=interface_id,
                user=request.user,
                is_active=True
            )
        except ApiInterface.DoesNotExist:
            return Response(
                {'error': '接口不存在或无权限访问'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # 获取API Token
            api_token = ApiToken.objects.get(
                provider=interface.provider,
                user=request.user,
                is_active=True
            )
        except ApiToken.DoesNotExist:
            return Response(
                {'error': f'未找到{interface.provider.display_name}的有效Token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 调用API
        from .views import ApiInterfaceViewSet
        view_instance = ApiInterfaceViewSet()
        result = view_instance._call_api(interface, api_token.token, message, request.user)
        
        response_serializer = ApiCallResponse(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.data)
        
        return Response(result)