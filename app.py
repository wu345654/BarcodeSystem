from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from database import (
    init_database, OrderModel, BarcodeModel, ScanRecordModel, get_connection
)
from barcode_generator import create_barcodes_for_order, generate_barcode_image

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 初始化数据库
init_database()


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/orders')
def orders_page():
    """订单管理页面"""
    return render_template('orders.html')


@app.route('/scan')
def scan_page():
    """条码扫描页面"""
    return render_template('scan.html')


@app.route('/barcodes/<int:order_id>')
def barcodes_page(order_id):
    """条码列表页面"""
    return render_template('barcodes.html', order_id=order_id)


@app.route('/print-label/<int:order_id>')
def print_label_page(order_id):
    """打印标签页面"""
    return render_template('print_label.html', order_id=order_id)

@app.route('/reports')
def reports_page():
    """统计报表页面"""
    return render_template('reports.html')


@app.route('/scan-records')
def scan_records_page():
    """扫描记录页面"""
    return render_template('scan_records.html')


# ==================== API路由 - 订单管理 ====================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取所有订单"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    orders = OrderModel.get_all(page, page_size)
    # 为每个订单添加扫描统计
    for order in orders:
        stats = BarcodeModel.get_scan_statistics(order['id'])
        order['scan_stats'] = stats
    return jsonify({'success': True, 'data': orders})


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """获取单个订单"""
    order = OrderModel.get_by_id(order_id)
    if order:
        stats = BarcodeModel.get_scan_statistics(order_id)
        order['scan_stats'] = stats
        return jsonify({'success': True, 'data': order})
    return jsonify({'success': False, 'message': '订单不存在'}), 404


@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['work_tag', 'name', 'product']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'{field} 为必填字段'}), 400
    
    try:
        # 创建订单
        order_id = OrderModel.create(
            work_tag=data['work_tag'],
            name=data['name'],
            product=data['product'],
            color=data.get('color'),
            drawing_no=data.get('drawing_no'),
            quantity=data.get('quantity', 1)
        )
        
        # 生成条码
        quantity = data.get('quantity', 1)
        barcodes = create_barcodes_for_order(order_id, quantity)
        
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {
                'order_id': order_id,
                'barcodes_count': len(barcodes)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """更新订单"""
    data = request.get_json()
    
    # 检查订单是否存在
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    try:
        success = OrderModel.update(order_id, **data)
        if success:
            return jsonify({'success': True, 'message': '订单更新成功'})
        return jsonify({'success': False, 'message': '更新失败'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """删除订单"""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    try:
        success = OrderModel.delete(order_id)
        if success:
            return jsonify({'success': True, 'message': '订单删除成功'})
        return jsonify({'success': False, 'message': '删除失败'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/orders/search', methods=['GET'])
def search_orders():
    """搜索订单"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'success': False, 'message': '请输入搜索关键词'}), 400
    
    orders = OrderModel.search(keyword)
    for order in orders:
        stats = BarcodeModel.get_scan_statistics(order['id'])
        order['scan_stats'] = stats
    return jsonify({'success': True, 'data': orders})


# ==================== API路由 - 条码管理 ====================

@app.route('/api/orders/<int:order_id>/barcodes', methods=['GET'])
def get_barcodes(order_id):
    """获取订单的所有条码"""
    order = OrderModel.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': '订单不存在'}), 404
    
    barcodes = BarcodeModel.get_by_order(order_id)
    # 添加图片路径
    for barcode in barcodes:
        barcode['image_path'] = f"/static/barcodes/order_{order_id}_seq_{barcode['sequence_no']}.png"
    
    return jsonify({
        'success': True,
        'data': {
            'order': order,
            'barcodes': barcodes
        }
    })


@app.route('/api/barcodes/<barcode>', methods=['GET'])
def get_barcode(barcode):
    """根据条码值获取条码信息"""
    barcode_info = BarcodeModel.get_by_barcode(barcode)
    if barcode_info:
        order = OrderModel.get_by_id(barcode_info['order_id'])
        barcode_info['order'] = order
        barcode_info['image_path'] = f"/static/barcodes/{barcode}.png"
        return jsonify({'success': True, 'data': barcode_info})
    return jsonify({'success': False, 'message': '条码不存在'}), 404


# ==================== API路由 - 扫描功能 ====================

@app.route('/api/scan', methods=['POST'])
def scan_barcode():
    """
    扫描条码
    检查条码是否已扫描，防止重复扫描
    """
    data = request.get_json()
    barcode_value = data.get('barcode')
    scanned_by = data.get('scanned_by', '')
    
    if not barcode_value:
        return jsonify({'success': False, 'message': '请输入条码'}), 400
    
    # 查询条码
    barcode_info = BarcodeModel.get_by_barcode(barcode_value)
    
    if not barcode_info:
        # 条码不存在
        ScanRecordModel.create(
            barcode_id=0,
            barcode=barcode_value,
            scan_result='FAILED',
            message='条码不存在',
            scanned_by=scanned_by
        )
        return jsonify({
            'success': False,
            'scan_result': 'NOT_FOUND',
            'message': '条码不存在，请检查条码是否正确'
        }), 404
    
    # 检查是否已扫描
    if barcode_info['is_scanned']:
        # 重复扫描
        ScanRecordModel.create(
            barcode_id=barcode_info['id'],
            barcode=barcode_value,
            scan_result='DUPLICATE',
            message='条码已扫描，不能重复扫描',
            scanned_by=scanned_by
        )
        return jsonify({
            'success': False,
            'scan_result': 'DUPLICATE',
            'message': '⚠️ 该条码已扫描，不能重复扫描！',
            'data': {
                'barcode': barcode_info,
                'order': OrderModel.get_by_id(barcode_info['order_id']),
                'first_scanned_at': barcode_info['scanned_at'],
                'first_scanned_by': barcode_info['scanned_by']
            }
        }), 409
    
    # 正常扫描 - 标记为已扫描
    BarcodeModel.mark_as_scanned(barcode_info['id'], scanned_by)
    
    # 记录扫描成功
    ScanRecordModel.create(
        barcode_id=barcode_info['id'],
        barcode=barcode_value,
        scan_result='SUCCESS',
        message='扫描成功',
        scanned_by=scanned_by
    )
    
    # 获取订单信息
    order = OrderModel.get_by_id(barcode_info['order_id'])
    
    return jsonify({
        'success': True,
        'scan_result': 'SUCCESS',
        'message': '✅ 扫描成功！',
        'data': {
            'barcode': barcode_info,
            'order': order
        }
    })


@app.route('/api/scan-records', methods=['GET'])
def get_scan_records():
    """获取扫描记录"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    limit = request.args.get('limit', 500, type=int)  # 保持向后兼容
    
    if page and page_size:
        records = ScanRecordModel.get_all(page, page_size)
    else:
        records = ScanRecordModel.get_all(None, None, limit)
    
    return jsonify({'success': True, 'data': records})


# ==================== 静态文件服务 ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory(app.static_folder, filename)


@app.route('/mic/<path:filename>')
def serve_mic(filename):
    """提供音频文件"""
    mic_dir = os.path.join(os.path.dirname(__file__), 'mic')
    return send_from_directory(mic_dir, filename)


# ==================== 统计信息 ====================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取系统统计信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 订单总数
    cursor.execute('SELECT COUNT(*) as count FROM orders')
    total_orders = cursor.fetchone()['count']
    
    # 条码总数
    cursor.execute('SELECT COUNT(*) as count FROM barcodes')
    total_barcodes = cursor.fetchone()['count']
    
    # 已扫描条码数
    cursor.execute('SELECT COUNT(*) as count FROM barcodes WHERE is_scanned = 1')
    scanned_barcodes = cursor.fetchone()['count']
    
    # 今日扫描数
    cursor.execute('''
        SELECT COUNT(*) as count FROM scan_records 
        WHERE date(scanned_at) = date('now')
    ''')
    today_scans = cursor.fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'success': True,
        'data': {
            'total_orders': total_orders,
            'total_barcodes': total_barcodes,
            'scanned_barcodes': scanned_barcodes,
            'unscanned_barcodes': total_barcodes - scanned_barcodes,
            'today_scans': today_scans
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
