#!/usr/bin/env python3
"""
订单条码管理系统启动脚本
"""
import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """自动打开浏览器"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """主函数"""
    print("=" * 60)
    print("📦 订单条码管理系统")
    print("=" * 60)
    print()
    
    # 检查依赖
    try:
        from flask import Flask
        from flask_cors import CORS
        import barcode
        from PIL import Image
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请先安装依赖: pip install -r requirements.txt")
        sys.exit(1)
    
    # 初始化数据库
    print("🔄 初始化数据库...")
    from database import init_database
    init_database()
    print("✅ 数据库初始化完成")
    print()
    
    # 创建静态目录
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'barcodes')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"✅ 创建条码目录: {static_dir}")
    
    print()
    print("🚀 启动服务器...")
    print("📍 访问地址: http://127.0.0.1:888")
    print()
    print("功能说明:")
    print("  • 订单管理: 创建、编辑、删除订单")
    print("  • 条码生成: 根据订单数量自动生成唯一条码")
    print("  • 条码扫描: 支持扫描枪和手动输入，防止重复扫描")
    print("  • 扫描记录: 查看所有扫描历史")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    # 自动打开浏览器
    def open_browser_888():
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:888')
    Timer(1, open_browser_888).start()
    
def main():
    # 启动Flask应用
    from app import app
    app.run(debug=True, host='0.0.0.0', port=888, use_reloader=False)

if __name__ == '__main__':
    main()
