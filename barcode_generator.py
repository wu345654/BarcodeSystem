import barcode
from barcode.writer import ImageWriter
from barcode.codex import Code128
import os
from datetime import datetime
from typing import List, Tuple, Dict
from database import BarcodeModel, OrderModel

BARCODE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'barcodes')


def ensure_barcode_dir():
    """确保条码图片目录存在"""
    if not os.path.exists(BARCODE_DIR):
        os.makedirs(BARCODE_DIR)


def generate_barcode_number(order_id: int, sequence_no: int) -> str:
    """
    生成条码编号
    格式: 日期(8位) + 订单ID(6位) + 序号(4位)
    例如: 202603030000010001
    """
    date_str = datetime.now().strftime('%Y%m%d')
    order_part = str(order_id).zfill(6)
    seq_part = str(sequence_no).zfill(4)
    return f"{date_str}{order_part}{seq_part}"


def generate_barcode_image(barcode_number: str, filename: str = None) -> str:
    """
    生成条码图片
    返回图片的相对路径
    """
    ensure_barcode_dir()
    
    if filename is None:
        filename = barcode_number
    
    # 生成Code128条码
    code128 = Code128(barcode_number, writer=ImageWriter())
    
    # 设置条码参数
    options = {
        'module_width': 0.4,
        'module_height': 15.0,
        'quiet_zone': 6.5,
        'font_size': 12,
        'text_distance': 5.0,
        'background': 'white',
        'foreground': 'black',
        'write_text': True,
        'text': barcode_number,
    }
    
    filepath = os.path.join(BARCODE_DIR, filename)
    code128.save(filepath, options)
    
    # 返回相对路径
    return f'/static/barcodes/{filename}.png'


def create_barcodes_for_order(order_id: int, quantity: int) -> List[Dict]:
    """
    为订单生成指定数量的条码
    返回生成的条码列表
    """
    barcodes = []
    
    for i in range(1, quantity + 1):
        # 生成条码编号
        barcode_number = generate_barcode_number(order_id, i)
        
        # 生成条码图片
        filename = f"order_{order_id}_seq_{i}"
        image_path = generate_barcode_image(barcode_number, filename)
        
        # 保存到数据库
        barcode_id = BarcodeModel.create(order_id, barcode_number, i)
        
        barcodes.append({
            'id': barcode_id,
            'order_id': order_id,
            'barcode': barcode_number,
            'sequence_no': i,
            'image_path': image_path
        })
    
    return barcodes


def get_barcode_image_path(barcode_number: str) -> str:
    """获取条码图片路径"""
    filename = f"{barcode_number}.png"
    filepath = os.path.join(BARCODE_DIR, filename)
    if os.path.exists(filepath):
        return f'/static/barcodes/{filename}'
    return None


def regenerate_barcode_image(barcode_number: str) -> str:
    """重新生成条码图片"""
    return generate_barcode_image(barcode_number, barcode_number)


if __name__ == '__main__':
    # 测试条码生成
    ensure_barcode_dir()
    test_barcode = generate_barcode_number(1, 1)
    image_path = generate_barcode_image(test_barcode, 'test')
    print(f"测试条码: {test_barcode}")
    print(f"图片路径: {image_path}")
