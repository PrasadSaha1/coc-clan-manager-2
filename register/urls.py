from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    path('', views.create_account, name='create_account'),
    path('create_account/', views.create_account, name='create_account'),
    path('email_verified/<uidb64>/<token>/', views.email_verified, name='email_verified'),
    path('login/', views.login_view, name='login'),
    path('forgot_username/', views.forgot_username, name='forgot_username'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('change_password_from_email/', views.change_password_from_email, name='change_password_from_email'),
]