from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

class ChangeUsernameForm(forms.Form):
    new_username = forms.CharField(
        label="New Username",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new username'}),
        help_text="Must be unique with at least 8 characters and no spaces"
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        help_text="Enter your password for confirmation."
    )

    def clean_new_username(self):
        # Get the new username from form data
        new_username = self.cleaned_data['new_username']
        
        # Check if the username already exists
        if User.objects.filter(username=new_username).exists():
            raise forms.ValidationError("This username is already taken.")
        
        # Additional username validation (e.g., length, format)
        if len(new_username) < 8:
            raise forms.ValidationError("Username must be at least 8 characters long.")
        if len(new_username) > 150:
            raise forms.ValidationError("Username cannot exceed 150 characters.")
        
        return new_username

    def clean_password(self):
        password = self.cleaned_data['password']
        return password
    
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'}),
        help_text="Enter your current password to authenticate."
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        help_text="Your new password must be at least 8 characters and not be commonly-used."
    )
    confirm_new_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        help_text="Re-enter your new password."
    )

    def clean_new_password(self):
        password = self.cleaned_data['new_password']

        # Validate the password using Django's password validation rules
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)

        return password

    
class AddEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        help_text="Enter a valid email address."
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # Validate the email format
        try:
            EmailValidator()(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        
        return email