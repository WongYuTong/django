from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'bio', 'favorite_foods', 'food_restrictions']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': '請簡短介紹自己...'}),
            'favorite_foods': forms.TextInput(attrs={'placeholder': '例如：牛肉麵, 滷肉飯, 壽司'}),
            'food_restrictions': forms.TextInput(attrs={'placeholder': '例如：海鮮過敏, 不吃辣, 素食者'})
        }
        labels = {
            'profile_pic': '個人頭像',
            'bio': '自我介紹',
            'favorite_foods': '喜愛的食物',
            'food_restrictions': '飲食禁忌'
        }
        
class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '請輸入標題'}),
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': '分享您的美食經驗...'})
        }
        labels = {
            'title': '標題',
            'content': '內容',
            'image': '圖片'
        } 