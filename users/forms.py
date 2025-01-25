from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Login',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'})
    )
    password = forms.CharField(
        label='Password',
        max_length=30,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'maxlength': '30'})
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterFormUser(forms.ModelForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email',  'password', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('This email already exists!')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2:
            if password != password2:
                raise forms.ValidationError('Passwords do not match!')
            if len(password) < 8:
                raise forms.ValidationError('Password is too short! It must contain at least 8 characters.')

        return cleaned_data


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


