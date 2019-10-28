from django.contrib import admin
from .models import ExtraInfo

class ExtraInfoAdmin(admin.ModelAdmin):
    list_display = ('org', 'username_kor', 'department', 'student_id')
    # list_display_links = ('username_kor')
    list_display_links = None

admin.site.register(ExtraInfo, ExtraInfoAdmin)
