from app import app

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    print("\nStarting server on http://127.0.0.1:888")
    app.run(debug=True, host='0.0.0.0', port=888, use_reloader=False)