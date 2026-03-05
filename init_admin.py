#!/usr/bin/env python3
"""
初始化超级管理员账号和权限
"""

import sqlite3
import os
import sys

# 数据库文件路径 - 使用与database.py相同的方式获取
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


def init_admin():
    """初始化超级管理员账号和权限"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 创建管理员角色
        cursor.execute('''
            INSERT OR IGNORE INTO roles (name, description)
            VALUES (?, ?)
        ''', ('admin', '超级管理员'))
        
        # 创建基本权限
        permissions = [
            ('查看订单', 'order.view', '查看订单列表和详情'),
            ('创建订单', 'order.create', '创建新订单'),
            ('编辑订单', 'order.edit', '编辑现有订单'),
            ('删除订单', 'order.delete', '删除订单'),
            ('扫描条码', 'scan.scan', '扫描条码'),
            ('查看扫描记录', 'scan.view', '查看扫描记录'),
            ('打印标签', 'label.print', '打印标签'),
            ('管理标签模板', 'label.template', '管理标签模板'),
            ('生成出库单', 'delivery.generate', '生成出库单'),
            ('查看统计报表', 'report.view', '查看统计报表'),
            ('管理用户', 'user.manage', '管理用户和权限'),
        ]
        
        for name, code, description in permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO permissions (name, code, description)
                VALUES (?, ?, ?)
            ''', (name, code, description))
        
        # 获取管理员角色ID
        cursor.execute('SELECT id FROM roles WHERE name = ?', ('admin',))
        admin_role = cursor.fetchone()
        if not admin_role:
            print('创建管理员角色失败')
            return False
        admin_role_id = admin_role['id']
        
        # 获取所有权限ID
        cursor.execute('SELECT id FROM permissions')
        permissions = cursor.fetchall()
        
        # 为管理员角色分配所有权限
        for permission in permissions:
            permission_id = permission['id']
            cursor.execute('''
                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                VALUES (?, ?)
            ''', (admin_role_id, permission_id))
        
        # 创建超级管理员用户
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, name, email, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin', '超级管理员', 'admin@example.com', 1))
        
        # 获取超级管理员用户ID
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        if not admin_user:
            print('创建超级管理员用户失败')
            return False
        admin_user_id = admin_user['id']
        
        # 为超级管理员用户分配管理员角色
        cursor.execute('''
            INSERT OR IGNORE INTO user_roles (user_id, role_id)
            VALUES (?, ?)
        ''', (admin_user_id, admin_role_id))
        
        conn.commit()
        print('超级管理员账号初始化成功！')
        print('用户名: admin')
        print('密码: admin')
        return True
        
    except Exception as e:
        print(f'初始化超级管理员账号失败: {str(e)}')
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    # 先初始化数据库表结构
    from database import init_database
    init_database()
    
    # 再初始化超级管理员账号
    init_admin()
