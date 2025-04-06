from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics', default='default_profile.png')
    bio = models.TextField(blank=True)
    favorite_foods = models.CharField(max_length=200, blank=True, help_text="請列出您喜愛的食物，用逗號分隔")
    food_restrictions = models.CharField(max_length=200, blank=True, help_text="請列出您的飲食禁忌，用逗號分隔")
    
    def __str__(self):
        return f'{self.user.username} Profile'

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class FavoritePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # 確保每個用戶只能收藏同一貼文一次
        unique_together = ('user', 'post')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} favorited {self.post.title}'

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # 確保每個用戶只能追蹤另一個用戶一次
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'
