import logging
import csv
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def initialize_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(800, 600)
    return driver

def sanitize_filename(name):
    """移除不合法的檔名字元"""
    return re.sub(r'[<>:"/\\|?*]', '', name)

def get_next_id(csv_file, keyword=''):
    """获取下一个可用的ID，并将关键字编码加入"""
    try:
        # 将关键字转换为简单编码（使用第1个字的unicode编码的前3位）
        keyword_code = ''
        if keyword:
            # 取第1个字符
            chars = keyword[:1]
            # 对字符取unicode编码的前3位
            keyword_code = ''.join([str(ord(c))[:3] for c in chars])
        
        if not os.path.exists(csv_file):
            return f"{keyword_code}00001" if keyword_code else "00001"
            
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过标题行
            
            # 获取所有ID
            ids = [row[0] for row in reader if row]
            
            if not ids:
                return f"{keyword_code}00001" if keyword_code else "00001"
            
            # 过滤出与当前关键字相同编码的ID
            if keyword_code:
                matching_ids = [id_str for id_str in ids if id_str.startswith(keyword_code)]
                if matching_ids:
                    # 获取最大数字并加1
                    max_num = max(int(id_str[len(keyword_code):]) for id_str in matching_ids)
                    return f"{keyword_code}{str(max_num + 1).zfill(5)}"
                else:
                    return f"{keyword_code}00001"
            else:
                # 如果没有关键字，使用纯数字ID
                numeric_ids = [int(id_str) for id_str in ids if id_str.isdigit()]
                return str(max(numeric_ids) + 1 if numeric_ids else 1).zfill(5)
                
    except Exception as e:
        logging.error(f"获取下一个ID时出错：{e}")
        return f"{keyword_code}00001" if keyword_code else "00001"

def format_intro_content(intro_text):
    """格式化簡介內容為字典格式"""
    try:
        intro_dict = {}
        
        for section in intro_text:
            section = re.sub(r'\\u\w+', '', section)
            section = re.sub(r'[\ue5ca\ue033]', '', section)
            
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            if lines:
                title = lines[0]
                items = [item for item in lines[1:] if item]
                if items:
                    intro_dict[title] = items

        formatted_parts = []
        for title, items in intro_dict.items():
            items = list(dict.fromkeys(items))
            formatted_parts.append(f"{title}：[{', '.join(items)}]")

        return ", ".join(formatted_parts)
    except Exception as e:
        logging.error(f"格式化簡介內容時出錯：{e}")
        return " , ".join(intro_text) 