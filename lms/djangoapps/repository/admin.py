from django.contrib import admin
from repository.models import Repository
from repository.models import Attachments

# Register your models here.

class AttachmentsInline(admin.TabularInline):
    model = Attachments

class RepositoryAdmin(admin.ModelAdmin):
    inlines = [AttachmentsInline]
    list_display = ('id', 'title', 'writer', 'created_date')

admin.site.register(Repository, RepositoryAdmin)
