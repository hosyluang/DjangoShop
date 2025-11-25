from django_shop.decorators import non_superuser_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegisterForm, AccountUpdateForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_superuser = False
            user.is_staff = False
            user.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("login")


@non_superuser_required
def account(request):
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get("password"):
                update_session_auth_hash(request, user)
            messages.success(request, "Cap nhat thong tin thanh cong")
            return redirect("account")
        else:
            messages.error(request, "Cap nhat that bai")
    else:
        form = AccountUpdateForm(instance=request.user)
    return render(request, "users/account.html", {"form": form})
