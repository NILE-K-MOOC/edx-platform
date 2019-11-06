# -*- coding: utf-8 -*-
'''
django admin pages for courseware model
'''

from courseware.models import StudentModule, OfflineComputedGrade, OfflineComputedGradeLog, CourseSection, CourseSectionCourse, CourseOrg
from ratelimitbackend import admin
from forms import CourseOrgForm

admin.site.register(StudentModule)

admin.site.register(OfflineComputedGrade)

admin.site.register(OfflineComputedGradeLog)


# Add 20191028
class CourseOrgAdmin(admin.ModelAdmin):
    fields = [
        'id',
        'org_code',
        'org_name',
        'org_image',
        'org_body',
    ]

    form = CourseOrgForm

    def save_model(self, request, obj, form, change):
        return super(CourseOrgAdmin, self).save_model(request, obj, form, change)


class CourseSecionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'section_name',
        'org',
    ]


class CourseSectionCourseAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'section_name',
        'course_id',
    ]

    def section_name(self, instance):
        return instance.section.section_name


admin.site.register(CourseOrg, CourseOrgAdmin)
admin.site.register(CourseSection, CourseSecionAdmin)
admin.site.register(CourseSectionCourse, CourseSectionCourseAdmin)
