# -*- coding: utf-8 -*-
from django import forms
from .models import Invitation
from django.forms import ModelForm
from django.core.validators import MinLengthValidator, EmailValidator, RegexValidator

class InvitationForm(forms.ModelForm):

    user_id = forms.IntegerField()#widget=forms.HiddenInput()
    username = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=100,required=True)
    email = forms.EmailField(max_length=40, required=True)
    job = forms.CharField(max_length=10, widget=forms.Select, required=True)
    purpose = forms.CharField(max_length=200, required=True)
    agree = forms.CharField(widget=forms.CheckboxInput, required=False)
    org = forms.CharField(max_length=20, required=True)

    class Meta:
        model = Invitation
        fields = ('username', 'phone', 'email', 'job', 'purpose', 'agree', 'org')





