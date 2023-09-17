from django import forms
from django.core.exceptions import ValidationError

from social.models import User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(max_length=200, widget=forms.PasswordInput, label='password')
    password2 = forms.CharField(max_length=200, widget=forms.PasswordInput, label='repeat password')

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email', 'first_name', 'last_name']

    def clean(self):
        cd = super().clean()
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('پسورد ها باید مطابقت داشته باشند')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('phone number already exists')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('email already exists')
        return email


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email', 'first_name', 'last_name', 'biography', 'job', 'date_of_birth',
                  'photo']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError('username already exists')
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.exclude(id=self.instance.id).filter(phone_number=phone_number).exists():
            raise forms.ValidationError('phone number already exists')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise forms.ValidationError('email already exists')
        return email


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, widget=forms.TextInput,
                               label='username or phone number or email')
    password = forms.CharField(max_length=200, required=True, widget=forms.PasswordInput)
