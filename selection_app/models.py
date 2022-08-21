from django.db import models
from users_app.models import Hairdresser


class Comment(models.Model):
    """ Модель комментария """
    autor = models.CharField(
        max_length=50, 
        verbose_name='автор',
    )
    belong_to = models.ForeignKey(
        Hairdresser, 
        on_delete=models.CASCADE, 
        verbose_name='кому',
        related_name='comments',
    )
    text = models.TextField(
        max_length=8000, 
        verbose_name='добавить отзыв',
    )
    rating_value = models.IntegerField(
        verbose_name='оценка',
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name_plural = 'комментарии'
        verbose_name = 'комментарий'

    def __str__(self):
        return self.text
