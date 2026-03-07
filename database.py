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
    
    # 订单明细表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            sequence_no INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            color TEXT,
            thickness TEXT,
            drawing_no TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
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
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 角色表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 权限表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 角色权限关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )
    ''')
    
    # 用户角色关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        )
    ''')
    
    # 出库单表头
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_no TEXT NOT NULL UNIQUE,
            customer_name TEXT NOT NULL,
            contract_no TEXT,
            project_name TEXT,
            delivery_quantity INTEGER DEFAULT 0,
            delivery_address TEXT,
            delivery_area REAL,
            receiver_name TEXT,
            receiver_phone TEXT,
            carrier_name TEXT,
            plate_number TEXT,
            driver_phone TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 出库单明细表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_order_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_order_id INTEGER NOT NULL,
            order_detail_id INTEGER,
            sequence_no INTEGER NOT NULL,
            building_no TEXT,
            drawing_no TEXT,
            product_name TEXT,
            width REAL,
            thickness TEXT,
            unit TEXT,
            quantity INTEGER DEFAULT 0,
            single_weight REAL,
            total_weight REAL,
            single_groove REAL,
            total_groove REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (delivery_order_id) REFERENCES delivery_orders(id) ON DELETE CASCADE,
            FOREIGN KEY (order_detail_id) REFERENCES order_details(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()


class OrderModel:
    """订单数据模型"""
    
    @staticmethod
    def create(work_tag: str, name: str, product: str, quantity: int = 0) -> int:
        """创建订单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (work_tag, name, product, quantity)
            VALUES (?, ?, ?, ?)
        ''', (work_tag, name, product, quantity))
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
        allowed_fields = ['work_tag', 'name', 'product', 'quantity']
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
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class OrderDetailModel:
    """订单明细数据模型"""
    
    @staticmethod
    def create(order_id: int, sequence_no: int, product_name: str, 
               color: str = None, thickness: str = None, 
               drawing_no: str = None, quantity: int = 1) -> int:
        """创建订单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO order_details (order_id, sequence_no, product_name, color, thickness, drawing_no, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, sequence_no, product_name, color, thickness, drawing_no, quantity))
        detail_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return detail_id
    
    @staticmethod
    def get_by_id(detail_id: int) -> Optional[Dict]:
        """根据ID获取订单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM order_details WHERE id = ?', (detail_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_order(order_id: int) -> List[Dict]:
        """获取订单的所有明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM order_details WHERE order_id = ? ORDER BY sequence_no
        ''', (order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(detail_id: int, **kwargs) -> bool:
        """更新订单明细"""
        allowed_fields = ['sequence_no', 'product_name', 'color', 'thickness', 'drawing_no', 'quantity']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [detail_id]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE order_details SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(detail_id: int) -> bool:
        """删除订单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM order_details WHERE id = ?', (detail_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete_by_order(order_id: int) -> bool:
        """删除订单的所有明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM order_details WHERE order_id = ?', (order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


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
    
    @staticmethod
    def delete_by_order(order_id: int) -> bool:
        """删除订单的所有条码"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM barcodes WHERE order_id = ?', (order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


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


class UserModel:
    """用户数据模型"""
    
    @staticmethod
    def create(username: str, password: str, name: str, email: str = None, avatar: str = None) -> int:
        """创建用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password, name, email, avatar)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password, name, email, avatar))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Dict]:
        """根据用户名获取用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict]:
        """获取所有用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(user_id: int, **kwargs) -> bool:
        """更新用户"""
        allowed_fields = ['username', 'password', 'name', 'email', 'is_active', 'avatar']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', values)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(user_id: int) -> bool:
        """删除用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


class RoleModel:
    """角色数据模型"""
    
    @staticmethod
    def create(name: str, description: str = None) -> int:
        """创建角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO roles (name, description)
            VALUES (?, ?)
        ''', (name, description))
        role_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return role_id
    
    @staticmethod
    def get_by_id(role_id: int) -> Optional[Dict]:
        """根据ID获取角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE id = ?', (role_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_name(name: str) -> Optional[Dict]:
        """根据名称获取角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict]:
        """获取所有角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roles ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class PermissionModel:
    """权限数据模型"""
    
    @staticmethod
    def create(name: str, code: str, description: str = None) -> int:
        """创建权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO permissions (name, code, description)
            VALUES (?, ?, ?)
        ''', (name, code, description))
        permission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return permission_id
    
    @staticmethod
    def get_by_id(permission_id: int) -> Optional[Dict]:
        """根据ID获取权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM permissions WHERE id = ?', (permission_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_code(code: str) -> Optional[Dict]:
        """根据代码获取权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM permissions WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all() -> List[Dict]:
        """获取所有权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM permissions ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class UserRoleModel:
    """用户角色关联模型"""
    
    @staticmethod
    def create(user_id: int, role_id: int) -> bool:
        """为用户分配角色"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_roles (user_id, role_id)
                VALUES (?, ?)
            ''', (user_id, role_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_roles_by_user(user_id: int) -> List[Dict]:
        """获取用户的所有角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.* FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_users_by_role(role_id: int) -> List[Dict]:
        """获取角色的所有用户"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.* FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            WHERE ur.role_id = ?
        ''', (role_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class RolePermissionModel:
    """角色权限关联模型"""
    
    @staticmethod
    def create(role_id: int, permission_id: int) -> bool:
        """为角色分配权限"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            ''', (role_id, permission_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_permissions_by_role(role_id: int) -> List[Dict]:
        """获取角色的所有权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.* FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
        ''', (role_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_roles_by_permission(permission_id: int) -> List[Dict]:
        """获取拥有该权限的所有角色"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.* FROM roles r
            JOIN role_permissions rp ON r.id = rp.role_id
            WHERE rp.permission_id = ?
        ''', (permission_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class AuthModel:
    """认证和权限检查模型"""
    
    @staticmethod
    def check_user_permission(user_id: int, permission_code: str) -> bool:
        """检查用户是否拥有指定权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = ? AND p.code = ?
        ''', (user_id, permission_code))
        row = cursor.fetchone()
        conn.close()
        return row['count'] > 0
    
    @staticmethod
    def get_user_permissions(user_id: int) -> List[Dict]:
        """获取用户的所有权限"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT p.* FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = ?
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


class DeliveryOrderModel:
    """出库单表头数据模型"""
    
    @staticmethod
    def create(delivery_no: str, customer_name: str, contract_no: str = None,
               project_name: str = None, delivery_quantity: int = 0,
               delivery_address: str = None, delivery_area: float = None,
               receiver_name: str = None, receiver_phone: str = None,
               carrier_name: str = None, plate_number: str = None,
               driver_phone: str = None, status: str = 'draft') -> int:
        """创建出库单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO delivery_orders (delivery_no, customer_name, contract_no, project_name,
                delivery_quantity, delivery_address, delivery_area, receiver_name,
                receiver_phone, carrier_name, plate_number, driver_phone, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (delivery_no, customer_name, contract_no, project_name,
              delivery_quantity, delivery_address, delivery_area, receiver_name,
              receiver_phone, carrier_name, plate_number, driver_phone, status))
        delivery_order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return delivery_order_id
    
    @staticmethod
    def get_by_id(delivery_order_id: int) -> Optional[Dict]:
        """根据ID获取出库单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM delivery_orders WHERE id = ?', (delivery_order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all(page: int = 1, page_size: int = 10) -> List[Dict]:
        """获取所有出库单"""
        conn = get_connection()
        cursor = conn.cursor()
        offset = (page - 1) * page_size
        cursor.execute('''
            SELECT * FROM delivery_orders 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_count() -> int:
        """获取出库单总数"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM delivery_orders')
        row = cursor.fetchone()
        conn.close()
        return row['count']
    
    @staticmethod
    def update(delivery_order_id: int, **kwargs) -> bool:
        """更新出库单"""
        allowed_fields = ['customer_name', 'contract_no', 'project_name',
                         'delivery_quantity', 'delivery_address', 'delivery_area',
                         'receiver_name', 'receiver_phone', 'carrier_name',
                         'plate_number', 'driver_phone', 'status']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [delivery_order_id]
        
        sql = f"""UPDATE delivery_orders 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?"""
        cursor.execute(sql, values)
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(delivery_order_id: int) -> bool:
        """删除出库单"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM delivery_orders WHERE id = ?', (delivery_order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def generate_delivery_no() -> str:
        """生成出库单号"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM delivery_orders 
            WHERE delivery_no LIKE ?
        ''', (f'CK{date_str}%',))
        row = cursor.fetchone()
        conn.close()
        seq = row['count'] + 1
        return f'CK{date_str}{seq:04d}'


class DeliveryOrderDetailModel:
    """出库单明细数据模型"""
    
    @staticmethod
    def create(delivery_order_id: int, sequence_no: int, order_detail_id: int = None,
               building_no: str = None, drawing_no: str = None, product_name: str = None,
               width: float = None, thickness: str = None, unit: str = None,
               quantity: int = 0, single_weight: float = None, total_weight: float = None,
               single_groove: float = None, total_groove: float = None) -> int:
        """创建出库单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO delivery_order_details (delivery_order_id, order_detail_id, sequence_no,
                building_no, drawing_no, product_name, width, thickness, unit, quantity,
                single_weight, total_weight, single_groove, total_groove)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (delivery_order_id, order_detail_id, sequence_no, building_no, drawing_no,
              product_name, width, thickness, unit, quantity, single_weight, total_weight,
              single_groove, total_groove))
        detail_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return detail_id
    
    @staticmethod
    def get_by_id(detail_id: int) -> Optional[Dict]:
        """根据ID获取出库单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM delivery_order_details WHERE id = ?', (detail_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_delivery_order(delivery_order_id: int) -> List[Dict]:
        """根据出库单ID获取所有明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, od.color, od.thickness as order_thickness
            FROM delivery_order_details d
            LEFT JOIN order_details od ON d.order_detail_id = od.id
            WHERE d.delivery_order_id = ?
            ORDER BY d.sequence_no
        ''', (delivery_order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(detail_id: int, **kwargs) -> bool:
        """更新出库单明细"""
        allowed_fields = ['sequence_no', 'building_no', 'drawing_no', 'product_name',
                         'width', 'thickness', 'unit', 'quantity', 'single_weight',
                         'total_weight', 'single_groove', 'total_groove']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [detail_id]
        
        sql = f"""UPDATE delivery_order_details 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?"""
        cursor.execute(sql, values)
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete(detail_id: int) -> bool:
        """删除出库单明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM delivery_order_details WHERE id = ?', (detail_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    @staticmethod
    def delete_by_delivery_order(delivery_order_id: int) -> bool:
        """删除出库单的所有明细"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM delivery_order_details WHERE delivery_order_id = ?', (delivery_order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


# 初始化数据库
if __name__ == '__main__':
    init_database()
    print("数据库初始化完成！")
