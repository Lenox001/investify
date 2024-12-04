from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django import forms
from .models import ContactMessage, RecentActivity, Investment, Transaction  
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .forms import UserEditForm
import base64
from django.http import JsonResponse
from django.conf import settings
from .utils import get_mpesa_access_token
from datetime import datetime
import requests
from django.db import IntegrityError
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name', required=True)
    email = forms.EmailField(label='Your Email', required=True)
    message = forms.CharField(widget=forms.Textarea, label='Your Message', required=True)

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label='Username')
    email = forms.EmailField(required=True, label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

def index(request):
    if request.user.is_authenticated:
        return render(request, 'core/index.html')  # Render the index page for authenticated users
    else:
        return redirect('login')  # Redirect to the login page for unauthenticated users

@login_required
def user(request):
    # Fetch recent activities and transactions for the logged-in user
    recent_activities = RecentActivity.objects.filter(user=request.user)
    
    # Change 'date' to 'created_at'
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]  # Last 5 transactions

    # Calculate the user's total investment balance
    total_balance = Investment.objects.filter(user=request.user).aggregate(balance=Sum('amount'))['balance'] or 0

    return render(request, 'core/account.html', {
        'recent_activities': recent_activities,
        'transactions': transactions,
        'balance': total_balance,
        'user': request.user,
    })

def contact(request):
    form = ContactForm(request.POST or None)  # Handle form initialization
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        # Create a ContactMessage object and save it to the database
        ContactMessage.objects.create(name=name, email=email, message=message)

        # Notify user about successful submission
        messages.success(request, 'Your message has been sent successfully!')

        # Reset the form after submission
        form = ContactForm()  

    elif request.method == 'POST':
        # Notify user about form errors
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'core/contact.html', {'form': form})

def invest(request):
    return render(request, 'core/invest.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Log the activity
            RecentActivity.objects.create(
                user=user,
                activity="Logged in",  # Customize this message as needed
            )
            messages.success(request, 'You have logged in successfully.')
            return redirect('index')  # Redirect to the home page or desired URL
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')  # Render the login page

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Hash the password
            user.save()
            login(request, user)  # Log the user in immediately after registration
            # Log the activity
            RecentActivity.objects.create(
                user=user,
                activity="Registered an account",  # Customize this message as needed
            )
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('index')  # Redirect to the home page or desired URL
        else:
            for error in form.errors.values():
                messages.error(request, error)

    form = CustomUserCreationForm()  # Render an empty registration form
    return render(request, 'core/register.html', {'form': form})  # Render the registration page

def logout_view(request):
    user = request.user
    logout(request)  # Log the user out
    if user.is_authenticated:
        # Log the activity
        RecentActivity.objects.create(
            user=user,
            activity="Logged out",  # Customize this message as needed
        )
    messages.success(request, 'You have logged out successfully.')  # Notify user
    return redirect('login')  # Redirect to the login page

def edit_account(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Log the activity
            RecentActivity.objects.create(
                user=request.user,
                activity="Updated account details",  # Customize this message as needed
            )
            messages.success(request, 'Your account has been updated successfully.')
            return redirect('user')  # Redirect to account page after saving
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'core/edit_account.html', {'form': form})

def basic_package(request):
    return render(request, 'core/basic_package.html')

def classic_package(request):
    return render(request, 'core/classic_package.html')

def premium_package(request):
    return render(request, 'core/premium_package.html')

def titanium_package(request):
    return render(request, 'core/titanium_package.html')

@login_required
def investment_overview(request):
    if request.user.is_authenticated:
        investments = Investment.objects.filter(user=request.user)

        # Calculate the user's total investment balance
        total_balance = investments.aggregate(balance=Sum('amount'))['balance'] or 0

        return render(request, 'core/investment_overview.html', {
            'investments': investments,
            'balance': total_balance
        })
    return redirect('login')  # Redirect to login if user is not authenticated

@login_required
def lipa_na_mpesa_online(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Get the M-Pesa access token
        access_token = get_mpesa_access_token()

        # Prepare the STK Push request data
        api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        headers = {'Authorization': f'Bearer {access_token}'}
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode('utf-8')).decode('utf-8')

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": "https://yourdomain.com/callback",
            "AccountReference": "Investment Amount",
            "TransactionDesc": "Payment for Investify Package"
        }

        # Make the STK Push request to M-Pesa API
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()

        print("M-Pesa response:", response_data)  # Debugging line

        transaction_id = response_data.get('MerchantRequestID')

        try:
            if response_data.get('ResponseCode') == '0':
                # Payment initiated successfully
                transaction = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_id=transaction_id,
                    transaction_type='investment',
                    status='success'
                )
                # Log success in RecentActivity
                RecentActivity.objects.create(
                    user=request.user,
                    activity=f"Successful payment of Ksh {amount} for investment."
                )
                return render(request, 'core/payment_success.html')
            else:
                # Payment initiation failed
                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_id=transaction_id,
                    transaction_type='investment',
                    status='failed'
                )
                messages.error(request, 'Payment failed. Please try again.')
                return render(request, 'core/payment_failed.html')

        except IntegrityError as e:
            messages.error(request, 'There was an error saving the transaction. Please try again.')
            print("IntegrityError:", str(e))  # Debugging line
            return render(request, 'core/payment_failed.html')

    return render(request, 'core/lipa_na_mpesa.html')

def custom_admin_dashboard(request):
    recent_activities = RecentActivity.objects.all()[:5]  # Get the 5 most recent activities
    return render(request, 'admin/index.html', {'recent_activities': recent_activities})
