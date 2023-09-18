from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from taggit.models import Tag

from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.auth.views import (PasswordChangeView, PasswordChangeDoneView, PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)

from .models import Post


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
            return redirect('social:home')
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
                    return redirect('social:home')
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
    posts = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    context = {
        'posts': posts,
        'tag': tag,
    }
    return render(request, 'social/post_list.html', context)
