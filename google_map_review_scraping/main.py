import sys
import logging
import json
from utils import initialize_driver
from scraper import open_url, click_update_results_checkbox, fetch_store_links, fetch_intro_info
import time
import random
sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    keywords = "火鍋"
    
    # 讀取town.json文件
    try:
        with open('town.json', 'r', encoding='utf-8') as f:
            town_data = json.load(f)
    except FileNotFoundError:
        logging.error("找不到town.json文件")
        return
    except json.JSONDecodeError:
        logging.error("town.json文件格式錯誤")
        return
    
    # 篩選台北市的鄉鎮區
    taipei_districts = []
    for town in town_data:
        if town.get('CountyName') == '臺北市':
            taipei_districts.append({
                'DistrictName': town.get('TownName'),
                'latitude': town.get('latitude'),
                'longitude': town.get('longitude')
            })
    
    # 跳過前六個區域，取剩下的區域
    seen_districts = set()
    remaining_districts = []
    
    # 先記錄前六個區域
    for district in taipei_districts:
        if district['DistrictName'] not in seen_districts and len(seen_districts) < 6:
            seen_districts.add(district['DistrictName'])
    
    # 取得剩下的區域
    for district in taipei_districts:
        if district['DistrictName'] not in seen_districts:
            remaining_districts.append(district)
            seen_districts.add(district['DistrictName'])
    
    logging.info(f"將要抓取以下 {len(remaining_districts)} 個區域的資料：{[d['DistrictName'] for d in remaining_districts]}")
    
    driver = initialize_driver()
    all_store_links = set()  # 使用集合來儲存不重複的店家連結
    
    try:
        # 第一次搜尋時設置更新結果選項
        url = f"https://www.google.com/maps/search/{keywords}"
        open_url(driver, url)
        click_update_results_checkbox(driver)
        time.sleep(1)
        
        # 對每個鄉鎮區進行搜尋
        for district in remaining_districts:
            logging.info(f"開始搜尋 {district['DistrictName']} 的{keywords}店家")
            url = f"https://www.google.com/maps/search/{keywords}"
            open_url(driver, url)
            
            # 獲取該區域的店家連結
            district_links = fetch_store_links(
                driver, 
                keywords,
                district['latitude'],
                district['longitude'],
                15  # 使用更大的縮放級別以獲取更精確的結果
            )
            
            # 將新的連結加入總集合中（自動去除重複項）
            all_store_links.update(district_links)
            logging.info(f"{district['DistrictName']} 新增 {len(district_links)} 個店家，目前共有 {len(all_store_links)} 個不重複店家")
            time.sleep(2)
        
        # 處理所有收集到的店家連結
        for store_link in all_store_links:
            driver.get(store_link)
            store_name = driver.title.split(' - ')[0]
            fetch_intro_info(driver, store_name, keywords)
            logging.info(f"完成抓取店家 {store_name} 的評論與簡介。")
            time.sleep(random.uniform(1, 3))
            
    except Exception as e:
        logging.error(f"錯誤：{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 