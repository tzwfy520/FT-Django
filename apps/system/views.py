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
import os
import psutil
import re
from pathlib import Path

from .models import SystemConfig, SystemLog, SystemMonitor, DataSource
from django.conf import settings
from django.db import connection

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
class SystemConfigView(BaseAPIView):
    """系统配置API"""
    
    def get(self, request):
        """获取系统配置"""
        try:
            config_key = request.GET.get('key', '').strip()
            category = request.GET.get('category', '').strip()
            
            if config_key:
                # 获取特定配置
                try:
                    config = SystemConfig.objects.get(key=config_key)
                    return self.success_response({
                        'key': config.key,
                        'value': config.value,
                        'category': config.category,
                        'description': config.description,
                        'is_sensitive': config.is_sensitive,
                        'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except SystemConfig.DoesNotExist:
                    return self.error_response('配置不存在', 404)
            
            else:
                # 获取配置列表
                queryset = SystemConfig.objects.all()
                
                if category:
                    queryset = queryset.filter(category=category)
                
                queryset = queryset.order_by('category', 'key')
                
                configs = []
                for config in queryset:
                    config_data = {
                        'key': config.key,
                        'category': config.category,
                        'description': config.description,
                        'is_sensitive': config.is_sensitive,
                        'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # 敏感配置不返回值
                    if not config.is_sensitive:
                        config_data['value'] = config.value
                    else:
                        config_data['value'] = '***'
                    
                    configs.append(config_data)
                
                # 按类别分组
                grouped_configs = {}
                for config in configs:
                    category = config['category']
                    if category not in grouped_configs:
                        grouped_configs[category] = []
                    grouped_configs[category].append(config)
                
                return self.success_response({
                    'configs': configs,
                    'grouped_configs': grouped_configs
                })
                
        except Exception as e:
            logger.error(f"获取系统配置失败: {str(e)}")
            return self.error_response('获取配置失败')
    
    def post(self, request):
        """创建或更新系统配置"""
        try:
            data = json.loads(request.body)
            
            key = data.get('key', '').strip()
            value = data.get('value')
            category = data.get('category', 'general').strip()
            description = data.get('description', '').strip()
            is_sensitive = data.get('is_sensitive', False)
            
            if not key:
                return self.error_response('请提供配置键名')
            
            if value is None:
                return self.error_response('请提供配置值')
            
            # 创建或更新配置
            config, created = SystemConfig.objects.update_or_create(
                key=key,
                defaults={
                    'value': value,
                    'category': category,
                    'description': description,
                    'is_sensitive': is_sensitive
                }
            )
            
            action = '创建' if created else '更新'
            
            return self.success_response({
                'key': config.key,
                'category': config.category,
                'description': config.description,
                'updated_at': config.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }, f'配置{action}成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"保存系统配置失败: {str(e)}")
            return self.error_response('保存配置失败')
    
    def delete(self, request):
        """删除系统配置"""
        try:
            data = json.loads(request.body)
            key = data.get('key', '').strip()
            
            if not key:
                return self.error_response('请提供配置键名')
            
            try:
                config = SystemConfig.objects.get(key=key)
                config.delete()
                return self.success_response(message=f'配置 "{key}" 删除成功')
            except SystemConfig.DoesNotExist:
                return self.error_response('配置不存在', 404)
                
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"删除系统配置失败: {str(e)}")
            return self.error_response('删除配置失败')


@method_decorator(csrf_exempt, name='dispatch')
class DataSourceView(BaseAPIView):
    """数据源管理API"""
    
    def get(self, request):
        """获取数据源列表"""
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            source_type = request.GET.get('type', '').strip()
            is_active = request.GET.get('is_active', '').strip()
            
            queryset = DataSource.objects.all()
            
            if source_type:
                queryset = queryset.filter(source_type=source_type)
            
            if is_active:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            queryset = queryset.order_by('-created_at')
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            sources = []
            for source in page_obj:
                source_data = {
                    'id': source.id,
                    'name': source.name,
                    'source_type': source.source_type,
                    'description': f'{source.get_source_type_display()} - {source.host}:{source.port}',
                    'is_active': source.is_active,
                    'last_sync_time': source.last_test_time.strftime('%Y-%m-%d %H:%M:%S') if source.last_test_time else None,
                    'created_at': source.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': source.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 构建配置信息，隐藏敏感数据
                config = {
                    'host': source.host,
                    'port': source.port,
                    'username': source.username,
                    'password': '***' if source.password else '',
                    'database_name': source.database_name or ''
                }
                # 添加连接参数并隐藏敏感信息
                connection_params = source.get_connection_params()
                if connection_params:
                    for key, value in connection_params.items():
                        if key.lower() in ['password', 'secret', 'token', 'key']:
                            config[key] = '***'
                        else:
                            config[key] = value
                source_data['config'] = config
                
                sources.append(source_data)
            
            return self.success_response({
                'sources': sources,
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
            logger.error(f"获取数据源列表失败: {str(e)}")
            return self.error_response('获取数据源列表失败')
    
    def post(self, request):
        """创建数据源"""
        try:
            data = json.loads(request.body)
            
            name = data.get('name', '').strip()
            source_type = data.get('source_type', '').strip()
            host = data.get('host', '').strip()
            port = data.get('port')
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            database_name = data.get('database_name', '').strip()
            connection_params = data.get('connection_params', '{}')
            
            if not name:
                return self.error_response('请提供数据源名称')
            
            if not source_type:
                return self.error_response('请提供数据源类型')
                
            if not host:
                return self.error_response('请提供主机地址')
                
            if not port:
                return self.error_response('请提供端口号')
            
            # 检查名称是否已存在
            if DataSource.objects.filter(name=name).exists():
                return self.error_response('数据源名称已存在')
            
            # 如果connection_params是字符串，确保它是有效的JSON
            if isinstance(connection_params, str):
                try:
                    json.loads(connection_params)
                except json.JSONDecodeError:
                    connection_params = '{}'
            else:
                connection_params = json.dumps(connection_params)
            
            source = DataSource.objects.create(
                name=name,
                source_type=source_type,
                host=host,
                port=port,
                username=username,
                password=password,
                database_name=database_name,
                connection_params=connection_params
            )
            
            return self.success_response({
                'id': source.id,
                'name': source.name,
                'source_type': source.source_type,
                'host': source.host,
                'port': source.port,
                'created_at': source.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '数据源创建成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"创建数据源失败: {str(e)}")
            return self.error_response('创建数据源失败')
    
    def put(self, request):
        """更新数据源"""
        try:
            data = json.loads(request.body)
            source_id = data.get('id')
            
            if not source_id:
                return self.error_response('请提供数据源ID')
            
            try:
                source = DataSource.objects.get(id=source_id)
            except DataSource.DoesNotExist:
                return self.error_response('数据源不存在', 404)
            
            # 更新字段
            if 'name' in data:
                name = data['name'].strip()
                if name and name != source.name:
                    if DataSource.objects.filter(name=name).exclude(id=source_id).exists():
                        return self.error_response('数据源名称已存在')
                    source.name = name
            
            if 'description' in data:
                source.description = data['description'].strip()
            
            if 'config' in data:
                source.config = data['config']
            
            if 'is_active' in data:
                source.is_active = data['is_active']
            
            source.save()
            
            return self.success_response({
                'id': source.id,
                'name': source.name,
                'updated_at': source.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }, '数据源更新成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"更新数据源失败: {str(e)}")
            return self.error_response('更新数据源失败')


@method_decorator(csrf_exempt, name='dispatch')
class DataSourcePasswordView(BaseAPIView):
    """数据源密码查看API"""
    
    def get(self, request, source_id):
        """获取数据源真实密码"""
        try:
            try:
                source = DataSource.objects.get(id=source_id)
            except DataSource.DoesNotExist:
                return self.error_response('数据源不存在', 404)
            
            return self.success_response({
                'password': source.password
            })
            
        except Exception as e:
            logger.error(f"获取数据源密码失败: {str(e)}")
            return self.error_response('获取数据源密码失败')


@method_decorator(csrf_exempt, name='dispatch')
class SystemLogView(BaseAPIView):
    """系统日志API"""
    
    def get(self, request):
        """获取系统日志"""
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 50))
            level = request.GET.get('level', '').strip()
            module = request.GET.get('module', '').strip()
            date_from = request.GET.get('date_from', '').strip()
            date_to = request.GET.get('date_to', '').strip()
            search = request.GET.get('search', '').strip()
            
            queryset = SystemLog.objects.all()
            
            if level:
                queryset = queryset.filter(level=level)
            
            if module:
                queryset = queryset.filter(module__icontains=module)
            
            if search:
                queryset = queryset.filter(
                    Q(message__icontains=search) |
                    Q(module__icontains=search)
                )
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                    queryset = queryset.filter(created_at__gte=date_from_obj)
                except ValueError:
                    return self.error_response('开始日期格式错误，请使用YYYY-MM-DD格式')
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                    queryset = queryset.filter(created_at__lt=date_to_obj)
                except ValueError:
                    return self.error_response('结束日期格式错误，请使用YYYY-MM-DD格式')
            
            queryset = queryset.order_by('-created_at')
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            logs = []
            for log in page_obj:
                logs.append({
                    'id': log.id,
                    'level': log.level,
                    'module': log.module,
                    'message': log.message,
                    'extra_data': log.extra_data,
                    'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return self.success_response({
                'logs': logs,
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
            logger.error(f"获取系统日志失败: {str(e)}")
            return self.error_response('获取日志失败')


@require_http_methods(["GET"])
def system_monitor(request):
    """系统监控信息"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_info = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': round(disk.used / disk.total * 100, 2)
        }
        
        # 网络IO
        network = psutil.net_io_counters()
        network_info = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv,
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
        
        # 系统负载（仅Unix系统）
        load_avg = None
        try:
            load_avg = os.getloadavg()
        except (OSError, AttributeError):
            pass
        
        # 进程信息
        process_count = len(psutil.pids())
        
        # 系统启动时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        monitor_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'load_avg': load_avg,
            'process_count': process_count,
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime_seconds': int(uptime.total_seconds())
        }
        
        # 保存监控数据到数据库
        SystemMonitor.objects.create(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk_info['percent'],
            load_avg=load_avg[0] if load_avg else None,
            process_count=process_count
        )
        
        return JsonResponse({
            'success': True,
            'message': '获取监控信息成功',
            'data': monitor_data
        })
        
    except Exception as e:
        logger.error(f"获取系统监控信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取监控信息失败',
            'data': None
        }, status=500)


@require_http_methods(["GET"])
def system_stats(request):
    """系统统计信息"""
    try:
        # 配置统计
        total_configs = SystemConfig.objects.count()
        config_categories = SystemConfig.objects.values('category').distinct().count()
        
        # 数据源统计
        total_sources = DataSource.objects.count()
        active_sources = DataSource.objects.filter(is_active=True).count()
        
        # 日志统计
        total_logs = SystemLog.objects.count()
        today = datetime.now().date()
        today_logs = SystemLog.objects.filter(created_at__date=today).count()
        
        # 按日志级别统计
        log_level_stats = SystemLog.objects.values('level').annotate(
            count=Count('id')
        ).order_by('level')
        
        # 最近7天的日志数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_logs = SystemLog.objects.filter(
            created_at__gte=seven_days_ago
        ).count()
        
        # 监控数据统计
        latest_monitor = SystemMonitor.objects.order_by('-created_at').first()
        
        stats = {
            'configs': {
                'total': total_configs,
                'categories': config_categories
            },
            'data_sources': {
                'total': total_sources,
                'active': active_sources
            },
            'logs': {
                'total': total_logs,
                'today': today_logs,
                'recent': recent_logs,
                'by_level': list(log_level_stats)
            },
            'latest_monitor': {
                'cpu_percent': float(latest_monitor.cpu_percent) if latest_monitor else None,
                'memory_percent': float(latest_monitor.memory_percent) if latest_monitor else None,
                'disk_percent': float(latest_monitor.disk_percent) if latest_monitor else None,
                'timestamp': latest_monitor.created_at.strftime('%Y-%m-%d %H:%M:%S') if latest_monitor else None
            } if latest_monitor else None
        }
        
        return JsonResponse({
            'success': True,
            'message': '获取统计信息成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取系统统计信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取统计信息失败',
            'data': None
        }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SystemTestView(BaseAPIView):
    """系统测试API"""
    
    def post(self, request):
        """测试系统组件"""
        try:
            data = json.loads(request.body)
            test_type = data.get('test_type', '').strip()
            
            if not test_type:
                return self.error_response('请提供测试类型')
            
            if test_type == 'database':
                # 测试数据库连接
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        result = cursor.fetchone()
                    
                    return self.success_response({
                        'test_type': 'database',
                        'status': 'success',
                        'message': '数据库连接正常'
                    })
                except Exception as e:
                    return self.error_response(f'数据库连接失败: {str(e)}')
            
            elif test_type == 'akshare':
                # 测试akshare数据接口
                try:
                    import akshare as ak
                    # 获取一个简单的数据来测试连接
                    data = ak.stock_zh_a_spot_em()
                    if data is not None and len(data) > 0:
                        return self.success_response({
                            'test_type': 'akshare',
                            'status': 'success',
                            'message': 'akshare接口连接正常',
                            'sample_count': len(data)
                        })
                    else:
                        return self.error_response('akshare接口返回数据为空')
                except Exception as e:
                    return self.error_response(f'akshare接口测试失败: {str(e)}')
            
            elif test_type == 'redis':
                # 测试Redis连接（如果配置了Redis）
                try:
                    import redis
                    from django.conf import settings
                    
                    # 这里需要根据实际的Redis配置进行调整
                    redis_client = redis.Redis(host='localhost', port=6379, db=0)
                    redis_client.ping()
                    
                    return self.success_response({
                        'test_type': 'redis',
                        'status': 'success',
                        'message': 'Redis连接正常'
                    })
                except Exception as e:
                    return self.error_response(f'Redis连接失败: {str(e)}')
            
            else:
                return self.error_response('不支持的测试类型')
                
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"系统测试失败: {str(e)}")
            return self.error_response('系统测试失败')


@method_decorator(csrf_exempt, name='dispatch')
class MySQLTablesView(BaseAPIView):
    """MySQL数据库表管理API"""
    
    def _get_module_chinese_name(self, module_name):
        """将模块名转换为中文显示名称"""
        module_mapping = {
            'ai': 'AI智能分析',
            'ai_records': 'AI记录管理',
            'analysis': '数据分析',
            'market': '市场数据',
            'stocks': '股票管理',
            'system': '系统管理',
            'tasks': '任务调度',
            # 系统内部功能
            'auth': '认证/授权',
            'admin': '后台管理',
            'migrations': '数据库迁移',
            'management': '系统维护'
        }
        return module_mapping.get(module_name, module_name)
    
    def _get_table_calling_modules(self, table_name):
        """分析表被哪些模块调用"""
        calling_modules = set()
        
        # 获取项目根目录下的apps目录
        apps_dir = Path(settings.BASE_DIR) / 'apps'
        if not apps_dir.exists():
            return list(calling_modules)
        
        # 构建搜索模式
        patterns = [
            rf'["\']?{table_name}["\']?',  # 直接引用表名
            rf'db_table\s*=\s*["\']?{table_name}["\']?',  # Django模型中的db_table
            rf'from_table\s*=\s*["\']?{table_name}["\']?',  # 可能的查询引用
            rf'table\s*=\s*["\']?{table_name}["\']?',  # 表名引用
        ]
        
        try:
            # 遍历apps目录下的所有Python文件
            for py_file in apps_dir.rglob('*.py'):
                if py_file.name.startswith('__') or 'migrations' in str(py_file):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 检查是否包含表名引用
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            # 获取相对于apps目录的路径，取第一级目录作为模块名
                            relative_path = py_file.relative_to(apps_dir)
                            module_name = relative_path.parts[0] if relative_path.parts else 'unknown'
                            calling_modules.add(module_name)
                            break
                            
                except (UnicodeDecodeError, PermissionError):
                    continue
                    
        except Exception as e:
            logger.warning(f"分析表调用模块时出错: {str(e)}")
            
        return list(calling_modules)
    
    def get(self, request, source_id):
        """获取MySQL数据库表信息"""
        try:
            # 获取数据源配置
            try:
                data_source = DataSource.objects.get(id=source_id, source_type='mysql')
            except DataSource.DoesNotExist:
                return self.error_response('MySQL数据源不存在', 404)
            
            # 获取数据库表信息
            with connection.cursor() as cursor:
                # 获取所有表的基本信息
                cursor.execute("""
                    SELECT 
                        TABLE_NAME as table_name,
                        TABLE_ROWS as table_rows,
                        DATA_LENGTH as data_length,
                        ENGINE as engine,
                        TABLE_COLLATION as collation,
                        TABLE_COMMENT as comment,
                        CREATE_TIME as create_time,
                        UPDATE_TIME as update_time
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s
                    ORDER BY TABLE_NAME
                """, [data_source.database_name])
                
                # 先收集所有表信息
                all_tables = []
                for row in cursor.fetchall():
                    table_name = row[0]
                    calling_modules = self._get_table_calling_modules(table_name)
                    # 将英文模块名转换为中文显示名称
                    chinese_modules = [self._get_module_chinese_name(module) for module in calling_modules]
                    
                    table_info = {
                        'name': table_name,
                        'rows': row[1] or 0,
                        'size': row[2] or 0,
                        'engine': row[3] or 'Unknown',
                        'collation': row[4] or 'Unknown',
                        'comment': row[5] or '',
                        'callingModules': chinese_modules,
                        'create_time': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                        'update_time': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None
                    }
                    all_tables.append(table_info)
                
                # 按调用模块分组
                grouped_tables = {}
                for table in all_tables:
                    modules = table['callingModules']
                    if not modules:  # 如果没有调用模块，归类到"未分类"
                        group_key = '未分类'
                    else:
                        # 如果有多个模块，使用第一个作为主要分组
                        group_key = modules[0]
                    
                    if group_key not in grouped_tables:
                        grouped_tables[group_key] = []
                    grouped_tables[group_key].append(table)
                
                # 对每组内的表按行数排序（降序）
                for group_key in grouped_tables:
                    grouped_tables[group_key].sort(key=lambda x: x['rows'], reverse=True)
                
                # 构建返回数据
                table_groups = []
                for group_name, tables in grouped_tables.items():
                    table_groups.append({
                        'groupName': group_name,
                        'tables': tables,
                        'count': len(tables)
                    })
                
                # 按组名排序，"未分类"放在最后
                table_groups.sort(key=lambda x: (x['groupName'] == '未分类', x['groupName']))
            
            return self.success_response({
                'tableGroups': table_groups,
                'total': len(all_tables),
                'database_name': data_source.database_name
            })
            
        except Exception as e:
            logger.error(f"获取MySQL表信息失败: {str(e)}")
            return self.error_response('获取MySQL表信息失败')
    
    def delete(self, request, source_id):
        """删除MySQL数据库表"""
        try:
            data = json.loads(request.body)
            table_name = data.get('table_name', '').strip()
            
            if not table_name:
                return self.error_response('请提供要删除的表名')
            
            # 获取数据源配置
            try:
                data_source = DataSource.objects.get(id=source_id, source_type='mysql')
            except DataSource.DoesNotExist:
                return self.error_response('MySQL数据源不存在', 404)
            
            # 验证表名是否存在
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, [data_source.database_name, table_name])
                
                if cursor.fetchone()[0] == 0:
                    return self.error_response('指定的表不存在')
                
                # 删除表
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            
            logger.info(f"成功删除表: {table_name}")
            return self.success_response(message=f'表 {table_name} 删除成功')
            
        except json.JSONDecodeError:
            return self.error_response('请求数据格式错误')
        except Exception as e:
            logger.error(f"删除MySQL表失败: {str(e)}")
            return self.error_response('删除表失败')


@method_decorator(csrf_exempt, name='dispatch')
class MySQLTableStructureView(BaseAPIView):
    """MySQL表结构查看API"""
    
    def get(self, request, source_id, table_name):
        """获取指定表的结构信息"""
        try:
            # 获取数据源配置
            try:
                data_source = DataSource.objects.get(id=source_id)
            except DataSource.DoesNotExist:
                return self.error_response('数据源不存在')
            
            import pymysql
            
            # 建立数据库连接
            connection = pymysql.connect(
                host=data_source.host,
                port=data_source.port,
                user=data_source.username,
                password=data_source.password,
                database=data_source.database_name,
                charset='utf8mb4',
                connect_timeout=30
            )
            
            cursor = connection.cursor()
            
            # 1. 获取DDL信息 - 表创建语句
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_table_result = cursor.fetchone()
            ddl_info = {
                'create_statement': create_table_result[1] if create_table_result else None
            }
            
            # 2. 获取表结构信息 - 字段详情
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = []
            for row in cursor.fetchall():
                columns_info.append({
                    'field': row[0],      # 字段名
                    'type': row[1],       # 数据类型
                    'null': row[2],       # 是否允许NULL
                    'key': row[3],        # 键类型(PRI, UNI, MUL等)
                    'default': row[4],    # 默认值
                    'extra': row[5]       # 额外信息(auto_increment等)
                })
            
            # 3. 获取索引信息
            cursor.execute(f"SHOW INDEX FROM `{table_name}`")
            indexes_info = []
            for row in cursor.fetchall():
                indexes_info.append({
                    'table': row[0],           # 表名
                    'non_unique': row[1],      # 是否唯一索引(0=唯一, 1=非唯一)
                    'key_name': row[2],        # 索引名
                    'seq_in_index': row[3],    # 列在索引中的序号
                    'column_name': row[4],     # 列名
                    'collation': row[5],       # 排序方式(A=升序, D=降序)
                    'cardinality': row[6],     # 基数(索引中唯一值的数量)
                    'sub_part': row[7],        # 前缀长度
                    'packed': row[8],          # 关键字如何被压缩
                    'null': row[9],            # 是否包含NULL
                    'index_type': row[10],     # 索引类型(BTREE, HASH等)
                    'comment': row[11]         # 注释
                })
            
            # 4. 获取表统计信息
            cursor.execute(f"""
                SELECT 
                    TABLE_ROWS,
                    DATA_LENGTH,
                    INDEX_LENGTH,
                    AUTO_INCREMENT,
                    TABLE_COMMENT,
                    ENGINE,
                    TABLE_COLLATION,
                    CREATE_TIME,
                    UPDATE_TIME
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (data_source.database_name, table_name))
            
            table_stats = cursor.fetchone()
            stats_info = {
                'rows': table_stats[0] if table_stats else 0,
                'data_length': table_stats[1] if table_stats else 0,
                'index_length': table_stats[2] if table_stats else 0,
                'auto_increment': table_stats[3] if table_stats else None,
                'comment': table_stats[4] if table_stats else '',
                'engine': table_stats[5] if table_stats else '',
                'collation': table_stats[6] if table_stats else '',
                'create_time': table_stats[7].isoformat() if table_stats and table_stats[7] else None,
                'update_time': table_stats[8].isoformat() if table_stats and table_stats[8] else None
            }
            
            cursor.close()
            connection.close()
            
            return self.success_response({
                'table_name': table_name,
                'ddl_info': ddl_info,
                'columns_info': columns_info,
                'indexes_info': indexes_info,
                'stats_info': stats_info
            })
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return self.error_response(f'获取表结构失败: {str(e)}')