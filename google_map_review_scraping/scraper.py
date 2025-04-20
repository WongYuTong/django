import logging
import time
import random
import csv
import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
from utils import sanitize_filename, get_next_id, format_intro_content

def open_url(driver, url):
    """打開指定的 URL"""
    try:
        driver.get(url)
    except TimeoutException:
        logging.error("打開URL時超時，請檢查網絡連接或URL是否正確。")

def scroll_reviews(driver, store_name, pause_time=3, max_no_change_attempts=5, batch_size=50, max_scrolls=10000, store_id=None):
    """持續滾動評論區直到沒有新評論"""
    try:
        # 如果沒有提供 store_id，則無法追蹤評論數量
        if store_id is None:
            logging.warning("未提供店家編號，無法追蹤評論數量")
            return

        # 讀取現有評論數量和有評論敘述的數量
        review_count = 0
        review_with_text_count = 0
        if os.path.exists("all_reviews.csv"):
            with open("all_reviews.csv", mode='r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                next(reader)  # 跳過標題行
                for row in reader:
                    if row and row[0] == str(store_id):
                        review_count += 1
                        # 檢查評論欄位（索引4）是否有實際內容
                        if row[4] and row[4] != "無評論":
                            review_with_text_count += 1
        
        if review_with_text_count >= 60:
            logging.info(f"店家 {store_name}（編號：{store_id}）已達到60則有效評論上限，跳過抓取")
            # 更新完成狀態
            update_completion_status(store_id, "已完成", f"已達到60則有效評論上限")
            return
            
        if review_count >= 160:
            logging.info(f"店家 {store_name}（編號：{store_id}）已達到160則評論上限，跳過抓取")
            # 更新完成狀態
            update_completion_status(store_id, "已完成", f"已達到160則評論上限")
            return

        scrollable_div = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde'))
        )
        
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        scroll_count = 0
        no_change_attempts = 0
        processed_reviews = set()
        
        while no_change_attempts < max_no_change_attempts and scroll_count < max_scrolls:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            scroll_count += 1
            time.sleep(random.uniform(0.2, 0.3))
            reviews = driver.find_elements(By.CLASS_NAME, 'jftiEf')
            logging.info(f"第 {scroll_count} 次滾動，已加載 {len(reviews)} 條評論。")
            
            new_reviews = [review for review in reviews if review not in processed_reviews]
            if new_reviews:
                # 計算剩餘可抓取的有效評論數量
                remaining_reviews = min(60 - review_with_text_count, 160 - review_count)
                if remaining_reviews <= 0:
                    logging.info(f"店家 {store_name}（編號：{store_id}）已達到評論上限")
                    # 更新完成狀態
                    if review_with_text_count >= 60:
                        update_completion_status(store_id, "已完成", f"已達到60則有效評論上限")
                    else:
                        update_completion_status(store_id, "已完成", f"已達到160則評論上限")
                    break
                
                # 確保不超過限制
                reviews_to_process = min(len(new_reviews[:batch_size]), max(50, remaining_reviews * 2))  # 預估可能有一半是無效評論
                new_text_reviews = fetch_reviews(driver, store_name, new_reviews[:reviews_to_process], store_id)
                processed_reviews.update(new_reviews[:reviews_to_process])
                review_with_text_count += new_text_reviews
                
                if review_with_text_count >= 60:
                    logging.info(f"店家 {store_name}（編號：{store_id}）已達到60則有效評論上限")
                    # 更新完成狀態
                    update_completion_status(store_id, "已完成", f"已達到60則有效評論上限")
                    break
            
            if new_height == last_height:
                no_change_attempts += 1
                logging.info(f"沒有更多新評論，連續未增加評論次數：{no_change_attempts}")
                time.sleep(pause_time)
            else:
                no_change_attempts = 0
                last_height = new_height
            
            if no_change_attempts >= max_no_change_attempts:
                logging.info("連續多次未增加評論，停止滾動。")
                # 更新完成狀態
                update_completion_status(store_id, "已完成", "已抓取所有可用評論")
                break
    except Exception as e:
        logging.error(f"滾動評論區時出錯：{e}")
        logging.error("詳細錯誤信息：", exc_info=True)

def sort_reviews_by_latest(driver):
    """點擊排序按鈕並選擇最新排序"""
    try:
        sort_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="排序評論"]'))
        )
        sort_button.click()
        time.sleep(0.5)
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.fxNQSd[data-index="1"]'))
        ).click()
        time.sleep(1)
        logging.info("已選擇最新排序。")
    except Exception as e:
        logging.error(f"選擇最新排序時錯：{e}")

def fetch_store_links(driver, keyword, latitude, longitude, zoom_level, max_scrolls=10, pause_time=3):
    """使用關鍵字滾動獲取所有店家的鏈接，並儲存店家資訊"""
    store_links = set()  # 使用集合避免重複
    try:
        driver.get(f'https://www.google.com/maps/search/{keyword}/@{latitude},{longitude},{zoom_level}z')
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form:nth-child(2)"))).click()
        except Exception:
            pass

        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        driver.execute_script("""
            var scrollableDiv = arguments[0];
            function scrollWithinElement(scrollableDiv) {
                return new Promise((resolve, reject) => {
                    var totalHeight = 0;
                    var distance = 1000;
                    var scrollDelay = 10000;
                    
                    var timer = setInterval(() => {
                        var scrollHeightBefore = scrollableDiv.scrollHeight;
                        var elementsBefore = scrollableDiv.querySelectorAll('div[jsaction]').length;
                        scrollableDiv.scrollBy(0, distance);
                        totalHeight += distance;

                        if (totalHeight >= scrollHeightBefore) {
                            totalHeight = 0;
                            setTimeout(() => {
                                var scrollHeightAfter = scrollableDiv.scrollHeight;
                                var elementsAfter = scrollableDiv.querySelectorAll('div[jsaction]').length;
                                if (scrollHeightAfter > scrollHeightBefore || elementsAfter > elementsBefore) {
                                    return;
                                } else {
                                    clearInterval(timer);
                                    resolve();
                                }
                            }, scrollDelay);
                        }
                    }, 200);
                });
            }
            return scrollWithinElement(scrollableDiv);
        """, scrollable_div)

        items = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')
        logging.info(f"找到 {len(items)} 個店家。")

        for item in items:
            try:
                # 等待元素可點擊，最多等待2秒
                WebDriverWait(item, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a'))
                )
                # 嘗試更精確的選擇器
                link_element = item.find_element(By.CSS_SELECTOR, 'a[href*="maps/place"]')
                if not link_element:
                    link_element = item.find_element(By.CSS_SELECTOR, 'a')
                
                link = link_element.get_attribute('href')
                if link:
                    store_links.add(link)
                    logging.info(f"成功獲取店家連結: {link[:60]}...")
                else:
                    logging.warning("找到連結元素但無法獲取href屬性")
                
                # # 獲取店名與評價
                # store_name = item.find_element(By.CSS_SELECTOR, 'div.qBF1Pd').text
                # try:
                #     rating = item.find_element(By.CSS_SELECTOR, 'span.MW4etd').text
                # except NoSuchElementException:
                #     rating = "無星數"
                    
                # save_store_info(store_name, rating, latitude, longitude,keyword)  # 存入 CSV
            except TimeoutException:
                logging.warning(f"等待連結元素超時，可能不是有效店家項目")
            except NoSuchElementException as e:
                logging.warning(f"找不到連結元素: {str(e).split('Stacktrace')[0]}")
            except Exception as e:
                logging.error(f"獲取店家鏈接時出錯：{str(e).split('Stacktrace')[0]}")

    except Exception as e:
        logging.error(f"獲取店家鏈接時出錯：{e}")
    return list(store_links)

def open_reviews(driver):
    """點擊評論按鈕"""
    try:
        reviews_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "評論")]'))
        )
        reviews_button.click()
        time.sleep(1)
    except Exception as e:
        logging.error(f"點擊評論按鈕時出錯：{e}")

def fetch_reviews(driver, store_name, reviews, store_id=None):
    """抓取評論並保存到單獨的 CSV 文件和總評論檔案"""
    try:
        all_reviews_file = "all_reviews.csv"
        current_date = time.strftime("%Y-%m-%d")
        new_text_reviews_count = 0  # 追蹤新增的有效評論數量
        
        if not os.path.exists(all_reviews_file):
            with open(all_reviews_file, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["店家編號", "用戶", "評分", "日期", "評論文字", "類別及評分", "評論抓取日期", "用戶評論記錄網址"])
        
        # 讀取已存在的評論
        existing_reviews = []
        if os.path.exists(all_reviews_file):
            with open(all_reviews_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                next(reader)  # 跳過標題行
                for row in reader:
                    if len(row) >= 4:  # 確保行至少有店家編號、用戶名和日期
                        existing_reviews.append({
                            'store_id': row[0],
                            'user_name': row[1],
                            'date': row[3]
                        })

        logging.info(f"共找到 {len(reviews)} 條評論：\n")
        
        for review in reviews:
            try:
                # 先檢查評論是否有全文按鈕
                try:
                    # 先找到评论内容区域
                    try:
                        review_content = review.find_element(By.CLASS_NAME, 'MyEned')
                    except NoSuchElementException:
                        # 如果找不到 MyEned，嘗試找 jJc9Ad
                        review_content = review.find_element(By.CLASS_NAME, 'jJc9Ad')
                        
                    # 在评论内容区域中查找全文按钮
                    full_text_button = review_content.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="顯示更多"]')
                    
                    # 如果找到按鈕，則點擊展開
                    if full_text_button and full_text_button.is_displayed():
                        logging.info("找到全文按鈕，點擊展開...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", full_text_button)
                        full_text_button.click()
                        time.sleep(0.1)
                        # 检查是否需要重试点击，最多重试5次
                        retry_count = 0
                        max_retries = 5
                        while retry_count < max_retries:
                            time.sleep(0.1)
                            try:
                                retry_button = review_content.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="顯示更多"]')
                                if retry_button.is_displayed():
                                    logging.info(f"檢測到全文按鈕仍然存在，第 {retry_count + 1} 次嘗試點擊...")
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", retry_button)
                                    time.sleep(0.1)
                                    retry_button.click()
                                    time.sleep(0.1)
                                    retry_count += 1
                                else:
                                    break  # 按钮不可见，说明已展开成功
                            except NoSuchElementException:
                                break  # 找不到按钮，说明已展开成功
                        
                        if retry_count >= max_retries:
                            logging.info("已達到最大重試次數，停止嘗試點擊全文按鈕")
                except NoSuchElementException:
                    logging.info("未找到全文按鈕或評論內容區域")
                except Exception as e:
                    logging.info(f"處理全文按鈕時出錯: {str(e).split('Stacktrace')[0]}")

                # 獲取用戶信息
                user_name = review.find_element(By.CLASS_NAME, 'd4r55').text
                rating_text = review.find_element(By.CLASS_NAME, 'kvMYJc').get_attribute("aria-label")
                rating = ''.join(filter(str.isdigit, rating_text))
                review_date = review.find_element(By.CLASS_NAME, 'rsqaWe').text
                
                # 獲取用戶評論記錄網址
                user_profile_url = "無評論記錄網址"
                try:
                    user_profile_button = review.find_element(By.CSS_SELECTOR, 'button.al6Kxe')
                    if user_profile_button:
                        user_profile_url = user_profile_button.get_attribute('data-href')
                        logging.info(f"找到用戶評論記錄網址：{user_profile_url}")
                except NoSuchElementException:
                    logging.info("未找到用戶評論記錄網址")
                except Exception as e:
                    logging.error(f"獲取用戶評論記錄網址時出錯：{e}")
                
                # 檢查評論是否已存在
                is_duplicate = any(
                    existing['store_id'] == str(store_id) and
                    existing['user_name'] == user_name and
                    existing['date'] == review_date
                    for existing in existing_reviews
                )
                
                if not is_duplicate:
                    try:
                        # 首先嘗試獲取常規文字評論
                        review_text = "無評論"
                        structured_review_text = "無類別及評分"
                        
                        try:
                            review_text_element = review.find_element(By.CSS_SELECTOR, 'span.wiI7pd')
                            if review_text_element:
                                review_text = review_text_element.text.replace('\n', ' ').strip()
                                logging.info(f"{user_name} 評論文字：{review_text}")
                        except NoSuchElementException:
                            logging.info("未找到文字評論")
                            review_text = "無評論"
                            
                        # 嘗試查找結構化評論
                        try:
                            structured_review = review.find_element(By.CSS_SELECTOR, 'div[jslog="127691"]')
                            if structured_review:
                                structured_review_text = structured_review.text.replace('\n', ' ').strip()
                                logging.info(f"{user_name} 類別及評分：{structured_review_text}")
                        except NoSuchElementException:
                            logging.info("未找到類別及評分")
                            structured_review_text = "無類別及評分"
                            
                    except Exception as e:
                        logging.error(f"處理評論文本時出錯：{e}")
                        review_text = "無評論"
                        structured_review_text = "無類別及評分"

                    # 寫入總評論檔案
                    with open(all_reviews_file, mode='a', newline='', encoding='utf-8-sig') as file:
                        writer = csv.writer(file)
                        writer.writerow([store_id, user_name, rating, review_date, review_text, structured_review_text, current_date, user_profile_url])
                    
                    # 將新評論添加到現有評論列表中（需要三個欄位都相同才判定為重複）
                    existing_reviews.append({
                        'store_id': str(store_id),
                        'user_name': user_name,
                        'date': review_date
                    })
                    
                    # 如果評論不是"無評論"，則計入有文字評論數
                    if review_text != "無評論":
                        new_text_reviews_count += 1
                    
                    logging.info(f"抓取評論: 用戶: {user_name}, 評分: {rating}, 日期: {review_date}, 評論: {review_text}")
                    logging.info('-' * 30)
                else:
                    logging.info(f"評論已存在（店家編號 {store_id}、用戶 {user_name}、日期 {review_date} 都相同），跳過")
            except Exception as e:
                logging.error(f"無法解析評論的部分內容：{e}")

        logging.info(f"本次新增 {len(reviews)} 條評論，其中有含文字的評論 {new_text_reviews_count} 條。")
        return new_text_reviews_count  # 返回新增的有效評論數量
    except Exception as e:
        logging.error(f"抓取評論時出錯：{e}")

def fetch_intro_info(driver, store_name, keyword):
    """抓取店家簡介信息"""
    csv_file = "store_intros.csv"
    try:
        if not os.path.exists(csv_file):
            with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["編號", "店名", "地址", "經緯度", "營業時間", "官方網站", "店家簡述", "簡介", "關鍵字", "星數", "價位", "圖片檔案名稱", "是否已完成"])

        store_brief = "無簡述"
        intro_text = []
        address = "無地址"
        coordinates = "無經緯度"
        business_hours = "無營業時間"
        website = "無官方網站"
        rating = "無星數"
        price_level = "無價位資訊"
        # business_status = ""  # 暫時停用營業狀態
        image_filename = ""
        is_completed = "未完成"  # 預設為未完成

        # 先獲取店家編號，這樣可以用於圖片命名與檢查是否已完成
        next_id = get_next_id(csv_file, keyword)

        # 檢查店家是否已經在資料庫中，且是否已完成抓取
        if os.path.exists(csv_file):
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["編號"] == next_id:
                        if row["是否已完成"] == "已完成":
                            logging.info(f"店家 {store_name}（編號：{next_id}）已完成評論抓取，跳過。")
                            return  # 如果已完成，直接返回，不再處理
                        else:
                            logging.info(f"店家 {store_name}（編號：{next_id}）未完成評論抓取，直接進行評論抓取。")
                            try:
                                open_reviews(driver)
                                sort_reviews_by_latest(driver)
                                scroll_reviews(driver, store_name, pause_time=3, batch_size=50, store_id=next_id)
                                logging.info(f"完成抓取店家 {store_name} 的評論。")
                            except Exception as e:
                                logging.error(f"抓取評論時出錯：{e}")
                            return  # 完成評論抓取後返回

        # 創建圖片資料夾
        img_dir = "img"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        try:
            # 尋找主要圖片元素
            img_element = driver.find_element(By.CSS_SELECTOR, 'img[src*="googleusercontent.com"]')
            if img_element:
                img_url = img_element.get_attribute('src')
                if img_url:
                    # 使用店家編號作為圖片檔案名稱
                    image_filename = f"{next_id}.jpg"
                    img_path = os.path.join(img_dir, image_filename)
                    
                    # 下載圖片
                    try:
                        response = requests.get(img_url)
                        if response.status_code == 200:
                            with open(img_path, 'wb') as f:
                                f.write(response.content)
                            logging.info(f"已保存店家圖片：{image_filename}")
                        else:
                            logging.error(f"下載圖片失敗，狀態碼：{response.status_code}")
                            image_filename = ""
                    except Exception as e:
                        logging.error(f"下載圖片時出錯：{e}")
                        image_filename = ""
        except NoSuchElementException:
            logging.info("未找到店家圖片")

        # try:
        #     status_element = driver.find_element(By.CSS_SELECTOR, 'div.lMbq3e span.fCEvvc span[jslog="75719; mutable:true;"]')
        #     if status_element and status_element.text:
        #         business_status = status_element.text
        #         logging.info(f"找到營業狀態：{business_status}")
        # except NoSuchElementException:
        #     logging.info("未找到營業狀態")

        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-hidden="true"]')
            if rating_element:
                rating = rating_element.text
                logging.info(f"找到店家星數：{rating}")
        except NoSuchElementException:
            logging.info("未找到店家星數")

        # 抓取分類標籤
        category_keywords = set()
        try:
            category_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.DkEaL')
            for button in category_buttons:
                category_text = button.text.strip()
                if category_text:
                    category_keywords.add(category_text)
                    logging.info(f"找到分類標籤：{category_text}")
        except NoSuchElementException:
            logging.info("未找到分類標籤")
        except Exception as e:
            logging.error(f"抓取分類標籤時出錯：{e}")

        try:
            price_element = driver.find_element(By.CSS_SELECTOR, 'span.mgr77e span[aria-label^="價格"]')
            if price_element:
                price_level = price_element.get_attribute('aria-label').replace('價格: ', '')
                logging.info(f"找到店家價位：{price_level}")
        except NoSuchElementException:
            logging.info("未找到店家價位")

        try:
            address_element = driver.find_element(By.CSS_SELECTOR, 'div.Io6YTe.fontBodyMedium')
            if address_element:
                address = address_element.text
                logging.info(f"找到店家地址：{address}")
        except NoSuchElementException:
            logging.info("未找到店家地址")

        try:
            current_url = driver.current_url
            logging.info(f"當前URL：{current_url}")
            coords_match = re.search(r'!3d([\d.]+)!4d([\d.]+)', current_url)
            if coords_match:
                lat, lng = coords_match.groups()
                coordinates = f"{lat},{lng}"
                logging.info(f"找到店家經緯度：{coordinates}")
        except Exception as e:
            logging.error(f"獲取經緯度時出錯：{e}")

        if os.path.exists(csv_file):
            found_duplicate = False
            rows = []
            store_id_to_use = next_id
            is_already_completed = False
            
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if (row['店名'] == store_name and 
                        row['經緯度'] == coordinates and 
                        row['地址'] == address):
                        # 檢查關鍵字是否已存在
                        existing_keywords = set()
                        if row['關鍵字']:
                            existing_keywords = set(row['關鍵字'].split(','))
                        
                        # 添加搜尋關鍵字
                        if keyword not in existing_keywords:
                            existing_keywords.add(keyword)
                        
                        # 添加分類標籤關鍵字
                        existing_keywords.update(category_keywords)
                        
                        # 更新關鍵字欄位
                        row['關鍵字'] = ','.join(sorted(existing_keywords))
                        
                        # 記錄該店家的編號和完成狀態
                        store_id_to_use = row['編號']
                        is_already_completed = row['是否已完成'] == "已完成"
                        found_duplicate = True
                        
                    rows.append(row)
                    
            if found_duplicate:
                # 重寫整個文件以更新關鍵字
                with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                logging.info(f"發現重複店家：{store_name}，已更新關鍵字")
                
                # 如果店家已標記為完成，則跳過
                if is_already_completed:
                    logging.info(f"店家 {store_name}（編號：{store_id_to_use}）已完成評論抓取，跳過。")
                    return
                
                # 如果店家未完成，則繼續抓取評論
                logging.info(f"店家 {store_name}（編號：{store_id_to_use}）未完成評論抓取，繼續抓取評論。")
                try:
                    open_reviews(driver)
                    sort_reviews_by_latest(driver)
                    scroll_reviews(driver, store_name, pause_time=3, batch_size=50, store_id=store_id_to_use)
                    logging.info(f"完成抓取店家 {store_name} 的評論。")
                except Exception as e:
                    logging.error(f"抓取評論時出錯：{e}")
                return
                    
        time.sleep(random.uniform(1.5, 2.5))

        try:
            hours_element = driver.find_element(By.CSS_SELECTOR, 'div[aria-label*="星期"]')
            if hours_element:
                business_hours = hours_element.get_attribute('aria-label')
                business_hours = business_hours.split('. ')[0]
                logging.info(f"找到營業時間：{business_hours}")
        except NoSuchElementException:
            logging.info("未找到營業時間")

        try:
            website_element = driver.find_element(By.CSS_SELECTOR, 'a.CsEnBe[data-item-id="authority"]')
            if website_element:
                website = website_element.get_attribute('href')
                logging.info(f"找到官方網站：{website}")
        except NoSuchElementException:
            logging.info("未找到官方網站")

        try:
            intro_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "簡介")]'))
            )
            intro_button.click()
            time.sleep(1)
        except (NoSuchElementException, TimeoutException):
            logging.info(f"{store_name} 找不到簡介按鈕，跳過...")
            with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow([next_id, store_name, address, coordinates, business_hours, website, "無簡述", "無詳細簡介", keyword, rating, price_level, image_filename, is_completed])
            return

        try:
            hlvsq_element = driver.find_element(By.CSS_SELECTOR, 'div.PbZDve span.HlvSq')
            if hlvsq_element:
                store_brief = hlvsq_element.text
                logging.info(f"找到店家簡短描述：{store_brief}")
        except NoSuchElementException:
            logging.info("未找到店家簡短描述，將繼續抓取其他簡介內容")

        try:
            scrollable_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde'))
            )
            scroll_intro_section(driver, scrollable_div)

            intro_blocks = driver.find_elements(By.CLASS_NAME, 'iP2t7d')
            for block in intro_blocks:
                try:
                    content = block.text.strip()
                    if content:
                        intro_text.append(content)
                except Exception as e:
                    logging.error(f"處理簡介塊時出錯：{e}")

        except TimeoutException:
            logging.info(f"{store_name} 沒有找到簡介內容")

        logging.info(f"簡介內容：{intro_text}")
        formatted_intro = format_intro_content(intro_text) if intro_text else "無詳細簡介"
        
        with open(csv_file, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            # 合併關鍵字
            all_keywords = set([keyword])  # 加入搜尋關鍵字
            all_keywords.update(category_keywords)  # 加入分類標籤關鍵字
            keywords_str = ','.join(sorted(all_keywords))
            
            writer.writerow([next_id, store_name, address, coordinates, business_hours, website, 
                           store_brief, formatted_intro, keywords_str, rating, price_level, 
                           image_filename, is_completed])
            logging.info(f"已保存 {store_name} 的所有信息，編號：{next_id}")
        time.sleep(1)

        try:
            open_reviews(driver)
            sort_reviews_by_latest(driver)
            scroll_reviews(driver, store_name, pause_time=3, batch_size=50, store_id=next_id)
            logging.info(f"完成抓取店家 {store_name} 的評論。")
        except Exception as e:
            logging.error(f"抓取評論時出錯：{e}")
            
    except Exception as e:
        logging.error(f"抓取 {store_name} 信息時出錯：{e}", exc_info=True)

def scroll_intro_section(driver, scrollable_div, max_scrolls=10, max_no_change_attempts=1, pause_time=1):
    """滾動簡介區塊"""
    try:
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        scroll_count = 0
        no_change_attempts = 0

        while no_change_attempts < max_no_change_attempts and scroll_count < max_scrolls:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(random.uniform(0.4, 0.6))
            
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            scroll_count += 1

            logging.info(f"第 {scroll_count} 次滾動，當前高度 {new_height}")

            if new_height == last_height:
                no_change_attempts += 1
                logging.info(f"未加載新內容，連續未變化次數：{no_change_attempts}")
                time.sleep(pause_time)
            else:
                no_change_attempts = 0
                last_height = new_height

            if no_change_attempts >= max_no_change_attempts:
                logging.info("簡介內容已完全加載，停止滾動。")
                break

    except Exception as e:
        logging.error(f"滾動簡介區塊時出錯：{e}", exc_info=True)

def click_update_results_checkbox(driver):
    """點擊 '地圖移動時更新結果' 復選框"""
    try:
        checkbox_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@role="checkbox"]'))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_button)
        checkbox_button.click()
        logging.info("已點擊 '地圖移動時更新結果' 復選框。")
    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"點擊 '地圖移動時更新結果' 復選框時出錯：{e}") 

def update_completion_status(store_id, status, reason=""):
    """更新店家的完成狀態"""
    csv_file = "store_intros.csv"
    if not os.path.exists(csv_file):
        logging.error(f"找不到檔案 {csv_file}，無法更新完成狀態")
        return
        
    try:
        # 讀取原始資料
        rows = []
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            header = next(reader)
            completion_index = header.index("是否已完成") if "是否已完成" in header else -1
            
            if completion_index == -1:
                logging.error("CSV 檔案缺少 '是否已完成' 欄位")
                return
                
            rows.append(header)  # 添加標題行
            
            for row in reader:
                if row and row[0] == str(store_id):
                    row[completion_index] = status
                    logging.info(f"更新店家（編號：{store_id}）狀態為 {status}：{reason}")
                rows.append(row)
        
        # 寫回檔案
        with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            
    except Exception as e:
        logging.error(f"更新完成狀態時出錯：{e}", exc_info=True) 