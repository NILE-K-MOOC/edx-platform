from django import forms
from notice.models import Notice

# notice form.
class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "contents"
        ]
        widgets = {'id': forms.HiddenInput()}