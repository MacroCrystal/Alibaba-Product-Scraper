import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from selenium.common.exceptions import TimeoutException

def sanitize_filename(url):
    sanitized_url = re.sub(r'[<>:"/\\|?*]', '_', url)
    sanitized_url = re.sub(r'\s+', '_', sanitized_url)
    return sanitized_url

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

with open('product_urls.json', 'r', encoding='utf-8') as json_file:
    product_urls = json.load(json_file)

url_limit = 45  # Change this value as needed
all_product_data = []

for url_count, url in enumerate(product_urls):
    if url_count >= url_limit:
        break
    
    print(f"Processing URL: {url}")
    
    retry_count = 0
    while retry_count < 3:  # Retry 3 times for each URL
        try:
            driver.get(url)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "attribute-list"))
            )

            attribute_dict = {}

            try:
                show_more_button = driver.find_element(By.CLASS_NAME, "more-bg")
                print("Clicking 'Show More' to reveal additional attributes.")
                show_more_button.click()
                time.sleep(2)

                WebDriverWait(driver, 60).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "attribute-item"))
                )
                print("Additional attributes revealed.")
            except:
                print("No 'Show More' button found, proceeding with the available attributes.")

            attribute_lists = driver.find_elements(By.CLASS_NAME, "attribute-list")
            
            for idx, attribute_list in enumerate(attribute_lists):
                attribute_items = attribute_list.find_elements(By.CLASS_NAME, "attribute-item")
                print(f"Processing Attribute List {idx + 1} with {len(attribute_items)} attribute-items.")
                
                for i, item in enumerate(attribute_items):
                    try:
                        label_element = item.find_element(By.CLASS_NAME, "left")
                        value_element = item.find_element(By.CLASS_NAME, "right")
                        
                        if label_element:
                            label_html = label_element.get_attribute('innerHTML')
                            value_html = value_element.get_attribute('innerHTML') if value_element else "N/A"
                            label_clean = label_html.replace('<span>', '').replace('</span>', '')
                            value_clean = value_html.replace('<span>', '').replace('</span>', '') if value_html else "N/A"
                            
                            if label_clean and value_clean:
                                attribute_dict[label_clean] = value_clean
                                print(f"Label: {label_clean} - Value: {value_clean}")
                    except Exception as e:
                        print(f"Error processing an attribute item: {e}")
            
            all_product_data.append({'URL': url, **attribute_dict})
            break  # Exit the retry loop after successful processing
        
        except TimeoutException as e:
            print(f"Timeout occurred for URL: {url}. Retrying... ({retry_count + 1}/3)")
            retry_count += 1
            time.sleep(5)  # Wait before retrying

        except Exception as e:
            print(f"An error occurred for URL {url}: {e}")
            break  # Exit if an unexpected error occurs

    if retry_count == 3:
        print(f"Failed to process {url} after 3 retries, skipping this URL.")

time.sleep(3)  # Optional: add a small delay between each URL request to prevent being blocked

df = pd.DataFrame(all_product_data)
df.to_excel('all_product_data.xlsx', index=False, engine='openpyxl')

print(f"All product data has been saved to all_product_data.xlsx")

driver.quit()
