#!/usr/bin/env python3
"""
Order Barcode Management System Startup Script
"""
import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Auto open browser"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Main function"""
    print("=" * 60)
    print("Order Barcode Management System")
    print("=" * 60)
    print()
    
    # Check dependencies
    try:
        from flask import Flask
        from flask_cors import CORS
        import barcode
        from PIL import Image
        print("[OK] Dependencies check passed")
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Initialize database
    print("[INFO] Initializing database...")
    from database import init_database
    init_database()
    print("[OK] Database initialized")
    print()
    
    # Create static directory
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'barcodes')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"[OK] Created barcode directory: {static_dir}")
    
    print()
    print("[INFO] Starting server...")
    print("[INFO] Access URL: http://127.0.0.1:888")
    print()
    print("Features:")
    print("  - Order Management: Create, edit, delete orders")
    print("  - Barcode Generation: Auto-generate unique barcodes")
    print("  - Barcode Scanning: Support scanner and manual input")
    print("  - Scan Records: View all scan history")
    print()
    print("Press Ctrl+C to stop server")
    print("=" * 60)
    print()
    
    # Auto open browser
    def open_browser_888():
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:888')
    Timer(1, open_browser_888).start()
    
    # Start Flask app
    from app import app
    app.run(debug=True, host='0.0.0.0', port=888, use_reloader=False)

if __name__ == '__main__':
    main()
