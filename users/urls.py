from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import UserLogoutView, UserCreateView, email_confirm_view

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('confirm/<int:user_id>/<str:token>/', email_confirm_view, name='email_confirm'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name="users/password_reset_form.html",
        email_template_name="users/password_reset_email.html",
        subject_template_name="users/password_reset_subject.txt",
        success_url=reverse_lazy("users:password_reset_done"),
    ),
        name='password_reset'
    ),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"),
        name='password_reset_done'
    ),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url=reverse_lazy('users:password_reset_complete'),
    ),
        name='password_reset_confirm',
    ),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html',
    ),
        name='password_reset_complete',
    ),
    ]