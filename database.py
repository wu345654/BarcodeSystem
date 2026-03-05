import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# 数据库文件路径 - 使用更可靠的方式获取当前文件所在目录
import sys
if getattr(sys, 'frozen', False):
    # 打包后的环境
    DATABASE_PATH = os.path.join(os.path.dirname(sys.executable), 'order_system.db')
else:
    # 开发环境
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'order_system.db')


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库表结构"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            work_tag TEXT NOT NULL,
            name TEXT NOT NULL,
            color TEXT,
            drawing_no TEXT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 条码表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            barcode TEXT NOT NULL UNIQUE,
            sequence_no INTEGER NOT NULL,
            is_scanned BOOLEAN DEFAULT 0,
            scanned_at TIMESTAMP,
            scanned_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    ''')
    
    # 扫描记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode_id INTEGER NOT NULL,
            barcode TEXT NOT NULL,
            scan_result TEXT NOT NULL,
            message TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scanned_by TEXT,
            FOREIGN KEY (barcode_id) REFERENCES barcodes(id)
        )
    ''')
    
    # 标签模板表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS label_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            template TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


class OrderModel:
    """订单数据模型"""
    
    @staticmethod
    def create(work_tag: str, name: str, product: str, 
               color: str = None, drawing_no: str = None, 
               quantity: int = 1) -> int:
        """创建订单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (work_tag, name, color, drawing_no, product, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (work_tag, name, color, drawing_no, product, quantity))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id
    
    @staticmethod
    def get_by_id(order_id: int) -> Optional[Dict]:
        """根据ID获取订单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all(page: int = 1, page_size: int = 10) -> List[Dict]:
        """获取所有订单"""
        conn = get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * page_size
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?', (page_size, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(order_id: int, **kwargs) -> bool:
        """更新订单"""
        allowed_fields = ['work_tag', 'name', 'color', 'drawing_no', 'product', 'quantity']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [order_id]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE orders SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(order_id: int) -> bool:
        """删除订单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def search(keyword: str) -> List[Dict]:
        """搜索订单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM orders 
            WHERE work_tag LIKE ? OR name LIKE ? OR product LIKE ? 
            OR drawing_no LIKE ? OR color LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', 
              f'%{keyword}%', f'%{keyword}%'))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class BarcodeModel:
    """条码数据模型"""
    
    @staticmethod
    def create(order_id: int, barcode: str, sequence_no: int) -> int:
        """创建条码"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO barcodes (order_id, barcode, sequence_no)
            VALUES (?, ?, ?)
        ''', (order_id, barcode, sequence_no))
        barcode_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return barcode_id
    
    @staticmethod
    def get_by_order(order_id: int) -> List[Dict]:
        """获取订单的所有条码"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM barcodes WHERE order_id = ? ORDER BY sequence_no
        ''', (order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_barcode(barcode: str) -> Optional[Dict]:
        """根据条码值获取条码信息"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM barcodes WHERE barcode = ?', (barcode,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def mark_as_scanned(barcode_id: int, scanned_by: str = None) -> bool:
        """标记条码为已扫描"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE barcodes 
            SET is_scanned = 1, scanned_at = CURRENT_TIMESTAMP, scanned_by = ?
            WHERE id = ?
        ''', (scanned_by, barcode_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def get_scan_statistics(order_id: int) -> Dict:
        """获取订单的扫描统计"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_scanned = 1 THEN 1 ELSE 0 END) as scanned
            FROM barcodes WHERE order_id = ?
        ''', (order_id,))
        row = cursor.fetchone()
        conn.close()
        return {
            'total': row['total'] or 0,
            'scanned': row['scanned'] or 0,
            'unscanned': (row['total'] or 0) - (row['scanned'] or 0)
        }


class ScanRecordModel:
    """扫描记录数据模型"""
    
    @staticmethod
    def create(barcode_id: int, barcode: str, scan_result: str, 
               message: str = None, scanned_by: str = None) -> int:
        """创建扫描记录"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scan_records (barcode_id, barcode, scan_result, message, scanned_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (barcode_id, barcode, scan_result, message, scanned_by))
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id
    
    @staticmethod
    def get_all(page: int = None, page_size: int = None, limit: int = 100) -> List[Dict]:
        """获取所有扫描记录"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if page and page_size:
            offset = (page - 1) * page_size
            cursor.execute('''
                SELECT * FROM scan_records 
                ORDER BY scanned_at DESC 
                LIMIT ? OFFSET ?
            ''', (page_size, offset))
        else:
            cursor.execute('''
                SELECT * FROM scan_records 
                ORDER BY scanned_at DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_barcode(barcode: str) -> List[Dict]:
        """获取条码的扫描历史"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM scan_records 
            WHERE barcode = ? 
            ORDER BY scanned_at DESC
        ''', (barcode,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class LabelTemplateModel:
    """标签模板数据模型"""
    
    @staticmethod
    def create(name: str, template: str) -> int:
        """创建标签模板"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO label_templates (name, template)
            VALUES (?, ?)
        ''', (name, template))
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return template_id
    
    @staticmethod
    def get_by_id(template_id: int) -> Optional[Dict]:
        """根据ID获取标签模板"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM label_templates WHERE id = ?', (template_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict]:
        """获取所有标签模板"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM label_templates ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(template_id: int, name: str, template: str) -> bool:
        """更新标签模板"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE label_templates 
            SET name = ?, template = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (name, template, template_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(template_id: int) -> bool:
        """删除标签模板"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM label_templates WHERE id = ?', (template_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


# 初始化数据库
if __name__ == '__main__':
    init_database()
    print("数据库初始化完成！")
