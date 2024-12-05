from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from transactions.models import Transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash 
from decimal import Decimal

def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    return render(request, 'accounts/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        
        # Update profile picture if provided
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        
        # Update other fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.preferred_currency = request.POST.get('preferred_currency', user.preferred_currency)
        
        # Update financial settings
        if request.POST.get('monthly_budget'):
            user.monthly_budget = Decimal(request.POST.get('monthly_budget'))
        if request.POST.get('savings_goal'):
            user.savings_goal = Decimal(request.POST.get('savings_goal'))
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
        
    return render(request, 'accounts/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Not updated')
    else:
        form = PasswordChangeForm(request.user)  # Create a blank form for GET requests
    
    return redirect('accounts:profile')

