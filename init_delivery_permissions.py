#!/usr/bin/env python3
"""
初始化出库单相关权限
"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'order_system.db')


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_delivery_permissions():
    """初始化出库单相关权限"""
    conn = get_connection()
    cursor = conn.cursor()

    # 出库单相关权限
    delivery_permissions = [
        ('出库单查看', 'delivery.view', '查看出库单列表和详情'),
        ('出库单创建', 'delivery.create', '创建新的出库单'),
        ('出库单编辑', 'delivery.edit', '编辑出库单信息'),
        ('出库单删除', 'delivery.delete', '删除出库单'),
        ('出库单导出', 'delivery.export', '导出出库单为Excel'),
    ]

    print("开始添加出库单权限...")

    for name, code, description in delivery_permissions:
        # 检查权限是否已存在
        cursor.execute('SELECT id FROM permissions WHERE code = ?', (code,))
        existing = cursor.fetchone()

        if existing:
            print(f"  权限已存在: {name} ({code})")
        else:
            cursor.execute('''
                INSERT INTO permissions (name, code, description)
                VALUES (?, ?, ?)
            ''', (name, code, description))
            print(f"  添加权限: {name} ({code})")

    conn.commit()

    # 获取超级管理员角色ID
    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
    admin_role = cursor.fetchone()

    if admin_role:
        admin_role_id = admin_role['id']

        # 为超级管理员分配所有出库单权限
        cursor.execute('SELECT id, code FROM permissions WHERE code LIKE "delivery.%"')
        delivery_perms = cursor.fetchall()

        print(f"\n为超级管理员角色分配出库单权限...")

        for perm in delivery_perms:
            # 检查是否已关联
            cursor.execute('''
                SELECT 1 FROM role_permissions
                WHERE role_id = ? AND permission_id = ?
            ''', (admin_role_id, perm['id']))

            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (?, ?)
                ''', (admin_role_id, perm['id']))
                print(f"  分配权限: {perm['code']}")
            else:
                print(f"  权限已分配: {perm['code']}")

        conn.commit()

    conn.close()
    print("\n出库单权限初始化完成！")


if __name__ == '__main__':
    init_delivery_permissions()
