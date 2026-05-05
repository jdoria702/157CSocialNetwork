from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .neo4j_service import create_user_node

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            bio = form.cleaned_data.get("bio", "")

            create_user_node(user, bio=bio)

            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})

@login_required
def home_view(request):
    return render(request, "accounts/home.html")

def landing_view(request):
    return render(request, "accounts/landing.html")