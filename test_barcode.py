#!/usr/bin/env python3
"""
Test barcode generation function
"""
from database import OrderModel
from barcode_generator import create_barcodes_for_order, generate_barcode_image
import os

# Test 1: Create order and generate barcodes
print("Test 1: Create order and generate barcodes")
print("=" * 60)

# Create test order
order_id = OrderModel.create(
    work_tag="Test Project",
    name="Test Order", 
    product="Test Product",
    quantity=2
)

print(f"Created order ID: {order_id}")

# Generate barcodes
barcodes = create_barcodes_for_order(order_id, 2)

print(f"Generated barcode count: {len(barcodes)}")
for barcode in barcodes:
    print(f"Barcode: {barcode['barcode']}, Path: {barcode['image_path']}")

# Test 2: Check if barcode images exist
print("\nTest 2: Check if barcode images exist")
print("=" * 60)

for barcode in barcodes:
    image_file = barcode['image_path'].replace('/static/barcodes/', 'static/barcodes/')
    if os.path.exists(image_file):
        print(f"[OK] Barcode image exists: {image_file}")
    else:
        print(f"[ERROR] Barcode image not found: {image_file}")

# Test 3: Test barcode image path
print("\nTest 3: Test barcode image path")
print("=" * 60)

print("Access URL examples:")
for barcode in barcodes:
    print(f"http://127.0.0.1:8080{barcode['image_path']}")

print("\nTest completed!")
