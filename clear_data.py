#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import get_connection

def clear_all_data():
    """清除所有订单、条码和扫描记录数据"""
    print("⚠️  警告：此操作将清除所有订单数据、条码数据和扫描记录！")
    print("请确认是否继续 (y/n): ")
    
    # 读取用户输入
    try:
        confirm = input().strip().lower()
    except EOFError:
        confirm = 'n'
    
    if confirm != 'y':
        print("操作已取消")
        return
    
    print("\n开始清除数据...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        # 清除扫描记录
        cursor.execute('DELETE FROM scan_records')
        scan_records_deleted = cursor.rowcount
        print(f"✓ 清除扫描记录: {scan_records_deleted} 条")
        
        # 清除条码
        cursor.execute('DELETE FROM barcodes')
        barcodes_deleted = cursor.rowcount
        print(f"✓ 清除条码数据: {barcodes_deleted} 条")
        
        # 清除订单明细
        cursor.execute('DELETE FROM order_details')
        order_details_deleted = cursor.rowcount
        print(f"✓ 清除订单明细: {order_details_deleted} 条")
        
        # 清除订单
        cursor.execute('DELETE FROM orders')
        orders_deleted = cursor.rowcount
        print(f"✓ 清除订单数据: {orders_deleted} 条")
        
        # 提交事务
        conn.commit()
        print("\n✅ 所有数据已成功清除！")
        
    except Exception as e:
        print(f"\n❌ 清除数据失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    clear_all_data()
