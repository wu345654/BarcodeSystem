#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import get_connection

def clean_test_data():
    """清理测试数据"""
    print("清理测试数据...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        # 清除扫描记录
        cursor.execute('DELETE FROM scan_records')
        
        # 清除条码
        cursor.execute('DELETE FROM barcodes')
        
        # 清除订单明细
        cursor.execute('DELETE FROM order_details')
        
        # 清除订单
        cursor.execute('DELETE FROM orders')
        
        # 提交事务
        conn.commit()
        print("✅ 测试数据清理成功")
        
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    clean_test_data()
