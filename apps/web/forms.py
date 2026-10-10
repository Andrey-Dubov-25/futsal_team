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
    """Форма регистрации нового пользователя."""

    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'you@example.com',
                'autocomplete': 'email',
            }
        ),
    )
    first_name = forms.CharField(
        label='Имя',
        required=False,
        max_length=c.STAFF_FIRST_NAME_MAX_LENGTH,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иван',
                'autocomplete': 'given-name',
            }
        ),
    )
    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        max_length=c.STAFF_LAST_NAME_MAX_LENGTH,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов',
                'autocomplete': 'family-name',
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
                'placeholder': 'Ваш логин',
                'autocomplete': 'username',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Минимум 8 символов',
                'autocomplete': 'new-password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Повторите пароль',
                'autocomplete': 'new-password',
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
    """Форма входа."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': 'Ваш логин',
                'autocomplete': 'username',
                'autofocus': True,
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'placeholder': 'Пароль',
                'autocomplete': 'current-password',
            }
        )
