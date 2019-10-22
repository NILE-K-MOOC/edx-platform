from django.contrib import admin
from notice.models import Notice

# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'writer', 'created_date')

admin.site.register(Notice, NoticeAdmin)
