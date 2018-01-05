from django.conf.urls import patterns, url, include

from .views import UpdateCourseView
from .views import CreateUserView
from .views import CreateCourseView
from .views import EnrollUserView
from .views import RerunCourseView
from .views import ManageUserView

urlpatterns = patterns(
    '',
    url(r'^updatecourse/$', UpdateCourseView.as_view()),
    url(r'^createuser/$', CreateUserView.as_view()),
    url(r'^createcourse/$', CreateCourseView.as_view()),
    url(r'^enrolluser/$', EnrollUserView.as_view()),
    url(r'^reruncourse/$', RerunCourseView.as_view()),
    url(r'^manageuser/$',ManageUserView.as_view()),
)
