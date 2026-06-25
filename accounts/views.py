from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from generator.models import InterviewSession
from .forms import ProfilePictureForm
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db.models import Count

from django.core.mail import send_mail
from django.conf import settings
import random


def send_otp(email, otp, subject="Your AI Interview – Email Verification Code"):
    send_mail(
        subject = subject,
        message = (
            f"Hello, \n\n"
            f"Your Verification code is: {otp}\n\n"
            f"This code expires in 10 minutes. Do not share it with anyone.\n\n"
            f"– AI Interview Question Generator"
        ),
        from_email = settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validations
        if password != confirm_password:
            return render(request, "register.html", {"error":"Passwords do not match."})
        
        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error":"Email already registered."})
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))

        request.session["pending_registration"] = {
            "fullname":fullname,
            "email":email,
            "password":password,
            "otp":otp
        }

        try:
            send_otp(email, otp)
        except Exception as e:
            return render(request, "register.html", {"error":f"Could not send verification email. Please check your email address. ({e})"})
        
        return redirect("verify_email")

    return render(request, "register.html")

def verify_email(request):
    pending = request.session.get("pending_registration")

    if not pending:
        return redirect("register")
    
    if request.method == "POST":
        entered_otp = request.POST.get("otp","").strip()

        if entered_otp == pending["otp"]:
            user = User.objects.create_user(
                username = pending["email"],
                first_name = pending["fullname"],
                email = pending["email"],
                password = pending["password"],
            )

            del request.session["pending_registration"]

            login(request, user)

            return redirect("dashboard")
        else:
            return render(request, "verify_email.html", {"email":pending["email"], "error":"Invalid verification code. Please try again.",})
        
    return render(request, "verify_email.html", {"email": pending["email"]})

def resend_otp(request):
    pending = request.session.get("pending_registration")

    if not pending:
        return redirect("register")
    
    otp = str(random.randint(100000, 999999))
    pending["otp"] = otp
    request.session["pending_registration"] = pending

    try:
        send_otp(pending["email"], otp)
        return render(request, "verify_email.html", {
            "email":   pending["email"],
            "success": "A new verification code has been sent to your email.",
        })
    except Exception as e:
        return render(request, "verify_email.html", {
            "email": pending["email"],
            "error": f"Could not resend code. ({e})",
        })

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {
                "error":"Invalid username or password"
            })

    return render(request,"login.html")

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not User.objects.filter(email=email).exists():
            return render(request, "forgot_password.html", {"error": "No account found with that email address."})
        
        otp = str(random.randint(100000, 999999))
        request.session["password_reset"] = {
            "email":email,
            "otp":otp,
            "verified":False
        }

        try:
            send_otp(email, otp, subject="Your AI Interview – Password Reset Code")
        except Exception as e:
            return render(request, "forgot_password.html", {
                "error": f"Could not send email. Please try again. ({e})"
            })
        
        return redirect("verify_reset_otp")
    return render(request, "forgot_password.html")

def verify_reset_otp(request):
    reset_data = request.session.get("password_reset")

    if not reset_data:
        return redirect("forgot_password")
    
    if request.method == "POST":
        entered = request.POST.get("otp","").strip()

        if entered == reset_data["otp"]:
            reset_data["verified"] = True
            request.session["password_reset"] = reset_data

            return redirect("reset_password")
        
        else:
            return render(request, "verify_reset_otp.html", {
                "email": reset_data["email"],
                "error": "Invalid code. Please try again.",
            })
        
    return render(request, "verify_reset_otp.html", {"email": reset_data["email"]})


def resend_reset_otp(request):
    reset_data = request.session.get("password_reset")

    if not reset_data:
        return redirect("forgot_password")
    
    otp = str(random.randint(100000, 999999))

    reset_data["otp"] = otp
    reset_data["verified"] = False
    request.session["password_reset"] =reset_data

    try:
        send_otp(reset_data["email"], otp, subject="Your AI Interview – Password Reset Code")
        return render(request, "verify_reset_otp.html", {
            "email":   reset_data["email"],
            "success": "A new reset code has been sent to your email.",
        })
    
    except Exception as e:
        return render(request, "verify_reset_otp.html", {
            "email": reset_data["email"],
            "error": f"Could not resend code. ({e})",
        })
    

def reset_password(request):
    reset_data = request.session.get("password_reset")

    if not reset_data or not reset_data.get("verified"):
        return redirect("forgot_password")
    
    if request.method == "POST":
        new_password = request.POST.get("new_password","")
        confirm_password = request.POST.get("confirm_password","")

        if len(new_password) < 8:
            return render(request, "reset_password.html", {
                "error": "Password must be at least 8 characters."
            })
        
        if new_password != confirm_password:
            return render(request, "reset_password.html", {
                "error": "Passwords do not match."
            })
        
        try:
            user = User.objects.get(email=reset_data["email"])
            user.set_password(new_password)
            user.save()

        except User.DoesNotExist:
            return redirect("forgot_password")
        
        del request.session["password_reset"]

        return render(request, "reset_password.html", {"done": True})
 
    return render(request, "reset_password.html")

@login_required
def dashboard(request):
    sessions = InterviewSession.objects.filter(user=request.user)

    tot_sessions = sessions.count()

    tot_ques = sum(s.no_of_ques for s in sessions)

    favourite_role_obj = (
        sessions.values("role").annotate(count = Count("role")).order_by("-count").first()
    )

    favourite_role = favourite_role_obj["role"] if favourite_role_obj else "N/A"

    recent_session = sessions.order_by("-created_at")[:5]

    context = {
        "tot_sessions":tot_sessions,
        "tot_ques":tot_ques,
        "fav_role":favourite_role,
        "recent_sessions":recent_session
    }

    return render(request, "dashboard.html", context)

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile(request):
    sessions = InterviewSession.objects.filter(user = request.user)

    total_sessions = sessions.count()

    total_questions = sum(n.no_of_ques for n in sessions)

    recent_session = sessions.order_by('-created_at')[:5]

    context = {
        "total_sessions":total_sessions,
        "total_questions":total_questions,
        "recent_sessions":recent_session
    }

    return render(request, "profile.html", context)

@login_required
def change_profile_picture(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, "change_profile_pic.html", {"form":form})

@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = request.user

        if not user.check_password(current_password):
           return JsonResponse({
               "success":False,
               "message": "Current password is incorrect."
           })

        elif new_password != confirm_password:
            return JsonResponse({
                "success": False,
                "message": "New password and confirm password do not match."
            })
        
        else:
            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return JsonResponse({
                "success": True,
                "message": "Password changed successfully."
            })

    return redirect("profile")