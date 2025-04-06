from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import traceback

def create_default_avatar():
    """創建一個簡單的默認頭像圖片"""
    try:
        img_size = 300
        img = Image.new('RGB', (img_size, img_size), color=(70, 130, 180))  # 深藍色背景
        draw = ImageDraw.Draw(img)
        
        # 繪製圓形
        draw.ellipse((50, 50, img_size-50, img_size-50), fill=(255, 255, 255))  # 白色圓形
        
        # 繪製簡單的人形
        draw.ellipse((img_size//2-30, 110, img_size//2+30, 170), fill=(70, 130, 180))  # 頭部
        draw.rectangle((img_size//2-40, 170, img_size//2+40, 240), fill=(70, 130, 180))  # 身體
        
        # 儲存圖片
        output_path = 'static/images/default.jpg'
        img.save(output_path)
        print(f'默認頭像已創建: {output_path}')
        return True
    except Exception as e:
        print(f"創建默認頭像時出錯: {e}")
        traceback.print_exc()
        return False

def create_food_images():
    """創建美食圖片"""
    results = []
    try:
        # 牛肉麵圖片
        img_size = (500, 400)
        img1 = Image.new('RGB', img_size, color=(200, 150, 100))  # 棕色背景
        draw1 = ImageDraw.Draw(img1)
        
        # 繪製麵條和牛肉圖案
        draw1.ellipse((150, 100, 350, 300), fill=(220, 180, 130))  # 碗
        draw1.line([(180, 150), (320, 240)], fill=(240, 220, 180), width=10)  # 麵條
        draw1.line([(200, 200), (300, 180)], fill=(240, 220, 180), width=10)  # 麵條
        draw1.line([(220, 180), (280, 220)], fill=(240, 220, 180), width=10)  # 麵條
        draw1.rectangle((220, 160, 260, 190), fill=(120, 60, 40))  # 牛肉
        draw1.rectangle((270, 190, 310, 220), fill=(120, 60, 40))  # 牛肉
        
        draw1.text((200, 50), "Beef Noodle", fill=(255, 255, 255))
        
        output_path = 'static/images/food1.jpg'
        img1.save(output_path)
        print(f'美食圖片已創建: {output_path}')
        results.append(True)
    except Exception as e:
        print(f"創建牛肉麵圖片時出錯: {e}")
        traceback.print_exc()
        results.append(False)
    
    try:
        # 甜點圖片
        img_size = (500, 400)
        img2 = Image.new('RGB', img_size, color=(240, 220, 210))  # 淺棕色背景
        draw2 = ImageDraw.Draw(img2)
        
        # 繪製提拉米蘇圖案
        draw2.rectangle((150, 150, 350, 300), fill=(80, 50, 20))  # 巧克力層
        draw2.rectangle((150, 100, 350, 150), fill=(255, 240, 220))  # 馬斯卡彭起司層
        draw2.rectangle((150, 200, 350, 250), fill=(255, 240, 220))  # 馬斯卡彭起司層
        
        # 灑上可可粉
        for i in range(50):
            x = 150 + (i * 4)
            draw2.point((x, 100), fill=(60, 30, 10))
            draw2.point((x+2, 102), fill=(60, 30, 10))
        
        draw2.text((180, 50), "Tiramisu", fill=(60, 30, 10))
        
        output_path = 'static/images/food2.jpg'
        img2.save(output_path)
        print(f'美食圖片已創建: {output_path}')
        results.append(True)
    except Exception as e:
        print(f"創建提拉米蘇圖片時出錯: {e}")
        traceback.print_exc()
        results.append(False)
    
    try:
        # 默認食物圖片
        img_size = (500, 400)
        img3 = Image.new('RGB', img_size, color=(230, 230, 230))  # 灰色背景
        draw3 = ImageDraw.Draw(img3)
        
        # 繪製一個簡單的盤子和食物圖案
        draw3.ellipse((100, 100, 400, 300), fill=(255, 255, 255))  # 盤子
        draw3.rectangle((200, 150, 300, 220), fill=(200, 150, 100))  # 主菜
        draw3.ellipse((180, 180, 220, 220), fill=(100, 180, 100))  # 蔬菜
        draw3.ellipse((280, 180, 320, 220), fill=(180, 100, 100))  # 配菜
        
        draw3.text((180, 50), "Food", fill=(80, 80, 80))
        
        output_path = 'static/images/default_food.jpg'
        img3.save(output_path)
        print(f'美食圖片已創建: {output_path}')
        results.append(True)
    except Exception as e:
        print(f"創建默認食物圖片時出錯: {e}")
        traceback.print_exc()
        results.append(False)
    
    return all(results)

def main():
    try:
        # 確保目錄存在
        os.makedirs('static/images', exist_ok=True)
        
        # 創建圖片
        avatar_result = create_default_avatar()
        food_result = create_food_images()
        
        if avatar_result and food_result:
            print('所有示例圖片創建完成！')
        else:
            print('部分圖片創建失敗，請檢查錯誤訊息')
    except Exception as e:
        print(f"執行過程中出錯: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main() 