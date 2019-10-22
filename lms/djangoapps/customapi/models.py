from django.db import models


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(unique=True, max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class CoursewareStudentmodule(models.Model):
    module_type = models.CharField(max_length=32)
    module_id = models.CharField(max_length=255)
    course_id = models.CharField(max_length=255)
    state = models.TextField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    max_grade = models.FloatField(blank=True, null=True)
    done = models.CharField(max_length=8)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    student = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'courseware_studentmodule'
        unique_together = (('student', 'module_id', 'course_id'),)



# Create your models here.
