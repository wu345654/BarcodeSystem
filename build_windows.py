#!/usr/bin/env python3
"""
Windows版本打包脚本
在Windows系统上运行此脚本以生成可执行文件
"""
import os
import subprocess
import shutil
import platform

# 检查系统是否为Windows
if platform.system() != 'Windows' and os.name != 'nt':
    print("警告：此脚本在非Windows系统上运行，可能会出现兼容性问题")
    print("建议在Windows系统上运行此脚本")

# 清理旧的构建文件
def clean_build():
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('BarcodeSystem_Windows.spec'):
        os.remove('BarcodeSystem_Windows.spec')
    print("[OK] 清理完成")

# 安装依赖
def install_dependencies():
    print("[INFO] 安装依赖...")
    if os.path.exists('requirements.txt'):
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
    else:
        subprocess.run(['pip', 'install', 'flask', 'flask-cors', 'python-barcode', 'Pillow'], check=True)
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    print("[OK] 依赖安装完成")

# 打包可执行文件
def build_executable():
    print("[INFO] 打包可执行文件...")
    # 根据操作系统选择正确的分隔符
    import sys
    if sys.platform.startswith('win'):
        sep = ';'
    else:
        sep = ':'
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name=BarcodeSystem',
        '--add-data', f'templates{sep}templates',
        '--add-data', f'static{sep}static',
        '--icon=icon.ico',
        'start.py'
    ]
    subprocess.run(cmd, check=True)
    print("[OK] 打包完成")

# 复制数据库文件
def copy_database():
    if os.path.exists('order_system.db'):
        if os.path.exists('dist'):
            shutil.copy('order_system.db', 'dist/')
            print("[OK] 数据库文件复制完成")

# 主函数
def main():
    print("============================================================")
    print("Windows版本打包脚本")
    print("============================================================")
    
    try:
        clean_build()
        install_dependencies()
        build_executable()
        copy_database()
        
        print("\n[SUCCESS] 打包成功！")
        print("可执行文件位置: dist/BarcodeSystem.exe")
        print("\n使用方法:")
        print("1. 双击 dist/BarcodeSystem.exe 运行系统")
        print("2. 系统会自动在浏览器中打开 http://127.0.0.1:888")
    except Exception as e:
        print(f"[ERROR] 打包失败: {e}")

if __name__ == '__main__':
    main()
