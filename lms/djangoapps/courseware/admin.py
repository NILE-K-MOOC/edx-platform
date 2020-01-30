# -*- coding: utf-8 -*-
'''
django admin pages for courseware model
'''

from courseware.models import StudentModule, OfflineComputedGrade, OfflineComputedGradeLog, CourseSection, CourseSectionCourse, CourseOrg
from ratelimitbackend import admin
from forms import CourseOrgForm

import csv
from django.utils.safestring import mark_safe
from django.http import HttpResponse


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


admin.site.register(StudentModule)
admin.site.register(OfflineComputedGrade)
admin.site.register(OfflineComputedGradeLog)


# Add 20191028
class CourseOrgAdmin(admin.ModelAdmin):
    fields = [
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

    # fields = ['section_logo_large', 'view_section_logo_large', 'section_logo_large_hover', 'view_section_logo_large_hover', 'section_logo_small', 'view_section_logo_small',
    #           'section_name', 'order_no', 'org']

    fields = ['section_name', 'section_logo_large', 'section_logo_large_hover', 'section_logo_small', 'order_no', 'org']

    readonly_fields = ["view_section_logo_large", "view_section_logo_large_hover", "view_section_logo_small"]

    def view_section_logo_large(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.section_logo_large.url,
            width=obj.section_logo_large.width,
            height=obj.section_logo_large.height,
        )
        )

    def view_section_logo_large_hover(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.section_logo_large_hover.url,
            width=obj.section_logo_large_hover.width,
            height=obj.section_logo_large_hover.height,
        )
        )

    def view_section_logo_small(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.section_logo_small.url,
            width=obj.section_logo_small.width,
            height=obj.section_logo_small.height,
        )
        )


class CourseSectionCourseAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'id',
        'section_name',
        'course_id',
    ]

    actions = ["export_as_csv"]

    def section_name(self, instance):
        return instance.section.section_name


admin.site.site_header = "Kotech Admin"
admin.site.site_title = "Kotech Admin Portal"
admin.site.index_title = "Welcome Kotech Admin"

admin.site.register(CourseOrg, CourseOrgAdmin)
admin.site.register(CourseSection, CourseSecionAdmin)
admin.site.register(CourseSectionCourse, CourseSectionCourseAdmin)
