from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

from donations.models import (
    UserRole,
    RestaurantProfile,
    VolunteerProfile,
    NGOProfile
)

# ==========================================
# RESTAURANT REGISTER
# ==========================================
def restaurant_register(request):
    if request.method == "POST":
        u = request.POST["username"]
        e = request.POST["email"]
        p1 = request.POST["password1"]
        p2 = request.POST["password2"]

        if p1 != p2:
            return render(request, "auth/restaurant_register.html",
                          {"error": "Passwords do not match"})

        if User.objects.filter(username=u).exists():
            return render(request, "auth/restaurant_register.html",
                          {"error": "Username already taken"})

        if User.objects.filter(email=e).exists():
            return render(request, "auth/restaurant_register.html",
                          {"error": "Email already registered"})


        # Get restaurant profile fields from POST
        business_name = request.POST.get("business_name", "")
        contact_person = request.POST.get("contact_person", "")
        phone = request.POST.get("phone", "")
        city = request.POST.get("city", "")
        address = request.POST.get("address", "")

        user = User.objects.create_user(username=u, email=e, password=p1)
        UserRole.objects.create(user=user, role="restaurant")
        RestaurantProfile.objects.create(
            user=user,
            business_name=business_name,
            contact_person=contact_person,
            phone=phone,
            city=city,
            address=address
        )

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "auth/restaurant_register.html")


# ==========================================
# RESTAURANT LOGIN
# ==========================================
def restaurant_login(request):
    if request.method == "POST":
        u = request.POST["username"]
        p = request.POST["password"]

        # Allow login with email or username
        if "@" in u:
            try:
                from django.contrib.auth.models import User
                user_obj = User.objects.get(email=u)
                username = user_obj.username
            except User.DoesNotExist:
                return render(request, "auth/restaurant_login.html", {"error": "Invalid username or password"})
        else:
            username = u

        user = authenticate(request, username=username, password=p)

        if not user:
            return render(request, "auth/restaurant_login.html",
                          {"error": "Invalid username or password"})

        # Verify role
        if not hasattr(user, "userrole") or user.userrole.role != "restaurant":
            return render(request, "auth/restaurant_login.html",
                          {"error": "This is not a restaurant account"})

        login(request, user)
        return redirect("/dashboard/restaurant/")

    return render(request, "auth/restaurant_login.html")

def volunteer_register(request):
    if request.method == "POST":
        u = request.POST["username"]
        e = request.POST["email"]
        p1 = request.POST["password1"]
        p2 = request.POST["password2"]

        if p1 != p2:
            return render(request, "auth/volunteer_register.html",
                          {"error": "Passwords do not match"})

        if User.objects.filter(username=u).exists():
            return render(request, "auth/volunteer_register.html",
                          {"error": "Username already taken"})

        if User.objects.filter(email=e).exists():
            return render(request, "auth/volunteer_register.html",
                          {"error": "Email already registered"})


        # Get extra fields
        full_name = request.POST.get("full_name", "")
        age = request.POST.get("age", "")
        address = request.POST.get("address", "")
        city = request.POST.get("city", "")
        phone = request.POST.get("phone", "")
        aadhar_card = request.POST.get("aadhar_card", "")
        profile_photo = request.FILES.get("profile_photo")

        # Aadhaar verification placeholder (to be implemented)
        # is_verified = verify_aadhaar_with_uidai(aadhar_card)
        is_verified = False  # Default to False until implemented

        # Create USER
        user = User.objects.create_user(username=u, email=e, password=p1)

        # Assign ROLE
        UserRole.objects.create(user=user, role="volunteer")

        # Create volunteer profile
        VolunteerProfile.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            area=f"{address}, {city}" if city else address,
            profile_photo=profile_photo,
            aadhar_card=aadhar_card,
            aadhar_verified=is_verified,
        )

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "auth/volunteer_register.html")

def volunteer_login(request):
    if request.method == "POST":
        u = request.POST["username"]
        p = request.POST["password"]

        user = authenticate(request, username=u, password=p)

        if not user:
            return render(request, "auth/volunteer_login.html",
                          {"error": "Invalid username or password"})

        if not hasattr(user, "userrole") or user.userrole.role != "volunteer":
            return render(request, "auth/volunteer_login.html",
                          {"error": "This account is not a Volunteer account"})

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "auth/volunteer_login.html")

def ngo_register(request):
    if request.method == "POST":
        u = request.POST["username"]
        e = request.POST["email"]
        p1 = request.POST["password1"]
        p2 = request.POST["password2"]

        if p1 != p2:
            return render(request, "auth/ngo_register.html",
                          {"error": "Passwords do not match"})

        if User.objects.filter(username=u).exists():
            return render(request, "auth/ngo_register.html",
                          {"error": "Username already taken"})

        if User.objects.filter(email=e).exists():
            return render(request, "auth/ngo_register.html",
                          {"error": "Email already registered"})


        name = request.POST.get("name", "")
        contact_person = request.POST.get("contact_person", "")
        phone = request.POST.get("phone", "")
        address = request.POST.get("address", "")
        city = request.POST.get("city", "")

        user = User.objects.create_user(username=u, email=e, password=p1)
        UserRole.objects.create(user=user, role="ngo")
        NGOProfile.objects.create(
            user=user,
            name=name,
            contact_person=contact_person,
            phone=phone,
            address=address,
            city=city
        )

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "auth/ngo_register.html")

def ngo_login(request):
    if request.method == "POST":
        u = request.POST["username"]
        p = request.POST["password"]

        user = authenticate(request, username=u, password=p)

        if not user:
            return render(request, "auth/ngo_login.html",
                          {"error": "Invalid username or password"})

        if not hasattr(user, "userrole") or user.userrole.role != "ngo":
            return render(request, "auth/ngo_login.html",
                          {"error": "This account is not an NGO account"})

        login(request, user)
        return redirect("/dashboard/")

    return render(request, "auth/ngo_login.html")

# ==========================================
# DASHBOARD REDIRECTOR
# ==========================================
@login_required(login_url="/")   # if NOT logged in → redirect to homepage
def dashboard_redirect(request):
    """Send logged-in user to the correct dashboard based on role."""

    role = request.user.userrole.role  # get assigned role

    if role == "restaurant":
        return redirect("/dashboard/restaurant/")

    elif role == "volunteer":
        return redirect("/dashboard/volunteer/")

    elif role == "ngo":
        return redirect("/dashboard/ngo/")

    # fallback in case role missing
    return redirect("/")

def logout_view(request):
    logout(request)
    return redirect("/")