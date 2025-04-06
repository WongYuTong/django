from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/history/', views.post_history, name='post_history'),
    
    # 新增收藏和追蹤功能的URL
    path('post/<int:post_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('user/<int:user_id>/follow/', views.toggle_follow, name='toggle_follow'),
    path('favorites/', views.favorites, name='favorites'),
    path('followers/', views.followers, name='followers'),
] 