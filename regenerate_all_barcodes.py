#!/usr/bin/env python3
"""
重新生成所有订单的条码
按照当前规则（基于订单明细的数量）重新生成条码
"""

import os
import sys
from database import get_connection, BarcodeModel, OrderModel, OrderDetailModel
from barcode_generator import create_barcodes_for_order


def regenerate_all_barcodes():
    """重新生成所有订单的条码"""
    print("开始重新生成所有订单的条码...")
    
    # 清除所有条码
    print("1. 清除所有现有条码...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM barcodes')
    conn.commit()
    conn.close()
    print("✓ 所有条码已清除")
    
    # 获取所有订单
    print("2. 获取所有订单...")
    orders = OrderModel.get_all(1, 1000)  # 获取最多1000个订单
    print(f"✓ 找到 {len(orders)} 个订单")
    
    # 为每个订单重新生成条码
    print("3. 为每个订单重新生成条码...")
    total_barcodes = 0
    
    for order in orders:
        order_id = order['id']
        print(f"  处理订单 ID: {order_id}")
        
        # 获取订单明细
        order_details = OrderDetailModel.get_by_order(order_id)
        if not order_details:
            print(f"    ⚠️  订单 {order_id} 没有订单明细，跳过")
            continue
        
        # 生成条码
        barcodes = create_barcodes_for_order(order_id, order_details)
        total_barcodes += len(barcodes)
        print(f"    ✓ 生成了 {len(barcodes)} 个条码")
    
    print(f"\n✓ 重新生成完成！")
    print(f"总计生成了 {total_barcodes} 个条码")


if __name__ == '__main__':
    regenerate_all_barcodes()
