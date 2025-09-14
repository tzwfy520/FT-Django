#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import sys

# 远程MySQL连接配置
REMOTE_DB_CONFIG = {
    'host': '115.190.90.219',
    'port': 3306,
    'user': 'root',
    'password': 'Eccom@12345',
    'database': 'flask_stock',
    'charset': 'utf8mb4',
    'connect_timeout': 60,
    'read_timeout': 60,
    'write_timeout': 60,
    'autocommit': True,
    'ssl_disabled': True
}

def test_mysql_connection():
    """测试MySQL连接"""
    connection = None
    try:
        print(f"正在测试连接到MySQL服务器: {REMOTE_DB_CONFIG['host']}:{REMOTE_DB_CONFIG['port']}")
        print(f"用户名: {REMOTE_DB_CONFIG['user']}")
        print(f"数据库: {REMOTE_DB_CONFIG['database']}")
        
        # 尝试连接
        connection = pymysql.connect(**REMOTE_DB_CONFIG)
        print("✓ MySQL连接成功!")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ MySQL版本: {version[0]}")
            
            # 检查目标表是否存在
            cursor.execute("SHOW TABLES LIKE 'stock_basic_info'")
            table_exists = cursor.fetchone()
            if table_exists:
                print("✓ 目标表 'stock_basic_info' 存在")
                
                # 获取表结构
                cursor.execute("DESCRIBE stock_basic_info")
                columns = cursor.fetchall()
                print("表结构:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
                    
                # 获取数据行数
                cursor.execute("SELECT COUNT(*) FROM stock_basic_info")
                count = cursor.fetchone()
                print(f"✓ 表中共有 {count[0]} 条记录")
                
                # 获取前5条数据样本
                cursor.execute("SELECT * FROM stock_basic_info LIMIT 5")
                samples = cursor.fetchall()
                print("数据样本:")
                for i, sample in enumerate(samples, 1):
                    print(f"  {i}. {sample}")
            else:
                print("✗ 目标表 'stock_basic_info' 不存在")
                
    except pymysql.Error as e:
        print(f"✗ MySQL连接失败: {e}")
        print(f"错误代码: {e.args[0]}")
        if len(e.args) > 1:
            print(f"错误信息: {e.args[1]}")
        return False
    except Exception as e:
        print(f"✗ 连接过程中发生未知错误: {e}")
        return False
    finally:
        if connection:
            connection.close()
            print("连接已关闭")
    
    return True

if __name__ == '__main__':
    print("=== MySQL连接测试 ===")
    success = test_mysql_connection()
    if success:
        print("\n测试完成: 连接成功")
        sys.exit(0)
    else:
        print("\n测试完成: 连接失败")
        sys.exit(1)