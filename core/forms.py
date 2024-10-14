from django import forms
from django.contrib.auth.models import User

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Include any other fields you want to allow editing
