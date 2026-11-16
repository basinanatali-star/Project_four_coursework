from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.conf import settings

from users.forms import UserRegisterForm
from users.models import CustomUser
from users.tokens import email_verification_token


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("service:index")


class UserCreateView(CreateView):
    model = CustomUser
    form_class = UserRegisterForm
    template_name = "users/users_form.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Отправляем письмо для подтверждения Email
        self.send_confirmation_email(self.object)

        messages.success(
            self.request,
            "Регистрация прошла успешно! "
            "Проверьте почту и подтвердите свой Email."
        )

        return response

    def send_confirmation_email(self, user):
        # Создаём токен подтверждения
        token = email_verification_token.make_token(user)

        # Формируем относительный адрес
        confirmation_path = reverse(
            "users:email_confirm",
            kwargs={
                "user_id": user.pk,
                "token": token,
            },
        )

        # Преобразуем его в полный URL
        confirmation_url = self.request.build_absolute_uri(confirmation_path)

        # Отправляем письмо
        send_mail(
            subject="Подтверждение регистрации",
            message=(
                f"Здравствуйте!\n\n"
                f"Для подтверждения электронной почты "
                f"перейдите по ссылке:\n{confirmation_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


def email_confirm_view(request, user_id, token):
    user = get_object_or_404(CustomUser, pk=user_id)

    # Проверяем, не подтверждён ли Email ранее
    if user.is_active:
        messages.info(request, "Электронная почта уже подтверждена.")
        return redirect("users:login")

    # Проверяем токен
    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])

        messages.success(
            request,
            "Электронная почта успешно подтверждена! "
            "Теперь вы можете войти."
        )
        return redirect("users:login")

    messages.error(
        request,
        "Ссылка подтверждения недействительна или срок её действия истёк."
    )
    return redirect("users:register")