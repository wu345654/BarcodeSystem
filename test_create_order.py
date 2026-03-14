#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import requests

def test_create_order():
    """测试创建订单，只提供work_tag"""
    print("测试创建订单...")
    
    # 测试数据：只提供work_tag
    order_data = {
        "work_tag": "测试工程",
        "details": [
            {
                "sequence_no": 1,
                "product_name": "测试产品",
                "quantity": 2
            }
        ]
    }
    
    try:
        # 发送请求
        response = requests.post('http://localhost:8888/api/orders', json=order_data)
        result = response.json()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {result}")
        
        if result.get('success'):
            print("✅ 测试成功！订单创建成功")
            print(f"订单ID: {result['data']['order_id']}")
        else:
            print(f"❌ 测试失败: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == '__main__':
    test_create_order()
