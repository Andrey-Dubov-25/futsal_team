"""Формы веб-сайта."""

from django import forms

from apps.news.models import Comment


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
