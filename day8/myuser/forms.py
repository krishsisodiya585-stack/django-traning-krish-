from django import forms
from django.contrib.auth.hashers import make_password
from .models import Student, user


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=20)
    name = forms.CharField(max_length=20, label='Name')
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput,
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if user.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'The passwords do not match.')
        return cleaned_data

    def save(self):
        return user.objects.create(
            username=self.cleaned_data['username'],
            name=self.cleaned_data['name'],
            password=make_password(self.cleaned_data['password']),
        )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('student_id', 'student_name', 'branch')
        labels = {
            'student_id': 'Student ID',
            'student_name': 'Student name',
            'branch': 'Student branch',
        }