from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.contrib.auth.models import User


def validate_faculty_email(email: str) -> str:
    """Normalize email or raise ValidationError if the domain suffix is not allowed."""
    normalized = (email or "").strip().lower()
    suffixes = getattr(settings, "ALLOWED_EMAIL_SUFFIXES", (".edu",))
    if not normalized or not any(normalized.endswith(s) for s in suffixes):
        raise forms.ValidationError(
            "Use a university email address ending in: " + ", ".join(suffixes)
        )
    return normalized


class SignUpForm(UserCreationForm):
    """
    Register with university email as login. Username is set to the email address.
    """

    username = forms.EmailField(
        label="University email",
        help_text="Use your .edu address. This will be your login.",
        max_length=150,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

    def clean_username(self):
        return validate_faculty_email(self.cleaned_data["username"])


class TeachOrangeAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        return validate_faculty_email(self.cleaned_data["username"])


class EduPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        return validate_faculty_email(self.cleaned_data["email"])
