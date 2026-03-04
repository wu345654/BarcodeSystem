#!/usr/bin/env python3
"""
订单条码管理系统入口点
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行启动脚本
from start import main

if __name__ == '__main__':
    main()
