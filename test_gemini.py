#!/usr/bin/env python3
"""
Gemini 2.5 Flash Preview 模型测试脚本
用于排查 gemini-2.5-flash-preview-04-17 接口测试无回复问题
"""

import os
import sys
import time
import requests
from openai import OpenAI

# 添加Django项目路径
sys.path.append('/Users/wangfuyu/PythonCode/FT-Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

import django
django.setup()

from apps.api_management.models import ApiProvider, ApiToken, ApiInterface

def test_gemini_direct():
    """直接测试Gemini模型"""
    print("=== 直接测试 Gemini 2.5 Flash Preview ===\n")
    
    try:
        # 获取推理时代的API配置
        provider = ApiProvider.objects.filter(name__icontains='aihubmix').first()
        if not provider:
            print("❌ 未找到推理时代API提供商配置")
            return False
            
        print(f"✅ 找到API提供商: {provider.display_name}")
        print(f"   Base URL: {provider.base_url}")
        
        # 获取API Token
        token = ApiToken.objects.filter(provider=provider, is_active=True).first()
        if not token:
            print("❌ 未找到有效的API Token")
            return False
            
        print(f"✅ 找到有效Token: {token.token[:10]}...")
        
        # 创建OpenAI客户端
        client = OpenAI(
            base_url=provider.base_url,
            api_key=token.token,
            timeout=600.0  # 10分钟超时
        )
        
        print("\n🔄 开始测试 gemini-2.5-flash-preview-04-17...")
        start_time = time.time()
        
        # 测试请求
        completion = client.chat.completions.create(
            model="gemini-2.5-flash-preview-04-17",
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"\n✅ 测试成功！响应时间: {response_time:.2f}秒")
        print(f"模型回复: {completion.choices[0].message.content}")
        print(f"Token使用情况:")
        print(f"  - 输入Token: {completion.usage.prompt_tokens}")
        print(f"  - 输出Token: {completion.usage.completion_tokens}")
        print(f"  - 总Token: {completion.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return False

def test_gemini_via_requests():
    """使用requests库直接测试API"""
    print("\n=== 使用 requests 直接测试 API ===\n")
    
    try:
        # 获取配置
        provider = ApiProvider.objects.filter(name__icontains='aihubmix').first()
        token = ApiToken.objects.filter(provider=provider, is_active=True).first()
        
        if not provider or not token:
            print("❌ 缺少必要的配置信息")
            return False
        
        url = f"{provider.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gemini-2.5-flash-preview-04-17",
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        print(f"🔄 发送请求到: {url}")
        start_time = time.time()
        
        response = requests.post(
            url, 
            json=data, 
            headers=headers, 
            timeout=600  # 10分钟超时
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📊 响应时间: {response_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功！")
            print(f"模型回复: {result['choices'][0]['message']['content']}")
            if 'usage' in result:
                print(f"Token使用情况:")
                print(f"  - 输入Token: {result['usage']['prompt_tokens']}")
                print(f"  - 输出Token: {result['usage']['completion_tokens']}")
                print(f"  - 总Token: {result['usage']['total_tokens']}")
            return True
        else:
            print(f"❌ 请求失败")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_other_gemini_models():
    """测试其他Gemini模型作为对比"""
    print("\n=== 测试其他 Gemini 模型作为对比 ===\n")
    
    models_to_test = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    try:
        provider = ApiProvider.objects.filter(name__icontains='aihubmix').first()
        token = ApiToken.objects.filter(provider=provider, is_active=True).first()
        
        if not provider or not token:
            print("❌ 缺少必要的配置信息")
            return
        
        client = OpenAI(
            base_url=provider.base_url,
            api_key=token.token,
            timeout=60.0  # 1分钟超时
        )
        
        for model in models_to_test:
            print(f"🔄 测试模型: {model}")
            try:
                start_time = time.time()
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "你好"}
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                end_time = time.time()
                print(f"  ✅ {model} 测试成功，响应时间: {end_time - start_time:.2f}秒")
            except Exception as e:
                print(f"  ❌ {model} 测试失败: {str(e)}")
            print()
            
    except Exception as e:
        print(f"❌ 对比测试失败: {str(e)}")

def main():
    """主函数"""
    print("🚀 开始 Gemini 2.5 Flash Preview 问题排查\n")
    print("=" * 60)
    
    # 测试1: 使用OpenAI客户端
    success1 = test_gemini_direct()
    
    # 测试2: 使用requests直接调用
    success2 = test_gemini_via_requests()
    
    # 测试3: 对比其他模型
    test_other_gemini_models()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"  - OpenAI客户端测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"  - requests直接测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 结论: gemini-2.5-flash-preview-04-17 模型可以正常工作")
        print("   问题可能出现在应用的其他部分，建议检查:")
        print("   1. 前端请求处理逻辑")
        print("   2. 后端API接口实现")
        print("   3. 数据库接口配置")
    else:
        print("\n⚠️  结论: gemini-2.5-flash-preview-04-17 模型无法正常工作")
        print("   这可能是模型提供商的问题，建议:")
        print("   1. 联系推理时代客服")
        print("   2. 检查模型名称是否正确")
        print("   3. 确认账户权限和余额")

if __name__ == "__main__":
    main()