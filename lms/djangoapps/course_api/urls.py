"""
Course API URLs
"""
from django.conf import settings
from django.conf.urls import include, url

from .views import CourseDetailView, CourseListView

urlpatterns = [
    # url(r'^v1/course/list$', CourseListView.as_view(), name="courseList2"),
    url(r'^v1/course/list/$', CourseListView.as_view(), name="courseList"),
    url(r'^v1/courses/$', CourseListView.as_view(), name="course-list"),
    # url(r'^v1/course/detail$', CourseDetailView.as_view(), name="courseDetail2"),
    url(r'^v1/course/detail/$', CourseDetailView.as_view(), name="courseDetail"),
    url(r'^v1/courses/{}'.format(settings.COURSE_KEY_PATTERN), CourseDetailView.as_view(), name="course-detail"),
    url(r'', include('course_api.blocks.urls'))
]
