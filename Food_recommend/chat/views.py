from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message, Recommendation
from user.models import Post, FavoritePost, Follow
import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
from django.conf import settings

# Create your views here.

@login_required
def chat_room(request):
    return render(request, 'chat/chat_room.html')

@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        
        # 保存用戶消息
        message = Message.objects.create(
            user=request.user,
            content=user_message,
            is_bot_response=False
        )
        
        # 模擬AI回覆 (在實際應用中，這裡會調用AI模型)
        bot_response = f"感謝您的訊息！這是關於'{user_message}'的美食推薦回覆。"
        
        # 保存機器人回覆
        bot_message = Message.objects.create(
            user=request.user,
            content=bot_response,
            is_bot_response=True
        )
        
        return JsonResponse({
            'status': 'success',
            'user_message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M')
            },
            'bot_response': {
                'id': bot_message.id,
                'content': bot_message.content,
                'timestamp': bot_message.timestamp.strftime('%Y-%m-%d %H:%M')
            }
        })
    
    return JsonResponse({'status': 'error', 'message': '方法不允許'}, status=405)

@login_required
def explore(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # 處理已登入用戶的收藏和關注狀態
    if request.user.is_authenticated:
        # 獲取用戶的收藏貼文ID列表
        favorite_post_ids = FavoritePost.objects.filter(
            user=request.user
        ).values_list('post_id', flat=True)
        
        # 獲取用戶關注的用戶ID列表
        following_user_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('followed_id', flat=True)
        
        # 標記哪些貼文已被收藏和哪些用戶已被關注
        for post in posts:
            post.is_favorited = post.id in favorite_post_ids
            post.is_following_author = post.user_id in following_user_ids
    
    return render(request, 'chat/explore.html', {'posts': posts})

@login_required
def home(request):
    return render(request, 'chat/home.html')

@require_POST
@csrf_exempt
def chat_assistant(request):
    """處理聊天助手API請求"""
    try:
        # 解析請求數據
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # 獲取用戶偏好信息
        preferences = data.get('preferences', {})
        favorite_foods = preferences.get('favoriteFoods', 'None')
        food_restrictions = preferences.get('foodRestrictions', 'None')
        
        # 用於與GPT模型構建提示詞的偏好字串
        preference_text = ''
        
        # 只有當有實際偏好時才添加相關提示詞
        if favorite_foods and favorite_foods != 'None':
            preference_text += f"用戶喜愛的食物: {favorite_foods}\n"
        
        if food_restrictions and food_restrictions != 'None':
            preference_text += f"用戶的飲食禁忌: {food_restrictions}\n"
        
        # 構建發送到GPT模型的系統提示詞
        system_prompt = "你是一個專業的美食推薦助手，專精於中華料理和各國美食。請用中文回答用戶的問題，風格要親切、專業而有趣。"
        
        if preference_text:
            system_prompt += "\n請注意以下用戶的飲食偏好，並在推薦時考慮這些因素：\n" + preference_text
        
        # 與OpenAI API交互
        try:
            # 這裡模擬AI助手的回應
            # 如果將來需要接入真實的OpenAI API，可以取消以下注釋並安裝OpenAI包
            """
            # 需要先安裝: pip install openai
            # 然後在settings.py中配置API密鑰
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            assistant_message = response.choices[0].message.content.strip()
            """
            
            # 模擬回應
            if "推薦" in user_message or "建議" in user_message:
                if favorite_foods and favorite_foods != 'None':
                    favorite_foods_list = favorite_foods.split(',')
                    assistant_message = f"根據您喜愛的食物（{favorite_foods}），我推薦您可以嘗試以下美食：\n\n"
                    
                    # 根據用戶喜愛的食物生成推薦
                    if "牛肉" in favorite_foods or "肉" in favorite_foods:
                        assistant_message += "1. 紅燒牛肉麵 - 濃郁的湯底配上軟嫩的牛肉，是台灣的經典美食。\n"
                    if "海鮮" in favorite_foods or "魚" in favorite_foods:
                        if food_restrictions and "海鮮過敏" in food_restrictions:
                            assistant_message += "注意：我看到您的飲食禁忌中提到海鮮過敏，因此不推薦海鮮類食物。\n"
                        else:
                            assistant_message += "1. 清蒸魚 - 保留魚肉原有的鮮美，搭配薑絲和蔥花提香。\n"
                    if "麵" in favorite_foods or "面" in favorite_foods:
                        assistant_message += "2. 炸醬麵 - 經典北方麵食，鹹香可口。\n"
                    if "飯" in favorite_foods or "米" in favorite_foods:
                        assistant_message += "3. 雞肉飯 - 香嫩的雞肉配上油亮的米飯，簡單卻美味。\n"
                    
                    assistant_message += "\n您對這些推薦有興趣嗎？或者您想了解更多其他風格的美食？"
                    
                else:
                    assistant_message = "以下是一些我推薦的美食：\n\n1. 東坡肉 - 入口即化的紅燒肉，甜而不膩。\n2. 宮保雞丁 - 麻辣鮮香，是川菜代表之一。\n3. 蔥油餅 - 酥脆多層次，是受歡迎的街邊小吃。\n\n您有嘗試過這些美食嗎？"
            elif "早餐" in user_message:
                assistant_message = "早餐推薦：\n\n1. 燒餅油條 - 經典的中式早餐組合\n2. 豆漿與蛋餅 - 營養均衡的搭配\n3. 飯糰 - 方便攜帶的早餐選擇\n4. 蘿蔔糕 - 煎至金黃的外皮特別香脆\n\n這些早餐都很適合忙碌的早晨！"
            elif "晚餐" in user_message:
                assistant_message = "晚餐的選擇很多，以下是一些建議：\n\n1. 紅燒獅子頭 - 肉質鮮嫩多汁\n2. 清蒸魚 - 簡單健康的選擇\n3. 麻婆豆腐 - 麻辣下飯\n4. 水煮牛肉 - 鮮香辣爽\n\n您偏好什麼口味的晚餐呢？"
            elif "素食" in user_message or "蔬菜" in user_message:
                assistant_message = "素食美食推薦：\n\n1. 香菇青菜 - 清爽可口\n2. 麻婆豆腐（素食版）- 無肉也美味\n3. 素食炒麵 - 豐富的蔬菜和麵條\n4. 涼拌黃瓜 - 夏日開胃小菜\n\n這些素食料理不僅健康，而且味道絕佳！"
            elif "辣" in user_message or "川菜" in user_message:
                if food_restrictions and "不吃辣" in food_restrictions:
                    assistant_message = "我注意到您的飲食禁忌中提到不吃辣，以下是一些不辣但同樣美味的川菜推薦：\n\n1. 水煮白菜 - 清淡爽口\n2. 蒜泥白肉 - 鮮香可口\n3. 三杯雞 - 香氣十足但不辣\n\n川菜不僅僅有辣，還有很多清淡的選擇！"
                else:
                    assistant_message = "川菜推薦：\n\n1. 麻婆豆腐 - 麻辣鮮香\n2. 水煮魚 - 麻辣鮮嫩\n3. 宮保雞丁 - 香辣可口\n4. 夫妻肺片 - 獨特的麻辣風味\n\n川菜以其獨特的麻辣口味聞名，您偏好哪種辣度？"
            else:
                assistant_message = "感謝您的提問！我是美食推薦小幫手，可以為您推薦各種美食和餐廳。請告訴我您的口味偏好或是您想了解的美食類型，我會給您最適合的推薦。無論是中式、西式、日式料理，或是特定的料理方式，我都很樂意為您提供建議！"
                
            # 存儲消息（如果需要）
            if request.user.is_authenticated:
                Message.objects.create(
                    user=request.user,
                    content=user_message,
                    is_bot_response=False
                )
                
                Message.objects.create(
                    user=request.user,
                    content=assistant_message,
                    is_bot_response=True
                )
            
            return JsonResponse({
                'status': 'success',
                'message': assistant_message
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'與AI模型通訊時出錯: {str(e)}'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'處理請求時出錯: {str(e)}'
        }, status=400)

def about(request):
    """關於頁面視圖"""
    return render(request, 'chat/about.html')
