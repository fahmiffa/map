import os
import requests
import re
from playwright.sync_api import sync_playwright
import time

def check_whatsapp(phone):
    if not phone or phone == "N/A":
        return "N/A"
    
    # Clean number
    clean_number = re.sub(r'\D', '', phone)
    if clean_number.startswith('0'):
        clean_number = '62' + clean_number[1:]
        
    url = "https://broadcast.qlabcode.com/api/number"
    payload = {
        "number": "085640431181",
        "to": clean_number
    }
    
    try:
        # User defined API endpoint
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code == 200:
            res_data = response.json()
            # If API returns success status
            if res_data.get('status') == True:
                return "Valid"
            else:
                return "Invalid"
    except:
        return "Error"
    
    return "Unknown"

def scrape_maps(category, location, limit=10):
    keyword = f"{category} {location}"
    results = []
    with sync_playwright() as p:
        # Determine executable path for Linux (Armbian)
        browser_path = None
        if os.name != 'nt':
            # Common paths for chromium on Debian/Ubuntu/Armbian
            potential_paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser"]
            for path in potential_paths:
                if os.path.exists(path):
                    browser_path = path
                    break

        # Launch browser - headless for server use
        browser = p.chromium.launch(
            headless=True,
            executable_path=browser_path
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Navigate to Google Maps
        page.goto(f"https://www.google.com/maps/search/{keyword}")
        
        # Wait for the sidebar to load
        try:
            page.wait_for_selector('//div[@role="article"]', timeout=10000)
        except:
            browser.close()
            return []

        # Scroll sidebar to load more results dynamically based on limit
        prev_count = 0
        scroll_attempts = 0
        max_attempts = 15 # Safety limit to avoid infinite loops

        while True:
            places = page.locator('//div[@role="article"]')
            current_count = places.count()
            
            # Hover over a result to ensure scroll focus
            if current_count > 0:
                try:
                    places.nth(min(current_count - 1, 0)).hover()
                except: pass
            
            if current_count >= limit or (current_count == prev_count and scroll_attempts > 5):
                break
            
            # Scroll down the sidebar
            # Target the sidebar container if possible, or just wheel on the page
            page.mouse.wheel(0, 4000)
            time.sleep(2) # Wait for results to load
            
            if current_count == prev_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0 # Reset if we found new items
                
            prev_count = current_count
            if scroll_attempts > max_attempts:
                break

        # Get final results count
        places = page.locator('//div[@role="article"]')
        count = places.count()
        actual_limit = min(count, limit)

        for i in range(actual_limit):
            try:
                place = places.nth(i)
                # First, try to get name from the search result item (reliable and fast)
                name = ""
                try:
                    # fontHeadlineSmall or qBF1Pd are common classes for business names in the list
                    name_elem = place.locator('.fontHeadlineSmall, .qBF1Pd').first
                    if name_elem.count() > 0:
                        name = name_elem.inner_text()
                except: pass

                # Fallback: Click and look for the name in the detail panel with a specific class
                if not name or name.lower() == "hasil":
                    place.click()
                    time.sleep(2) 
                    try:
                        # DUwDvf is the standard class for business name in the detail panel
                        detail_name = page.locator('h1.DUwDvf').first
                        if detail_name.is_visible():
                            name = detail_name.inner_text()
                    except: pass

                # Final fallback for name
                if not name or name.lower() == "hasil":
                    try:
                        name = place.get_attribute('aria-label')
                    except: pass
                else:
                    # Always click to ensure address/phone are loaded in the panel
                    place.click()
                    time.sleep(1)

                address = "N/A"
                try:
                    addr_elem = page.locator('//button[@data-item-id="address"]').first
                    if addr_elem.is_visible():
                        address = addr_elem.inner_text()
                        # Hapus ikon unicode dan newline
                        address = re.sub(r'[\ue000-\uf8ff]', '', address).replace('\n', ' ').strip()
                except: pass

                phone = "N/A"
                try:
                    phone_elem = page.locator('//button[contains(@data-item-id,"phone")]').first
                    if phone_elem.is_visible():
                        phone = phone_elem.inner_text()
                        # Hapus ikon unicode dan newline
                        phone = re.sub(r'[\ue000-\uf8ff]', '', phone).replace('\n', '').strip()
                except: pass

                if name:
                    wa_status = check_whatsapp(phone)
                    data = {
                        "id": i + 1,
                        "nama": name,
                        "alamat": address,
                        "telepon": phone,
                        "wa_status": wa_status
                    }
                    results.append(data)
            except Exception as e:
                print(f"Error scraping item {i}: {e}")
                continue

        browser.close()
    return results
