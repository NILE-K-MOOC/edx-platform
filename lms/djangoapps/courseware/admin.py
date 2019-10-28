'''
django admin pages for courseware model
'''

from courseware.models import StudentModule, OfflineComputedGrade, OfflineComputedGradeLog, CourseSection, CourseSectionCourse
from ratelimitbackend import admin

admin.site.register(StudentModule)

admin.site.register(OfflineComputedGrade)

admin.site.register(OfflineComputedGradeLog)


# Add 20191028

class CourseSecionAdmin(admin.ModelAdmin):
    list_display = [
        'section_name',
    ]




class CourseSectionCourseAdmin(admin.ModelAdmin):
    list_display = [
        'section_name',
        'course_id',
    ]

    def section_name(self, instance):
        return instance.section.section_name


admin.site.register(CourseSection, CourseSecionAdmin)
admin.site.register(CourseSectionCourse, CourseSectionCourseAdmin)
