from django.shortcuts import render, redirect
from .forms import SignUpForm
from .send_emails import send_verification_email
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import UserProfile
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import PasswordResetForm, UsernameRetrievalForm, NewPasswordForm, SignInForm
from django.contrib.auth import login, authenticate, get_user_model, update_session_auth_hash
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .send_emails import send_custom_email
from .custom_decorators import redirect_if_authenticated 
from main.helpers import determine_email_level

@redirect_if_authenticated
def create_account(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()  
            login(request, user)
            user_profile = UserProfile.objects.create(user=user)
            if form.cleaned_data['email'] != "":
                send_verification_email(user, request)
            return render(request, 'main/home.html')
    else:
        form = SignUpForm()

    return render(request, 'register/create_account.html', {'form': form})

# note that this doesn't have redirect_if_authenicated
def email_verified(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.profile.email_verified = True
        user.profile.save()
    return render(request, "main/settings.html", {"email_level": determine_email_level(request.user), "success_message": "Email verified successfully!"})

@redirect_if_authenticated
def login_view(request):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Check if the user exists
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Username does not exist
                return render(request, 'register/login.html', {
                    'form': form,
                    'success_message': "Invalid username, please try again",
                    'is_error': True
                })

            # Check if the password is correct
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')  # Redirect to the homepage or dashboard after login
            else:
                # Incorrect password
                return render(request, 'register/login.html', {
                    'form': form,
                    'success_message': "Invalid password, please try again",
                    'is_error': True
                })
        else:
            return render(request, 'register/login.html', {
                'form': form,
                'success_message': "Something went wrong, please try again",
                'is_error': True
            })
    else:
        form = SignInForm()

    return render(request, 'register/login.html', {'form': form})

@redirect_if_authenticated
def forgot_username(request):
    if request.method == 'POST':
        form = UsernameRetrievalForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Search for users with the provided email
                users = User.objects.filter(email=email)

                if users.exists():
                    # Prepare the username(s) to send (one per line)
                    usernames = [user.username for user in users]
                    message = f"The username(s) associated with your email are:\n\n" + "\n".join(usernames)
                    subject = "Your Username(s)"
                    
                    # Send the email
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,  # Ensure you have a DEFAULT_FROM_EMAIL set in settings.py
                        [email],  # Recipient email address
                    )
                    success_message = "Check your email for your username(s)"
                    is_error = False
                else:
                    success_message = "No users were found with this email address"
                    is_error = True
            except Exception as e:
                success_message = "N/A"
                is_error = True
                print(e)

            return render(request, "register/forgot_username.html", {'form': form, "success_message": success_message, "is_error": is_error})
    else:
        form = UsernameRetrievalForm()

    return render(request, "register/forgot_username.html", {'form': form})

@redirect_if_authenticated
def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)

                context = {
                    'username': user.username,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                }
                send_custom_email(
                    subject='Password Reset Request',
                    template_name='register/password_reset_email.html',
                    context=context,
                    to_email=user.email
                )
                if user.email == "":
                    success_message = "There is no email associated with that account."
                    is_error = True
                else:
                    success_message = "Check the email registered with this account to reset your password."
                    is_error = False
            except User.DoesNotExist:
                success_message = "Invalid username. Click on the second link to retrieve it if you forgot it." 
                is_error = True
            
            return render(request, "register/forgot_password.html", {'form': form, "success_message": success_message, "is_error": is_error})
    else:
        form = PasswordResetForm()

    return render(request, 'register/forgot_password.html', {'form': form})

@redirect_if_authenticated
def change_password_from_email(request):
    uidb64 = request.GET.get('uidb64')
    token = request.GET.get('token')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = NewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                confirm_password = form.cleaned_data['confirm_password']

                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Keep the user logged in after password change
                    return render(request, "register/login.html", {'form': form, "success_message": "Password changed successfully!"})
                else:
                    return render(request, "register/change_password_from_email.html", {'form': form, "success_message": "The passwords did not match, please try again.", "is_error": True})
        else:
            form = NewPasswordForm()

        return render(request, 'register/change_password_from_email.html', {'form': form})
    else:
        return render(request, "register/change_password_from_email.html", {'form': form, "success_message": "Something went wrong, please try again.", "is_error": True})

    