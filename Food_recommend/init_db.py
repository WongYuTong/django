import os
import django
import sys
from pathlib import Path

# 將專案目錄添加到Python路徑中
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# 設置Django環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_recommend.settings')
django.setup()

from django.core.files import File
from django.contrib.auth.models import User
from chat.models import Message, Recommendation
from user.models import Profile, Post

def create_default_images():
    """創建默認的靜態圖片目錄和圖片"""
    # 創建目錄
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('media/profile_pics', exist_ok=True)
    os.makedirs('media/post_images', exist_ok=True)
    os.makedirs('media/recommendation_images', exist_ok=True)
    
    # 創建一個簡單的默認頭像
    if not os.path.exists('static/images/default.jpg'):
        print("請創建默認頭像圖片: static/images/default.jpg")
    
    # 創建示例食物圖片
    if not os.path.exists('static/images/food1.jpg'):
        print("請創建示例食物圖片: static/images/food1.jpg")
    
    if not os.path.exists('static/images/food2.jpg'):
        print("請創建示例食物圖片: static/images/food2.jpg")
    
    if not os.path.exists('static/images/default_food.jpg'):
        print("請創建默認食物圖片: static/images/default_food.jpg")

def create_superuser():
    """創建超級用戶"""
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('超級用戶已創建: admin/admin123')
    else:
        print('超級用戶已存在')

def create_test_users():
    """創建測試用戶"""
    for i in range(1, 4):
        username = f'test_user{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=f'test{i}@example.com',
                password='password123'
            )
            profile = Profile.objects.get(user=user)
            profile.bio = f'這是測試用戶{i}的個人簡介'
            profile.save()
            print(f'測試用戶已創建: {username}/password123')
        else:
            print(f'測試用戶已存在: {username}')

def create_sample_posts():
    """創建示例貼文"""
    if User.objects.filter(username='test_user1').exists():
        user = User.objects.get(username='test_user1')
        
        if not Post.objects.filter(user=user, title='美味的台式牛肉麵').exists():
            post = Post.objects.create(
                user=user,
                title='美味的台式牛肉麵',
                content='昨天去了一家新開的台式牛肉麵店，湯頭非常濃郁，牛肉軟嫩多汁，麵條有嚼勁。推薦給大家！'
            )
            print('示例貼文已創建: 美味的台式牛肉麵')
    
    if User.objects.filter(username='test_user2').exists():
        user = User.objects.get(username='test_user2')
        
        if not Post.objects.filter(user=user, title='甜點控必訪的提拉米蘇').exists():
            post = Post.objects.create(
                user=user,
                title='甜點控必訪的提拉米蘇',
                content='這家咖啡店的提拉米蘇真的太棒了！馬斯卡彭起司香濃滑順，咖啡酒香味恰到好處，餅乾軟硬適中。推薦給所有甜點愛好者！'
            )
            print('示例貼文已創建: 甜點控必訪的提拉米蘇')

def create_sample_recommendations():
    """創建示例推薦"""
    if User.objects.filter(username='test_user3').exists():
        user = User.objects.get(username='test_user3')
        
        if not Recommendation.objects.filter(user=user, food_name='日式拉麵').exists():
            recommendation = Recommendation.objects.create(
                user=user,
                food_name='日式拉麵',
                description='這家拉麵店的豚骨湯底熬製超過12小時，湯頭濃郁不膩，叉燒軟嫩多汁，完美搭配彈牙的麵條。絕對值得一試！'
            )
            print('示例推薦已創建: 日式拉麵')
    
    if User.objects.filter(username='test_user1').exists():
        user = User.objects.get(username='test_user1')
        
        if not Recommendation.objects.filter(user=user, food_name='泰式綠咖哩').exists():
            recommendation = Recommendation.objects.create(
                user=user,
                food_name='泰式綠咖哩',
                description='這家泰式餐廳的綠咖哩香辣適中，椰奶香氣十足，搭配雞肉和各種泰式香料，風味絕佳。推薦配泰式香米飯一起享用！'
            )
            print('示例推薦已創建: 泰式綠咖哩')

def create_sample_messages():
    """創建示例聊天訊息"""
    if User.objects.filter(username='test_user2').exists():
        user = User.objects.get(username='test_user2')
        
        if Message.objects.filter(user=user).count() == 0:
            Message.objects.create(
                user=user,
                content='我想找一家台北的日本料理餐廳',
                is_bot_response=False
            )
            
            Message.objects.create(
                user=user,
                content='推薦您前往信義區的「鮨極」，這是一家正統的日本料理餐廳，主廚有20年的經驗，特別推薦他們的季節限定的綜合生魚片和壽司套餐，價格範圍大約1500-3000元，建議提前預約。',
                is_bot_response=True
            )
            
            Message.objects.create(
                user=user,
                content='有便宜一點的選擇嗎？',
                is_bot_response=False
            )
            
            Message.objects.create(
                user=user,
                content='如果您預算較低，可以考慮「丸壽司」，這是一家平價的日本料理店，位於大安區，他們的套餐從500元起，壽司和丼飯都很有水準，特別推薦他們的鮭魚親子丼和綜合壽司套餐。不需要預約，但午晚餐時段可能需要等位。',
                is_bot_response=True
            )
            
            print('示例聊天訊息已創建')

def main():
    """主函數"""
    print('開始初始化數據庫...')
    
    create_default_images()
    create_superuser()
    create_test_users()
    create_sample_posts()
    create_sample_recommendations()
    create_sample_messages()
    
    print('數據庫初始化完成！')

if __name__ == '__main__':
    main() 