#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import OrderModel

def test_order_creation():
    """测试订单创建，只提供work_tag"""
    print("测试订单创建...")
    
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
    
    with app.app_context():
        try:
            # 计算订单明细总数量
            details = order_data.get('details', [])
            total_quantity = sum(detail.get('quantity', 1) for detail in details)
            
            # 创建订单
            order_id = OrderModel.create(
                work_tag=order_data['work_tag'],
                name=order_data.get('name', ''),
                product=order_data.get('product', ''),
                quantity=total_quantity
            )
            
            print(f"✅ 测试成功！订单创建成功")
            print(f"订单ID: {order_id}")
            
            # 验证订单是否存在
            order = OrderModel.get_by_id(order_id)
            if order:
                print(f"订单信息: {order}")
                print(f"name字段值: '{order.get('name')}'")
                print(f"product字段值: '{order.get('product')}'")
                print("✅ 订单数据验证成功")
            else:
                print("❌ 订单数据验证失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_order_creation()
