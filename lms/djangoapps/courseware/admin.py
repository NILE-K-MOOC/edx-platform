# -*- coding: utf-8 -*-
from django.contrib import admin

from config_models.admin import ConfigurationModelAdmin, KeyedConfigurationModelAdmin

from courseware import models


class IndexLogo(admin.ModelAdmin):

    # list_display = ['id', 'main_logo_img', 'section_1_before', 'section_1_hover', 'section_2_before', 'section_2_hover',
    #                 'section_3_before', 'section_3_hover', 'section_4_before', 'section_4_hover', 'section_5_before',
    #                 'section_5_hover', 'section_6_before', 'section_6_hover',
    #                 'regist_date', 'modify_date']

    list_display = ['id', 'main_logo_img','regist_date', 'modify_date']
    list_filter = ['id', 'modify_date']


class IndexSection(admin.ModelAdmin):
    list_display = ['id', 'section_logo_large', 'section_name', 'order_no']


class IndexSectionCourse(admin.ModelAdmin):
    list_display = ['id', 'course_id', 'section_id']


admin.site.register(models.TbIndexImage, IndexLogo)
admin.site.register(models.TbSections, IndexSection)
admin.site.register(models.TbSectionCourses, IndexSectionCourse)
admin.site.register(models.DynamicUpgradeDeadlineConfiguration, ConfigurationModelAdmin)
admin.site.register(models.OfflineComputedGrade)
admin.site.register(models.OfflineComputedGradeLog)
admin.site.register(models.CourseDynamicUpgradeDeadlineConfiguration, KeyedConfigurationModelAdmin)
admin.site.register(models.OrgDynamicUpgradeDeadlineConfiguration, KeyedConfigurationModelAdmin)
admin.site.register(models.StudentModule)
