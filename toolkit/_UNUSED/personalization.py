import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

def get_facebook_ads_html(url):
    # 1. Setup Chrome options
    options = uc.ChromeOptions()
    options.headless = False  # Set to True if you don't want to see the browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # 2. Launch browser
    driver = uc.Chrome(options=options)

    # 3. Load the Facebook Ads Library page
    url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=rugtomize&search_type=keyword_unordered"
    driver.get(url)

    # 4. Optional: Wait to ensure JS content loads (can increase to 15+ secs for heavy pages)
    time.sleep(12)

    # 5. Scroll down multiple times to load dynamic content
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    # 6. Get full page source *after* JS is rendered
    full_html = driver.page_source

    # 7. Print or save
    print(full_html)

    # 8. Save the html to a file
    with open("facebook_ads_rendered.html", "w", encoding="utf-8") as f:
        f.write(full_html)

    # Optional: Save to a file
    # with open("facebook_ads_rendered.html", "w", encoding="utf-8") as f:
    #     f.write(full_html)

    # 8. Close the browser
    driver.quit()

