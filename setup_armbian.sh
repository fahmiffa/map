#!/bin/bash

echo "==============================================="
echo "  Setup Maps Scraper Pro untuk Armbian Server  "
echo "==============================================="

# 1. Update sistem dan install Chromium OS (Wajib untuk ARM architecture)
echo "[1/4] Menginstall Chromium bawaan sistem (mendukung ARM)..."
sudo apt update
sudo apt install -y chromium chromium-browser xvfb python3-venv python3-pip

# 2. Setup Virtual Environment
echo "[2/4] Menjalankan Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
echo "[3/4] Menginstall Library Python..."
pip install -r requirements.txt

# 4. Beri tahu Playwright untuk tidak mendownload browser-nya sendiri
# karena sering tidak kompatibel dengan arsitektur processor ARM
export PLAYWRIGHT_BROWSERS_PATH=0

echo "✅ Setup Selesai!"
echo " "
echo "Untuk menjalankan aplikasi di background pada server Anda, gunakan perintah:"
echo "source venv/bin/activate"
echo "gunicorn --bind 0.0.0.0:5000 app:app --timeout 120"
