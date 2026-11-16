from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)

        # Пользователь должен подтвердить email
        user.is_active = False

        if commit:
            user.save()

        return user