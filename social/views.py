from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from taggit.models import Tag
from django.views.decorators.http import require_POST
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.auth.views import (PasswordChangeView, PasswordChangeDoneView, PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from .models import Post, Image, Contact


def home(request):
    return render(request, 'social/home.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('social:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_user(request):
    if request.method == 'POST':
        form = UserEditForm(data=request.POST, files=request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('social:profile')
    else:
        form = UserEditForm(instance=request.user)
    context = {'form': form}
    return render(request, 'registration/edit_user.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('social:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('social:profile')
                else:
                    return HttpResponse('this account is disabled')
            else:
                return HttpResponse('you are not logged in')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('social:home')
    return render(request, 'registration/logged_out.html')


def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            description = f"{cd['name']}\n{cd['email']}\n{cd['phone_number']}\n\n{cd['description']}"
            send_mail(cd['subject'], description, 'danielsadri01@gmail.com', ['danielsadri01@gmail.com'], False)
            return render(request, 'forms/ticket_done.html')
    else:
        form = TicketForm()
    return render(request, 'forms/ticket.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('social:password_change_done')


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('social:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('social:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


def post_list(request, tag_slug=None):
    posts = Post.objects.select_related('author').order_by('-total_likes')
    # filter by tag
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    # filter by pagination
    paginator = Paginator(posts, 2)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'social/post_list_ajax.html', {'posts': posts})
    context = {'posts': posts, 'tag': tag}
    return render(request, 'social/post_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # get_similar_posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_post = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created')[:2]
    # comment form
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'similar_post': similar_post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'social/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(post=post, image_file=form.cleaned_data['image1'])
            Image.objects.create(post=post, image_file=form.cleaned_data['image2'])
            return redirect('social:profile')
    else:
        form = PostCreateForm()
    return render(request, 'forms/post_create.html', {'form': form})


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostUpdateForm(data=request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            Image.objects.create(post=post, image_file=form.cleaned_data['image1'])
            Image.objects.create(post=post, image_file=form.cleaned_data['image2'])
            return redirect('social:profile')
    else:
        form = PostUpdateForm(instance=post)
    return render(request, 'forms/post_update.html', {'form': form, 'post': post})


def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('social:profile')
    return render(request, 'social/post_delete.html', {'post': post})


def image_delete(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.method == 'POST':
        image.delete()
        return redirect('social:profile')
    return render(request, 'social/image_delete.html', {'image': image})


@login_required
def profile(request):
    posts = Post.objects.filter(author=request.user)
    saved_posts = request.user.saved_posts.all()
    return render(request, 'social/profile.html', {'posts': posts, 'saved_posts': saved_posts})


def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            results = Post.objects.filter(Q(description__icontains=query))
    context = {
        'results': results,
        'query': query
    }
    return render(request, 'social/search.html', context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'comment': comment,
        'form': form,
    }
    return render(request, 'forms/comment.html', context)


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        post_likes_count = post.likes.count()
        response_data = {'liked': liked, 'likes_count': post_likes_count}
    else:
        response_data = {'error': 'Invalid post id'}
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get('post_id')
    if post_id is not None:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        response_data = {'saved': saved}
    else:
        response_data = {'error': 'Invalid post id'}
    return JsonResponse(response_data)


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'user/user_list.html', {'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'user/user_detail.html', {'user': user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('user_id')
    if user_id:
        try:
            user = get_object_or_404(User, id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            followers_count = user.followers.count()
            followings_count = user.following.count()
            return JsonResponse({'follow': follow, 'followers_count': followers_count, 'followings_count': followings_count})
        except User.DoesNotExist:
            return JsonResponse({'error': 'user does not exist'})
    return JsonResponse({'error': 'invalid request'})
