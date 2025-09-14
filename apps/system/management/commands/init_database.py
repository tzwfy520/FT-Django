from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '初始化数据库，创建必要的表和初始数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建数据库表',
        )
        parser.add_argument(
            '--sample-data',
            action='store_true',
            help='创建示例数据',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化数据库...'))
        
        try:
            # 检查数据库连接
            self.check_database_connection()
            
            # 执行数据库迁移
            self.run_migrations(options['force'])
            
            # 创建超级用户
            self.create_superuser()
            
            # 创建示例数据
            if options['sample_data']:
                self.create_sample_data()
            
            # 初始化系统配置
            self.init_system_config()
            
            self.stdout.write(
                self.style.SUCCESS('数据库初始化完成！')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'数据库初始化失败: {str(e)}')
            )
            raise e
    
    def check_database_connection(self):
        """检查数据库连接"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ 数据库连接正常'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 数据库连接失败: {str(e)}')
            )
            raise e
    
    def run_migrations(self, force=False):
        """执行数据库迁移"""
        from django.core.management import call_command
        
        try:
            if force:
                self.stdout.write('正在重置数据库迁移...')
                # 这里可以添加重置迁移的逻辑
            
            self.stdout.write('正在创建迁移文件...')
            call_command('makemigrations', verbosity=0)
            
            self.stdout.write('正在执行数据库迁移...')
            call_command('migrate', verbosity=0)
            
            self.stdout.write(self.style.SUCCESS('✓ 数据库迁移完成'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 数据库迁移失败: {str(e)}')
            )
            raise e
    
    def create_superuser(self):
        """创建超级用户"""
        from django.contrib.auth.models import User
        
        try:
            # 检查是否已存在超级用户
            if User.objects.filter(is_superuser=True).exists():
                self.stdout.write(self.style.WARNING('超级用户已存在，跳过创建'))
                return
            
            # 从环境变量获取超级用户信息
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123456')
            
            # 创建超级用户
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ 超级用户创建成功: {admin_username}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ 创建超级用户失败: {str(e)}')
            )
            # 不抛出异常，允许继续执行
    
    def create_sample_data(self):
        """创建示例数据"""
        try:
            self.stdout.write('正在创建示例数据...')
            
            # 创建示例股票数据
            self.create_sample_stocks()
            
            # 创建示例市场指数
            self.create_sample_indices()
            
            # 创建示例任务
            self.create_sample_tasks()
            
            self.stdout.write(self.style.SUCCESS('✓ 示例数据创建完成'))
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'创建示例数据失败: {str(e)}')
            )
            # 不抛出异常，允许继续执行
    
    def create_sample_stocks(self):
        """创建示例股票数据"""
        from apps.stocks.models import StockBasicInfo
        
        sample_stocks = [
            {'code': '000001', 'name': '平安银行', 'market': 'A股', 'industry': '银行'},
            {'code': '000002', 'name': '万科A', 'market': 'A股', 'industry': '房地产'},
            {'code': '000858', 'name': '五粮液', 'market': 'A股', 'industry': '食品饮料'},
            {'code': '600036', 'name': '招商银行', 'market': 'A股', 'industry': '银行'},
            {'code': '600519', 'name': '贵州茅台', 'market': 'A股', 'industry': '食品饮料'},
        ]
        
        for stock_data in sample_stocks:
            Stock.objects.get_or_create(
                code=stock_data['code'],
                defaults=stock_data
            )
    
    def create_sample_indices(self):
        """创建示例市场指数"""
        from apps.market.models import MarketIndex
        
        sample_indices = [
            {'code': '000001', 'name': '上证指数', 'market_type': 'INDEX'},
            {'code': '399001', 'name': '深证成指', 'market_type': 'INDEX'},
            {'code': '399006', 'name': '创业板指', 'market_type': 'INDEX'},
        ]
        
        for index_data in sample_indices:
            MarketIndex.objects.get_or_create(
                code=index_data['code'],
                defaults=index_data
            )
    
    def create_sample_tasks(self):
        """创建示例任务"""
        from apps.tasks.models import Task
        
        sample_tasks = [
            {
                'name': '更新股票实时数据',
                'task_type': 'DATA_UPDATE',
                'description': '定时更新股票实时价格数据',
                'schedule_type': 'INTERVAL',
                'interval_seconds': 30,
                'is_active': True
            },
            {
                'name': '每日股票分析',
                'task_type': 'ANALYSIS',
                'description': '每日执行股票技术分析',
                'schedule_type': 'CRON',
                'cron_expression': '0 16 * * 1-5',
                'is_active': True
            }
        ]
        
        for task_data in sample_tasks:
            Task.objects.get_or_create(
                name=task_data['name'],
                defaults=task_data
            )
    
    def init_system_config(self):
        """初始化系统配置"""
        from apps.system.models import SystemConfig
        
        try:
            # 创建默认系统配置
            default_configs = [
                {
                    'key': 'system.version',
                    'value': '1.0.0',
                    'description': '系统版本号'
                },
                {
                    'key': 'data.update_interval',
                    'value': '30',
                    'description': '数据更新间隔（秒）'
                },
                {
                    'key': 'analysis.enabled',
                    'value': 'true',
                    'description': '是否启用自动分析'
                },
                {
                    'key': 'market.trading_hours',
                    'value': '09:30-15:00',
                    'description': '交易时间'
                }
            ]
            
            for config in default_configs:
                SystemConfig.objects.get_or_create(
                    key=config['key'],
                    defaults={
                        'value': config['value'],
                        'description': config['description']
                    }
                )
            
            self.stdout.write(self.style.SUCCESS('✓ 系统配置初始化完成'))
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'系统配置初始化失败: {str(e)}')
            )