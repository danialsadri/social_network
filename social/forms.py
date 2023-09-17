from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, widget=forms.TextInput, label='username or phone number or email')
    password = forms.CharField(max_length=200, required=True, widget=forms.PasswordInput)
