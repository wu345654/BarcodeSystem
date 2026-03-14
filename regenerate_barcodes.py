#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import OrderModel, OrderDetailModel, BarcodeModel
from barcode_generator import create_barcodes_for_order

def regenerate_all_barcodes():
    orders = OrderModel.get_all(page=1, page_size=1000)
    
    print(f"找到 {len(orders)} 个订单")
    
    for order in orders:
        order_id = order['id']
        print(f"\n处理订单 {order_id}: {order['work_tag']}")
        
        details = OrderDetailModel.get_by_order(order_id)
        
        if not details:
            print(f"  订单 {order_id} 没有明细数据，跳过")
            continue
        
        print(f"  找到 {len(details)} 个订单明细")
        
        deleted_count = BarcodeModel.delete_by_order(order_id)
        print(f"  删除了 {deleted_count} 个旧条码")
        
        barcodes = create_barcodes_for_order(order_id, details)
        print(f"  成功生成 {len(barcodes)} 个新条码")
        
        for i, barcode in enumerate(barcodes[:3]):
            print(f"    条码 {i+1}: {barcode['barcode']}, detail_id: {barcode.get('order_detail_id')}")
        if len(barcodes) > 3:
            print(f"    ... 还有 {len(barcodes) - 3} 个条码")
    
    print(f"\n完成！共处理 {len(orders)} 个订单")
    
if __name__ == '__main__':
    regenerate_all_barcodes()
