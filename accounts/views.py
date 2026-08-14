from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import CustomUser
from .forms import (UserRegistrationForm, UserLoginForm, UserProfileUpdateForm,
                    AdminUserCreateForm, AdminUserUpdateForm)


def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return redirect('accounts:admin_user_list')
        return redirect('dashboard:home')
    return redirect('accounts:login')


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return redirect('accounts:admin_user_list')
        return redirect('dashboard:home')

    form = UserLoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        # 🔥 FIX: Auto assign admin role to superuser
        if user.is_superuser and user.role != 'admin':
            user.role = 'admin'
            user.save()

        if user.is_superuser or user.role == 'admin':
            messages.success(request, f'Welcome Admin, {user.username}!')
            return redirect('accounts:admin_user_list')

        else:
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')

    return render(request, 'accounts/login.html', {'form': form})


def user_register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'user'
        user.save()
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('accounts:login')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile(request):
    form = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form})


# 🔥 Improved admin check
def is_admin(user):
    return user.is_superuser or getattr(user, 'role', '') == 'admin'


@login_required
def admin_user_list(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    users = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_user_list.html', {'users': users})


@login_required
def admin_user_create(request):
    if not is_admin(request.user):
        return redirect('dashboard:home')

    form = AdminUserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully!')
        return redirect('accounts:admin_user_list')

    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Create User'})


@login_required
def admin_user_update(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard:home')

    user = get_object_or_404(CustomUser, pk=pk)
    form = AdminUserUpdateForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully!')
        return redirect('accounts:admin_user_list')

    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Edit User'})


@login_required
def admin_user_delete(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard:home')

    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('accounts:admin_user_list')

    return render(request, 'accounts/admin_user_confirm_delete.html', {'user': user})


@login_required
def toggle_user_status(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard:home')

    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()

        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} {status} successfully!')

    return redirect('accounts:admin_user_list')