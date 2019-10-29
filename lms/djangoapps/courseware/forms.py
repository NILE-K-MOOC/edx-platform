from django import forms
from models import CourseOrg


class CourseOrgForm(forms.ModelForm):
    org_body = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 100}))

    class Meta:
        model = CourseOrg
        fields = ('__all__')
