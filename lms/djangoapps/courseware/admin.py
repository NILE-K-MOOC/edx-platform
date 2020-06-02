from django.contrib import admin

from config_models.admin import ConfigurationModelAdmin, KeyedConfigurationModelAdmin

from courseware import models


class IndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'main_logo_img', 'section_1', 'section_2', 'section_3', 'section_4', 'section_5', 'section_6',
                    'regist_date', 'modify_date']


admin.site.register(models.TbIndexImage, IndexAdmin)
admin.site.register(models.DynamicUpgradeDeadlineConfiguration, ConfigurationModelAdmin)
admin.site.register(models.OfflineComputedGrade)
admin.site.register(models.OfflineComputedGradeLog)
admin.site.register(models.CourseDynamicUpgradeDeadlineConfiguration, KeyedConfigurationModelAdmin)
admin.site.register(models.OrgDynamicUpgradeDeadlineConfiguration, KeyedConfigurationModelAdmin)
admin.site.register(models.StudentModule)
