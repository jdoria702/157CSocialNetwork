from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .neo4j_service import create_user_node
from .forms import EditProfileForm
from .neo4j_service import get_user_node, update_user_node, get_all_users_except_current, follow_user, unfollow_user, get_following, get_followers, get_mutual_followers, get_friend_recommendations

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

@login_required
def discover_users_view(request):
    users = get_all_users_except_current(request.user.id)

    return render(request, "accounts/discover_users.html", {"users": users})

@login_required
def follow_user_view(request, user_id):
    if request.method == "POST":
        follow_user(request.user.id, user_id)

    return redirect("discover_users")

@login_required
def following_view(request):
    following = get_following(request.user.id)

    return render(request, "accounts/following.html", {"following": following})

@login_required
def followers_view(request):
    followers = get_followers(request.user.id)

    return render(request, "accounts/followers.html", {"followers": followers})

@login_required
def mutual_followers_view(request, other_user_id):
    mutual_followers = get_mutual_followers(request.user.id, other_user_id)
    other_user = get_user_node(other_user_id)

    return render(request, "accounts/mutual_followers.html", {
        "mutual_followers": mutual_followers,
        "other_user": other_user
    })

@login_required
def friend_recommendations_view(request):
    recommended_users = get_friend_recommendations(request.user.id)

    return render(request, "accounts/friend_recommendations.html", {"recommended_users": recommended_users})

@login_required
def unfollow_user_view(request, user_id):
    if request.method == "POST":
        unfollow_user(request.user.id, user_id)

    return redirect("following")