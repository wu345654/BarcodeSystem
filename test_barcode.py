#!/usr/bin/env python3
"""
测试条码生成功能
"""
from database import OrderModel
from barcode_generator import create_barcodes_for_order, generate_barcode_image
import os

# 测试1：创建订单并生成条码
print("测试1：创建订单并生成条码")
print("=" * 60)

# 创建测试订单
order_id = OrderModel.create(
    work_tag="测试工程名称",
    name="测试订单", 
    product="测试产品",
    quantity=2
)

print(f"创建订单 ID: {order_id}")

# 生成条码
barcodes = create_barcodes_for_order(order_id, 2)

print(f"生成条码数量: {len(barcodes)}")
for barcode in barcodes:
    print(f"条码: {barcode['barcode']}, 路径: {barcode['image_path']}")

# 测试2：检查条码图片是否存在
print("\n测试2：检查条码图片是否存在")
print("=" * 60)

for barcode in barcodes:
    image_file = barcode['image_path'].replace('/static/barcodes/', 'static/barcodes/')
    if os.path.exists(image_file):
        print(f"[OK] 条码图片存在: {image_file}")
    else:
        print(f"[ERROR] 条码图片不存在: {image_file}")

# 测试3：测试条码图片路径
print("\n测试3：测试条码图片路径")
print("=" * 60)

print("访问路径示例:")
for barcode in barcodes:
    print(f"http://127.0.0.1:8080{barcode['image_path']}")

print("\n测试完成！")
