#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')
django.setup()

from apps.system.models import DataSource

print('=== 数据源检查 ===')
print(f'DataSource 总数: {DataSource.objects.count()}')
print('\n数据源列表:')

for ds in DataSource.objects.all():
    print(f'  - ID: {ds.id}')
    print(f'    名称: {ds.name}')
    print(f'    类型: {ds.source_type} ({ds.get_source_type_display()})')
    print(f'    地址: {ds.host}:{ds.port}')
    print(f'    数据库: {ds.database_name}')
    print(f'    用户名: {ds.username}')
    print(f'    是否激活: {ds.is_active}')
    print(f'    创建时间: {ds.created_at}')
    print('    ---')

if DataSource.objects.count() == 0:
    print('\n没有找到任何数据源配置！')
    print('\n建议创建一些测试数据源:')
    print('1. MySQL数据源')
    print('2. MinIO对象存储')
    
    # 创建示例数据源
    print('\n正在创建示例数据源...')
    
    # MySQL数据源
    mysql_ds, created = DataSource.objects.get_or_create(
        name='MySQL主数据库',
        defaults={
            'source_type': 'mysql',
            'host': '115.190.80.219',
            'port': 3306,
            'username': 'root',
            'password': 'Eccom@12345',
            'database_name': 'django_stock',
            'connection_params': '{"charset": "utf8mb4", "connect_timeout": 30}',
            'is_active': True
        }
    )
    if created:
        print(f'✓ 创建MySQL数据源: {mysql_ds.name}')
    else:
        print(f'- MySQL数据源已存在: {mysql_ds.name}')
    
    # MinIO数据源
    minio_ds, created = DataSource.objects.get_or_create(
        name='MinIO对象存储',
        defaults={
            'source_type': 'minio',
            'host': '139.196.196.96',
            'port': 29000,
            'username': 'minioadmin',
            'password': 'Eccom@2024',
            'connection_params': '{"secure": false, "region": "us-east-1"}',
            'is_active': True
        }
    )
    if created:
        print(f'✓ 创建MinIO数据源: {minio_ds.name}')
    else:
        print(f'- MinIO数据源已存在: {minio_ds.name}')
    
    print(f'\n创建完成！现在有 {DataSource.objects.count()} 个数据源。')

print('\n=== 检查完成 ===')