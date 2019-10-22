from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Board data model.
class Repository(models.Model):
    title = models.CharField(max_length=255)
    contents = models.TextField()
    writer = models.ForeignKey(User, db_index=True) 
    created_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __unicode__(self):
        return self.title

    def __unicode__(self):
        return self.contents

def get_file_path(instance, filename):
    return "repository/%s/%s" %(timezone.now().date().strftime('%Y/%m/%d'), filename)

# Attachments data model.
class Attachments(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_file_path)
    
    def __unicode__(self):
        return unicode(self.file)
