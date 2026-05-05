from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .neo4j_service import create_user_node
from .forms import EditProfileForm
from .neo4j_service import get_user_node, update_user_node

def signup_view(request):
    # Handle form submission
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            bio = form.cleaned_data.get("bio", "")

            create_user_node(user, bio=bio)

            login(request, user)
            return redirect("home")
        
    # If GET request or form is invalid, render the signup page with the form
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})

@login_required
def home_view(request):
    return render(request, "accounts/home.html")

def landing_view(request):
    return render(request, "accounts/landing.html")

@login_required
def profile_view(request):
    neo4j_user = get_user_node(request.user.id)

    return render(request, "accounts/profile.html", {"neo4j_user": neo4j_user})

@login_required
def edit_profile_view(request):
    neo4j_user = get_user_node(request.user.id)

    # Handle form submission
    if request.method == "POST":
        form = EditProfileForm(request.POST)

        if form.is_valid():
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.username = form.cleaned_data["username"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()

            bio = form.cleaned_data.get("bio", "")
            update_user_node(request.user, bio=bio)

            return redirect("profile")
    
    # Pre-fill form with existing data and send to edit_profile.html
    else:
        form = EditProfileForm(initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": request.user.username,
            "email": request.user.email,
            "bio": neo4j_user.get("bio", "") if neo4j_user else "",
        })

    return render(request, "accounts/edit_profile.html", {"form": form})