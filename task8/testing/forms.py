from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import StudentProfile


User = get_user_model()


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label="Full name")
    email = forms.EmailField()
    terms = forms.BooleanField(label="I agree to the terms of use")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    field_order = ("full_name", "username", "email", "password1", "password2", "terms")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists() or StudentProfile.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        names = self.cleaned_data["full_name"].strip().split(maxsplit=1)
        user.first_name = names[0]
        user.last_name = names[1] if len(names) > 1 else ""
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user