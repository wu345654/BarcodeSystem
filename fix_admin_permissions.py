from database import init_database, UserModel, RoleModel, PermissionModel, UserRoleModel, RolePermissionModel, AuthModel, get_connection

def fix_admin_permissions():
    """修复admin用户的权限"""
    init_database()
    
    # 获取admin用户
    admin = UserModel.get_by_username('admin')
    if not admin:
        print("Admin用户不存在")
        return
    
    print(f"Admin用户ID: {admin['id']}")
    
    # 检查admin角色是否存在
    admin_role = RoleModel.get_by_name('admin')
    if not admin_role:
        print("创建admin角色...")
        admin_role_id = RoleModel.create(name='admin', description='管理员角色')
        admin_role = RoleModel.get_by_id(admin_role_id)
    else:
        print(f"Admin角色已存在，ID: {admin_role['id']}")
    
    # 检查admin用户是否已关联admin角色
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_roles WHERE user_id = ? AND role_id = ?', 
                 (admin['id'], admin_role['id']))
    existing = cursor.fetchone()
    conn.close()
    
    if not existing:
        print("为admin用户分配admin角色...")
        UserRoleModel.create(user_id=admin['id'], role_id=admin_role['id'])
    else:
        print("admin用户已拥有admin角色")
    
    # 获取所有权限
    permissions = PermissionModel.get_all()
    print(f"系统共有 {len(permissions)} 个权限")
    
    # 为admin角色分配所有权限
    for permission in permissions:
        # 检查是否已分配
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM role_permissions WHERE role_id = ? AND permission_id = ?', 
                     (admin_role['id'], permission['id']))
        existing = cursor.fetchone()
        conn.close()
        
        if not existing:
            print(f"为admin角色分配权限: {permission['code']} - {permission['name']}")
            RolePermissionModel.create(role_id=admin_role['id'], permission_id=permission['id'])
        else:
            print(f"admin角色已拥有权限: {permission['code']}")
    
    print("\nAdmin用户权限修复完成！")
    
    # 验证admin用户的权限
    user_permissions = AuthModel.get_user_permissions(admin['id'])
    print(f"\nAdmin用户当前拥有 {len(user_permissions)} 个权限:")
    for perm in user_permissions:
        print(f"  - {perm['code']}: {perm['name']}")

if __name__ == '__main__':
    fix_admin_permissions()