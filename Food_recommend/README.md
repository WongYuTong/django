# 美食推薦小幫手

一個基於Django的美食推薦應用，幫助用戶發現和分享美食體驗。

## 功能特點

- 用戶可以與AI聊天，獲取個人化的美食推薦
- 用戶可以創建個人資料和分享美食體驗
- 用戶可以瀏覽和探索其他用戶的美食推薦
- 現代化的用戶界面，包括側邊選單和響應式設計

## 技術棧

- **後端**: Python Django
- **前端**: HTML, CSS, JavaScript, Bootstrap 5
- **數據庫**: SQLite (開發環境)

## 系統需求

- Python 3.8+
- Django 3.2+
- Pillow (用於圖片處理)

## 安裝與設置

1. 克隆存儲庫：

```bash
git clone https://github.com/yourusername/food_recommend.git
cd food_recommend
```

2. 創建虛擬環境並激活：

```bash
python -m venv venv
source venv/bin/activate  # 在Linux/Mac上
venv\Scripts\activate  # 在Windows上
```

3. 安裝依賴：

```bash
pip install -r requirements.txt
```

4. 運行數據庫遷移：

```bash
python manage.py makemigrations
python manage.py migrate
```

5. 創建超級用戶（可選）：

```bash
python manage.py createsuperuser
```

6. 啟動開發服務器：

```bash
python manage.py runserver
```

應用將在 http://127.0.0.1:8000/ 上運行。

## 項目結構

- `food_recommend/`: 主要Django項目設置
- `chat/`: 聊天和美食推薦功能的應用
- `user/`: 用戶管理和個人資料功能的應用
- `templates/`: HTML模板文件
- `static/`: 靜態文件（CSS、JavaScript、圖片）
- `media/`: 用戶上傳的媒體文件

## 未來計劃

- 實現更多的人工智能推薦功能
- 添加美食標籤和分類系統
- 集成地圖以顯示附近的餐廳
- 實現社交功能，如關注其他用戶和點讚功能

## 圖片需求

以下是項目所需的圖片資源：

1. 默認用戶頭像 (`static/images/default.jpg`): 建議尺寸 300x300px
2. 示例美食圖片 (`static/images/food1.jpg`, `static/images/food2.jpg`): 建議尺寸 500x400px
3. Logo圖片 (`static/images/logo.png`): 建議尺寸 200x200px

## 貢獻

歡迎貢獻！請隨時提交問題或拉取請求。 