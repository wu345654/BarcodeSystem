#!/usr/bin/env python3
"""
清除数据库中的模拟数据脚本
保留表结构，只删除数据
"""

import sqlite3
import os

def clear_database_data():
    """清除数据库中的所有数据但保留表结构"""
    
    # 数据库文件路径
    db_path = 'order_system.db'
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在！")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("连接数据库成功")
        
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        # 清除表数据（按照外键依赖顺序）
        tables = ['scan_records', 'barcodes', 'orders']
        
        for table in tables:
            try:
                cursor.execute(f'DELETE FROM {table}')
                print(f"清除表 {table} 中的数据成功")
            except Exception as e:
                print(f"清除表 {table} 数据时出错: {e}")
                conn.rollback()
                conn.close()
                return False
        
        # 提交事务
        conn.commit()
        print("所有表数据清除成功")
        
        # 关闭连接
        conn.close()
        
        print("\n数据库模拟数据已清除，表结构已保留")
        return True
        
    except Exception as e:
        print(f"操作数据库时出错: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """主函数"""
    print("========================================")
    print("清除数据库模拟数据脚本")
    print("========================================")
    print("此脚本将清除数据库中的所有数据，但保留表结构")
    print("\n正在执行清除操作...")
    
    success = clear_database_data()
    
    if success:
        print("\n操作完成：数据库模拟数据已成功清除")
    else:
        print("\n操作失败：无法清除数据库数据")

if __name__ == "__main__":
    main()