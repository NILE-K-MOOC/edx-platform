from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# notice data model.
class Notice(models.Model):
    title = models.CharField(max_length=255)
    contents = models.TextField()
    writer = models.ForeignKey(User, db_index=True) 
    created_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    detail_url = models.TextField(default='', null=True)
    is_popup = models.BooleanField(null=False, default=False)
    is_display = models.BooleanField(null=False, default=False)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

   # def __unicode__(self):
   #     return self.title

    #def __unicode__(self):
    #    return self.contents
def get_file_path(instance, filename):
    return "notice/%s/%s" %(timezone.now().date().strftime('%Y/%m/%d'), filename)

# Attachments data model.
class Attachments(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_file_path)
    
    def __unicode__(self):
        return unicode(self.file)
