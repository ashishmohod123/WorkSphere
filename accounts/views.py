from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, UserRole
from .forms import UserLoginForm, UserProfileUpdateForm
from .decorators import admin_required, hr_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'profile':
            profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
            password_form = PasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Please correct the errors below.")
        elif form_type == 'password':
            password_form = PasswordChangeForm(user, request.POST)
            profile_form = UserProfileUpdateForm(instance=user)
            if password_form.is_valid():
                user_updated = password_form.save()
                update_session_auth_hash(request, user_updated)
                messages.success(request, "Password updated successfully.")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Password update failed. Please check criteria.")
    else:
        profile_form = UserProfileUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
        
    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
@hr_required
def user_list_view(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'accounts/user_list.html', {'users': users})
