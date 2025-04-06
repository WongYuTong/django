from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, FavoritePost, Follow
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, PostCreateForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'帳號已建立，現在可以登入！')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '帳號或密碼不正確！')
    
    return render(request, 'user/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '您的個人資料已更新！')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'posts': posts
    }
    
    return render(request, 'user/profile.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, '貼文已成功建立！')
            return redirect('post_history')
    else:
        form = PostCreateForm()
    
    return render(request, 'user/create_post.html', {'form': form})

@login_required
def post_history(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/post_history.html', {'posts': posts})

@login_required
def toggle_favorite(request, post_id):
    """收藏或取消收藏貼文"""
    post = get_object_or_404(Post, id=post_id)
    favorite, created = FavoritePost.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        # 如果已存在，說明用戶要取消收藏
        favorite.delete()
        is_favorite = False
        message = "已取消收藏"
    else:
        is_favorite = True
        message = "已加入收藏"
    
    # 如果是AJAX請求，返回JSON響應
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'message': message
        })
    
    # 否則重定向回上一頁
    return redirect(request.META.get('HTTP_REFERER', 'post_history'))

@login_required
def toggle_follow(request, user_id):
    """追蹤或取消追蹤用戶"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # 不能追蹤自己
    if request.user.id == user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': '不能追蹤自己'})
        messages.error(request, '不能追蹤自己')
        return redirect(request.META.get('HTTP_REFERER', 'profile'))
    
    follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    
    if not created:
        # 如果已存在，說明用戶要取消追蹤
        follow.delete()
        is_following = False
        message = f"已取消追蹤 {user_to_follow.username}"
    else:
        is_following = True
        message = f"已開始追蹤 {user_to_follow.username}"
    
    # 如果是AJAX請求，返回JSON響應
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_following': is_following,
            'message': message
        })
    
    # 否則重定向回上一頁
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def favorites(request):
    """顯示用戶收藏的貼文"""
    favorites = FavoritePost.objects.filter(user=request.user).select_related('post', 'post__user')
    return render(request, 'user/favorites.html', {'favorites': favorites})

@login_required
def followers(request):
    """顯示關注用戶的人"""
    followers = Follow.objects.filter(followed=request.user).select_related('follower')
    following = Follow.objects.filter(follower=request.user).select_related('followed')
    return render(request, 'user/followers.html', {
        'followers': followers,
        'following': following
    })
