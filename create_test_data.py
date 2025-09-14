#!/usr/bin/env python3
"""
创建测试数据脚本
用于创建API提供商、Token和接口配置
"""

import os
import sys

# 添加Django项目路径
sys.path.append('/Users/wangfuyu/PythonCode/FT-Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.api_management.models import ApiProvider, ApiToken, ApiInterface

def create_test_data():
    """创建测试数据"""
    print("🚀 开始创建测试数据...\n")
    
    # 创建或获取超级用户
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ 创建超级用户: {user.username}")
    else:
        print(f"✅ 找到现有用户: {user.username}")
    
    # 创建或获取API提供商
    provider, created = ApiProvider.objects.get_or_create(
        name='aihubmix',
        defaults={
            'display_name': '推理时代 AiHubMix',
            'base_url': 'https://aihubmix.com/v1',
            'is_active': True
        }
    )
    if created:
        print(f"✅ 创建API提供商: {provider.display_name}")
    else:
        print(f"✅ 找到现有提供商: {provider.display_name}")
    
    # 创建或获取API Token（需要用户提供真实的Token）
    print("\n⚠️  需要配置真实的API Token")
    print("请访问 https://aihubmix.com 获取您的API Token")
    
    # 检查是否已有Token
    existing_token = ApiToken.objects.filter(provider=provider, user=user).first()
    if existing_token:
        print(f"✅ 找到现有Token: {existing_token.token[:10]}...")
        token = existing_token
    else:
        # 创建一个占位符Token（需要用户手动更新）
        token = ApiToken.objects.create(
            provider=provider,
            user=user,
            token='your-api-token-here',  # 占位符
            is_active=False  # 默认不激活
        )
        print(f"⚠️  创建占位符Token，请手动更新为真实Token")
    
    # 创建测试接口配置
    interfaces_to_create = [
        {
            'name': 'Gemini 2.5 Flash Preview 测试',
            'model': 'gemini-2.5-flash-preview-04-17',
            'temperature': 0.7,
            'max_tokens': 1024,
            'purposes': ['stock_review', 'real_time_monitoring']
        },
        {
            'name': 'Gemini Pro 对比测试',
            'model': 'gemini-pro',
            'temperature': 0.7,
            'max_tokens': 1024,
            'purposes': ['stock_recommendation']
        },
        {
            'name': 'GPT-4 对比测试',
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1024,
            'purposes': ['stock_review']
        }
    ]
    
    for interface_data in interfaces_to_create:
        interface, created = ApiInterface.objects.get_or_create(
            provider=provider,
            name=interface_data['name'],
            user=user,
            defaults={
                'model': interface_data['model'],
                'temperature': interface_data['temperature'],
                'max_tokens': interface_data['max_tokens'],
                'purposes': interface_data['purposes'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ 创建接口配置: {interface.name}")
        else:
            print(f"✅ 找到现有接口: {interface.name}")
    
    print("\n📊 当前数据统计:")
    print(f"  - API提供商: {ApiProvider.objects.count()}")
    print(f"  - API Token: {ApiToken.objects.count()}")
    print(f"  - 接口配置: {ApiInterface.objects.count()}")
    
    print("\n🎉 测试数据创建完成！")
    print("\n📝 下一步操作:")
    print("1. 访问 https://aihubmix.com 获取真实的API Token")
    print("2. 在管理界面或数据库中更新Token")
    print("3. 重新运行 test_gemini.py 进行测试")

if __name__ == "__main__":
    create_test_data()