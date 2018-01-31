from django.conf.urls import patterns, url, include

from .views import DeleteCourseView
from .views import ProgressUserView
from .views import CourseEnrollView

urlpatterns = patterns(
    '',
    url(r'^deletecourse/$', DeleteCourseView.as_view()),
    url(r'^progressuser/$', ProgressUserView.as_view()),
    url(r'^courseenroll/$', CourseEnrollView.as_view()),
)
