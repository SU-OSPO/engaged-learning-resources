from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import SignUpForm, TeachOrangeAuthenticationForm


class TeachOrangeLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    authentication_form = TeachOrangeAuthenticationForm


class TeachOrangeLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def register(request):
    if request.user.is_authenticated:
        return redirect("activities:list")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(
                request,
                "Your account was created successfully. Welcome to TeachOrange.",
            )
            return redirect("activities:list")
    else:
        form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form})
