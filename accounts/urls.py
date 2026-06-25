from django.urls import path
from . import views

urlpatterns = [
    path("register/",views.register, name="register"),
    path("login/",views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("change_profile_pic/", views.change_profile_picture, name="change_profile_pic"),
    path("change_password/", views.change_password, name="change_password"),
    path("verify_email/", views.verify_email, name="verify_email"),
    path("resend_otp/", views.resend_otp, name="resend_otp"),

    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("verify_reset_otp/", views.verify_reset_otp, name="verify_reset_otp"),
    path("resend_reset_otp/", views.resend_reset_otp, name="resend_reset_otp"),
    path("reset_password/", views.reset_password, name="reset_password"),
]