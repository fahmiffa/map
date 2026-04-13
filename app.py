from flask import Flask, render_template, request, jsonify, send_file
from scraper import scrape_maps
import csv
import os
import io

app = Flask(__name__)

# Temporary storage for the last run results
last_results = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    global last_results
    data = request.json
    category = data.get('category', '')
    location = data.get('location', '')
    limit = int(data.get('limit', 10))
    
    if not category or not location:
        return jsonify({"error": "Category and Location are required"}), 400
    
    try:
        results = scrape_maps(category, location, limit)
        last_results = results
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download')
def download():
    global last_results
    if not last_results:
        return "No data to download", 400
    
    proxy = io.StringIO()
    writer = csv.DictWriter(proxy, fieldnames=["id", "nama", "alamat", "telepon", "wa_status"])
    writer.writeheader()
    writer.writerows(last_results)
    
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()
    
    return send_file(
        mem,
        as_attachment=True,
        download_name='google_maps_results.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
