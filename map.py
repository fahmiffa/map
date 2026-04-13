from playwright.sync_api import sync_playwright
import time
import csv

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ubah ke True kalau mau tanpa UI
        page = browser.new_page()

        keyword = input("Babershop Brebes")

        page.goto(f"https://www.google.com/maps/search/{keyword}")
        time.sleep(5)

        # Scroll sidebar
        for _ in range(10):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        # Ambil semua hasil
        places = page.locator('//div[@role="article"]')
        count = places.count()

        print(f"Total ditemukan: {count}")

        results = []

        for i in range(min(count, 20)):  # ambil max 20 dulu
            place = places.nth(i)
            place.click()
            time.sleep(3)

            try:
                name = page.locator('//h1').inner_text()
            except:
                name = ""

            try:
                address = page.locator('//button[@data-item-id="address"]').inner_text()
            except:
                address = ""

            try:
                phone = page.locator('//button[contains(@data-item-id,"phone")]').inner_text()
            except:
                phone = "Tidak ada"

            data = {
                "nama": name,
                "alamat": address,
                "telepon": phone
            }

            print(data)
            results.append(data)

        # Simpan ke CSV
        with open("hasil_playwright.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["nama", "alamat", "telepon"])
            writer.writeheader()
            writer.writerows(results)

        browser.close()

if __name__ == "__main__":
    run()