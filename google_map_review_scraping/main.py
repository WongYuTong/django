import sys
import logging
from utils import initialize_driver
from scraper import open_url, click_update_results_checkbox, fetch_store_links, fetch_intro_info

sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    url = f"https://www.google.com/maps/search/咖啡廳/"
    driver = initialize_driver()
    try:
        open_url(driver, url)
        click_update_results_checkbox(driver)
        keywords = "咖啡廳"
        store_links = fetch_store_links(driver, keywords, 24.8496199, 121.0237044, 11)
        for store_link in store_links:
            driver.get(store_link)        
            store_name = driver.title.split(' - ')[0]  # 假設店名在標題中
            fetch_intro_info(driver, store_name, keywords)  # 傳入關鍵字參數
            logging.info(f"完成抓取店家 {store_name} 的評論與簡介。")
            driver.back()  # 返回店家列表

    except Exception as e:
        logging.error(f"錯誤：{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 