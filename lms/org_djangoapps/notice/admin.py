from django.contrib import admin
from notice.models import Notice
from notice.models import Attachments

# Register your models here.

class AttachmentsInline(admin.TabularInline):
    model = Attachments

class NoticeAdmin(admin.ModelAdmin):
    inlines = [AttachmentsInline]
    list_display = ('id', 'title', 'writer', 'created_date')

admin.site.register(Notice, NoticeAdmin)

