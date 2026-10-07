"""Формы веб-сайта."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)

from apps.accounts.models import User
from apps.news.models import Comment
from config import constants as c


class CommentForm(forms.ModelForm):
    """Форма добавления комментария к новости."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Написать комментарий...',
                    'class': 'form-textarea',
                }
            ),
        }
        labels = {
            'text': '',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Отключаем стандартную валидацию required,
        # чтобы использовать наше сообщение об ошибке
        self.fields['text'].required = False

    def clean_text(self):
        """Проверить, что текст не пустой."""
        text = (self.cleaned_data.get('text') or '').strip()
        if not text:
            raise forms.ValidationError(
                'Текст комментария не может быть пустым.',
            )
        return text


class RegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя.

    Использует UserCreationForm Django (пароль + подтверждение +
    валидация), добавляет email и имя.
    """

    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'you@example.com',
            }
        ),
    )
    first_name = forms.CharField(
        label='Имя',
        required=False,
        max_length=c.STAFF_FIRST_NAME_MAX_LENGTH,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Иван',
            }
        ),
    )
    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        max_length=c.STAFF_LAST_NAME_MAX_LENGTH,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Иванов',
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'ivanov',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-input',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-input',
            }
        )

    def save(self, commit=True):
        """Создать пользователя с ролью FAN."""
        user = super().save(commit=False)
        user.role = User.Role.FAN
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Форма входа — те же поля, но со стилями."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Ваш логин',
                'autofocus': True,
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'class': 'form-input',
                'placeholder': 'Пароль',
            }
        )
