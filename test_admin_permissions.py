from database import init_database, UserModel, AuthModel

def test_admin_permissions():
    """测试admin用户权限"""
    init_database()
    
    # 获取admin用户
    admin = UserModel.get_by_username('admin')
    if not admin:
        print("Admin用户不存在")
        return
    
    print(f"Admin用户ID: {admin['id']}")
    
    # 获取admin用户的权限
    permissions = AuthModel.get_user_permissions(admin['id'])
    print(f"\nAdmin用户拥有 {len(permissions)} 个权限:")
    for perm in permissions:
        print(f"  - {perm['code']}: {perm['name']}")
    
    # 检查特定权限
    print("\n检查特定权限:")
    print(f"  - order.edit: {AuthModel.check_user_permission(admin['id'], 'order.edit')}")
    print(f"  - order.delete: {AuthModel.check_user_permission(admin['id'], 'order.delete')}")
    print(f"  - order.view: {AuthModel.check_user_permission(admin['id'], 'order.view')}")
    print(f"  - order.create: {AuthModel.check_user_permission(admin['id'], 'order.create')}")

if __name__ == '__main__':
    test_admin_permissions()