from django.contrib import admin
from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'autor',
        'belong_to',
        'text',
        'rating_value',
        'date_added',
    )
    list_editable = (
        'rating_value',
    )


admin.site.register(Comment, CommentAdmin)
