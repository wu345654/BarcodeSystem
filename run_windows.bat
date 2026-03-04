@echo off

REM 订单条码管理系统一键运行脚本
REM 在Windows系统上双击运行此文件

cls
echo =============================================================
echo 订单条码管理系统
 echo =============================================================
echo
echo 正在启动系统...
echo 请稍候...
echo
echo [INFO] 系统启动后将自动打开浏览器访问：
echo http://127.0.0.1:888
echo
echo [INFO] 功能说明：
echo   • 订单管理：创建、编辑、删除订单
echo   • 条码生成：根据订单数量自动生成唯一条码
echo   • 条码扫描：支持扫描枪和手动输入，防止重复扫描
echo   • 扫描记录：查看所有扫描历史
echo   • 统计报表：基于扫描结果生成订单统计信息
echo
echo [WARNING] 注意：
echo   • 首次运行可能需要安装依赖
echo   • 请确保888端口未被占用
echo   • 按 Ctrl+C 停止服务器
echo =============================================================
echo


REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 错误：未找到Python
    echo 请先安装Python 3.11并添加到PATH
    pause
    exit /b 1
)

REM 检查依赖
pip list | findstr "Flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 正在安装依赖...
    pip install flask flask-cors python-barcode Pillow==9.5.0
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败
        pause
        exit /b 1
    )
    echo [OK] 依赖安装完成
    echo
)

REM 运行系统
echo [INFO] 启动服务器...
echo
python start.py

pause