import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

search_keyword = "Industrial Cartridges Tools"
search_url = f"https://www.alibaba.com/trade/search?SearchText={search_keyword.replace(' ', '+')}"
driver.get(search_url)

time.sleep(3)

def get_product_urls():
    product_urls = []
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "search-card-e-slider__link"))
    )
    
    product_elements = driver.find_elements(By.CLASS_NAME, "search-card-e-slider__link")
    
    for element in product_elements:
        href = element.get_attribute("href")  
        if href:  
            product_urls.append(href)
    
    return product_urls

product_urls = get_product_urls()


print("\nExtracted Product URLs:")
for url in product_urls:
    print(url)

with open('product_urls.json', 'w', encoding='utf-8') as json_file:
    json.dump(product_urls, json_file, ensure_ascii=False, indent=4)

print("\nAll product URLs saved to 'product_urls.json'.")


driver.quit()
