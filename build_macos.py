#!/usr/bin/env python3
"""
macOS环境下的自动化打包脚本
用于生成可在macOS系统一键运行的文件
"""

import os
import sys
import subprocess
import shutil
import platform

# 检查系统是否为macOS
if platform.system() != 'Darwin':
    print("错误：此脚本仅适用于macOS系统！")
    sys.exit(1)

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
        return result
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return None

def main():
    """主函数"""
    print("========================================")
    print("macOS环境下的条码系统打包脚本")
    print("========================================")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {project_root}")
    
    # 检查必要的文件
    required_files = [
        'app.py',
        'database.py',
        'requirements.txt'
    ]
    
    for file in required_files:
        file_path = os.path.join(project_root, file)
        if not os.path.exists(file_path):
            print(f"错误：缺少必要文件 {file}！")
            sys.exit(1)
    
    # 清理旧的构建文件
    print("\n清理旧的构建文件...")
    build_dir = os.path.join(project_root, 'build')
    dist_dir = os.path.join(project_root, 'dist')
    spec_file = os.path.join(project_root, 'BarcodeSystem.spec')
    
    for path in [build_dir, dist_dir]:
        if os.path.exists(path):
            print(f"删除目录: {path}")
            shutil.rmtree(path)
    
    if os.path.exists(spec_file):
        print(f"删除文件: {spec_file}")
        os.remove(spec_file)
    
    # 检查并安装依赖
    print("\n检查并安装依赖...")
    requirements_file = os.path.join(project_root, 'requirements.txt')
    
    # 安装PyInstaller
    print("安装PyInstaller...")
    run_command("pip3 install pyinstaller")
    
    # 安装项目依赖
    print("安装项目依赖...")
    run_command(f"pip3 install -r {requirements_file}")
    
    # 使用PyInstaller打包
    print("\n使用PyInstaller打包...")
    
    # 打包命令
    pyinstaller_cmd = (
        f"pyinstaller --onefile --windowed --name BarcodeSystem "
        f"--add-data 'templates:templates' "
        f"--add-data 'static:static' "
        f"app.py"
    )
    
    result = run_command(pyinstaller_cmd, cwd=project_root)
    
    if result and result.returncode == 0:
        print("\n打包成功！")
        
        # 复制数据库文件
        print("复制数据库文件...")
        database_files = ['order_system.db']
        for db_file in database_files:
            src_db = os.path.join(project_root, db_file)
            if os.path.exists(src_db):
                dst_db = os.path.join(dist_dir, db_file)
                shutil.copy2(src_db, dst_db)
                print(f"复制 {db_file} 到 dist 目录")
            else:
                print(f"警告：数据库文件 {db_file} 不存在")
        
        # 创建macOS一键运行脚本
        print("创建macOS一键运行脚本...")
        run_script_path = os.path.join(dist_dir, 'run_barcode_system.sh')
        
        with open(run_script_path, 'w') as f:
            f.write('''#!/bin/bash

# 条码系统一键运行脚本 (macOS)

echo "===================================="
echo "条码系统启动脚本"
echo "===================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查可执行文件是否存在
if [ ! -f "$SCRIPT_DIR/BarcodeSystem" ]; then
    echo "错误：BarcodeSystem可执行文件不存在！"
    exit 1
fi

# 检查数据库文件是否存在
if [ ! -f "$SCRIPT_DIR/order_system.db" ]; then
    echo "警告：order_system.db数据库文件不存在，系统将自动创建"
fi

echo "正在启动条码系统..."
echo "系统将在 http://localhost:5001 上运行"
echo "按 Ctrl+C 停止服务"
echo "===================================="

# 进入应用目录
cd "$SCRIPT_DIR"

# 启动系统
./BarcodeSystem
''')
        
        # 设置脚本执行权限
        os.chmod(run_script_path, 0o755)
        
        # 创建DMG打包脚本（可选）
        print("创建DMG打包脚本...")
        dmg_script_path = os.path.join(dist_dir, 'create_dmg.sh')
        
        with open(dmg_script_path, 'w') as f:
            f.write('''#!/bin/bash

# 创建DMG安装包脚本

echo "创建DMG安装包..."

# 设置变量
APP_NAME="BarcodeSystem"
DMG_NAME="BarcodeSystem-macOS"
VOLUME_NAME="Barcode System"

# 创建临时目录
TMP_DIR=$(mktemp -d)
mkdir -p "$TMP_DIR/$VOLUME_NAME"

# 复制文件
cp -r "$APP_NAME" "$TMP_DIR/$VOLUME_NAME/"
cp "order_system.db" "$TMP_DIR/$VOLUME_NAME/"
cp "run_barcode_system.sh" "$TMP_DIR/$VOLUME_NAME/"

# 创建DMG
hdiutil create -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DIR/$VOLUME_NAME" \
    -ov -format UDZO \
    "$DMG_NAME.dmg"

# 清理临时目录
rm -rf "$TMP_DIR"

echo "DMG安装包创建完成: $DMG_NAME.dmg"
''')
        
        os.chmod(dmg_script_path, 0o755)
        
        print(f"\n打包完成！")
        print(f"可执行文件位置: {os.path.join(dist_dir, 'BarcodeSystem')}")
        print(f"一键运行脚本: {run_script_path}")
        print(f"DMG打包脚本: {dmg_script_path}")
        print("\n使用方法:")
        print(f"1. 进入 dist 目录: cd {dist_dir}")
        print("2. 运行一键脚本: ./run_barcode_system.sh")
        print("3. 在浏览器中访问: http://localhost:5001")
        print("\n创建DMG安装包:")
        print("  ./create_dmg.sh")
    else:
        print("\n打包失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
