#!/usr/bin/env python3
import sqlite3

def modify_orders_table():
    """修改orders表结构，移除name和product字段的NOT NULL约束"""
    print("开始修改orders表结构...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect('order_system.db')
        cursor = conn.cursor()
        
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        # 1. 创建临时表
        cursor.execute('''
            CREATE TABLE orders_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_tag TEXT NOT NULL,
                name TEXT,
                color TEXT,
                drawing_no TEXT,
                product TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ 创建临时表成功")
        
        # 2. 复制数据到临时表
        cursor.execute('''
            INSERT INTO orders_temp (id, work_tag, name, color, drawing_no, product, quantity, created_at, updated_at)
            SELECT id, work_tag, name, color, drawing_no, product, quantity, created_at, updated_at
            FROM orders
        ''')
        print("✓ 复制数据成功")
        
        # 3. 删除原表
        cursor.execute('DROP TABLE orders')
        print("✓ 删除原表成功")
        
        # 4. 重命名临时表为原表名
        cursor.execute('ALTER TABLE orders_temp RENAME TO orders')
        print("✓ 重命名表成功")
        
        # 提交事务
        conn.commit()
        print("\n✅ 数据库表结构修改成功！")
        print("name和product字段现在可以为空")
        
    except Exception as e:
        print(f"\n❌ 修改失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    modify_orders_table()
