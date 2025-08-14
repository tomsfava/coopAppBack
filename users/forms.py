from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'is_admin', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]
