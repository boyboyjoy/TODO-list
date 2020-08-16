from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from .models import User

LOGIN_URL = 'auth:login'
SIGN_UP_URL = 'auth:sign_up'


def log_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('main-page')
        else:
            return render(request, 'login_page.html', {'form': LoginForm()})
    elif request.method == 'POST':
        user = authenticate(email=request.POST.get('email', None),
                            password=request.POST.get('password', None))
        if user is not None:
            login(request, user)
            return redirect('main-page')
        else:
            messages.add_message(request, messages.WARNING,
                                 'Incorrect email or password')
            return redirect(LOGIN_URL)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(LOGIN_URL)
    else:
        return redirect('main-page')


def sign_up(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('main-page')
        else:
            return render(request, 'sign_up.html', {'form': SignUpForm()})
    else:
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(email=request.POST.get(
                'email', None),
                                            password=request.POST.get(
                                                'password', None))
            user.name = request.POST.get('username', None)
            if request.POST.get('moderator', None):
                user.is_moderator = True
            user.save()
            return redirect(LOGIN_URL)
        for error in form.errors:
            messages.add_message(request, messages.WARNING,
                                 form.errors[error])
        return redirect(SIGN_UP_URL)
