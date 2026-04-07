from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
        username = self.cleaned_data["username"].strip().lower()
        from django.conf import settings

        suffixes = getattr(settings, "ALLOWED_EMAIL_SUFFIXES", (".edu",))
        if not any(username.endswith(s) for s in suffixes):
            raise forms.ValidationError(
                "Registration requires a university email address ending in: "
                + ", ".join(suffixes)
            )
        return username
