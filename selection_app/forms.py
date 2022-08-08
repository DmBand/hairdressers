from django import forms
from django.core.exceptions import ValidationError

from captcha.fields import CaptchaField

from .models import Comment


# Rating
class IncreaseRatingForm(forms.ModelForm):
    """ Форма повышения рейтинга парикмахера """
    captcha = CaptchaField()

    class Meta:
        model = Comment
        fields = [
            'rating_value',
            'text',
            'captcha'
        ]

        widgets = {
            'text': forms.Textarea(attrs={'class': 'portfolio-textarea2',
                                          'placeholder': 'Не менее 10 символов!'})
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise ValidationError('Текст комментария должен содержать не менее 10 символов')
        return text
