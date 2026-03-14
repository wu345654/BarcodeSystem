#!/usr/bin/env python3
"""
使用Docker在macOS上打包Linux可执行文件
"""

import os
import sys
import subprocess
import shutil

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
    print("使用Docker打包Linux可执行文件")
    print("========================================")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {project_root}")
    
    # 检查Docker是否安装
    docker_check = run_command("docker --version")
    if not docker_check or docker_check.returncode != 0:
        print("错误：Docker未安装！请先安装Docker。")
        print("安装地址：https://www.docker.com/products/docker-desktop")
        sys.exit(1)
    
    # 清理旧的构建文件
    print("\n清理旧的构建文件...")
    build_dir = os.path.join(project_root, 'build')
    dist_dir = os.path.join(project_root, 'dist')
    
    for dir_path in [build_dir, dist_dir]:
        if os.path.exists(dir_path):
            print(f"删除目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    # 创建Dockerfile
    print("\n创建Dockerfile...")
    dockerfile_path = os.path.join(project_root, 'Dockerfile.build')
    
    with open(dockerfile_path, 'w') as f:
        f.write('''FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pyinstaller

# 复制项目文件
COPY . .

# 使用PyInstaller打包
RUN pyinstaller --onefile --name BarcodeSystem \\
    --add-data 'templates:templates' \\
    --add-data 'static:static' \\
    app.py

# 复制数据库文件
RUN if [ -f order_system.db ]; then cp order_system.db dist/; fi
''')
    
    # 构建Docker镜像
    print("\n构建Docker镜像...")
    docker_build_cmd = "docker build -f Dockerfile.build -t barcodesystem-build ."
    result = run_command(docker_build_cmd, cwd=project_root)
    
    if not result or result.returncode != 0:
        print("\nDocker镜像构建失败！")
        sys.exit(1)
    
    # 运行容器并复制构建结果
    print("\n运行容器并复制构建结果...")
    
    # 创建临时容器
    run_cmd = "docker create --name barcodesystem-temp barcodesystem-build"
    run_result = run_command(run_cmd, cwd=project_root)
    
    if not run_result or run_result.returncode != 0:
        print("\n创建容器失败！")
        sys.exit(1)
    
    # 复制dist目录
    copy_cmd = "docker cp barcodesystem-temp:/app/dist ./"
    copy_result = run_command(copy_cmd, cwd=project_root)
    
    # 清理容器
    cleanup_cmd = "docker rm barcodesystem-temp"
    run_command(cleanup_cmd, cwd=project_root)
    
    # 清理Dockerfile
    if os.path.exists(dockerfile_path):
        os.remove(dockerfile_path)
        print(f"删除临时文件: {dockerfile_path}")
    
    # 清理Docker镜像
    cleanup_image_cmd = "docker rmi barcodesystem-build"
    run_command(cleanup_image_cmd, cwd=project_root)
    
    if copy_result and copy_result.returncode == 0:
        print("\n打包成功！")
        
        # 创建Linux一键运行脚本
        print("创建Linux一键运行脚本...")
        run_script_path = os.path.join(dist_dir, 'run_barcode_system.sh')
        
        with open(run_script_path, 'w') as f:
            f.write('''#!/bin/bash

# 条码系统一键运行脚本 (Linux)

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
echo "系统将在 http://localhost:8888 上运行"
echo "按 Ctrl+C 停止服务"
echo "===================================="

# 进入应用目录
cd "$SCRIPT_DIR"

# 启动系统
./BarcodeSystem
''')
        
        # 设置脚本执行权限
        os.chmod(run_script_path, 0o755)
        
        print(f"\n打包完成！")
        print(f"可执行文件位置: {os.path.join(dist_dir, 'BarcodeSystem')}")
        print(f"一键运行脚本: {run_script_path}")
        print("\n使用方法:")
        print(f"1. 将 dist 目录复制到 Linux 服务器")
        print("2. 进入 dist 目录: cd dist")
        print("3. 运行一键脚本: ./run_barcode_system.sh")
        print("4. 在浏览器中访问: http://localhost:8888")
    else:
        print("\n打包失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
