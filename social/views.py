from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout


def home(request):
    return render(request, 'social/home.html')


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
