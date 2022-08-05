from django import forms
from django.forms import ModelForm
from .models import *

class UserForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('full_name', 'bio', 'avatar')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }