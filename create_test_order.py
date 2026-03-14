#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import OrderModel, OrderDetailModel, BarcodeModel
from barcode_generator import create_barcodes_for_order

def create_test_order():
    """创建测试订单"""
    print("创建测试订单...")
    
    with app.app_context():
        try:
            # 创建订单
            order_id = OrderModel.create(
                work_tag="测试工程",
                name="测试订单",
                product="测试产品",
                quantity=3
            )
            print(f"订单创建成功，ID: {order_id}")
            
            # 创建订单明细
            details = []
            
            # 明细1
            detail1_id = OrderDetailModel.create(
                order_id=order_id,
                sequence_no=1,
                product_name="不锈钢板",
                color="银色",
                thickness="1.2mm",
                drawing_no="DWG001",
                quantity=1
            )
            details.append({'id': detail1_id, 'sequence_no': 1, 'product_name': "不锈钢板", 'color': "银色", 'thickness': "1.2mm", 'drawing_no': "DWG001", 'quantity': 1})
            
            # 明细2
            detail2_id = OrderDetailModel.create(
                order_id=order_id,
                sequence_no=2,
                product_name="铝板",
                color="金色",
                thickness="2.0mm",
                drawing_no="DWG002",
                quantity=2
            )
            details.append({'id': detail2_id, 'sequence_no': 2, 'product_name': "铝板", 'color': "金色", 'thickness': "2.0mm", 'drawing_no': "DWG002", 'quantity': 2})
            
            print(f"订单明细创建成功: {len(details)} 个明细")
            
            # 生成条码
            barcodes = create_barcodes_for_order(order_id, details)
            print(f"条码生成成功: {len(barcodes)} 个条码")
            
            # 验证条码数据
            print("\n验证条码数据:")
            for i, barcode in enumerate(barcodes):
                print(f"条码 {i+1}: 序号={barcode['sequence_no']}, 明细ID={barcode.get('order_detail_id')}")
            
            print(f"\n测试订单创建完成！订单ID: {order_id}")
            print(f"请访问 http://localhost:8888/print-label/{order_id} 查看标签")
            
        except Exception as e:
            print(f"创建测试订单失败: {str(e)}")

if __name__ == '__main__':
    create_test_order()
