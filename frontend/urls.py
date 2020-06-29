from django.urls import path
from frontend import views


urlpatterns = [
    path("", views.HomePage.as_view(), name="f_home_page"),
    path("about-us/", views.AboutPage.as_view(), name="f_about_us"),
    path("learn-more/", views.LearMorePage.as_view(), name="f_lean_more"),
    path("user/login/", views.UserLogin.as_view(), name="user_login"),
    path("user/logout/", views.UserLogout.as_view(), name="user_logout"),
    path("user/signup/<int:url>/", views.UserRegistration.as_view(), name="user_signup"),
    path("user/forgot-password/", views.ForgetPassword.as_view(), name="forgot_password"),
    path("user/recover-password/<int:url>/", views.PasswordRecovery.as_view(), name="password_recovery"),
    path("user/profile/", views.UserProfile.as_view(), name="user_profile"),
    path("user/leader-board/", views.UserLeaderBoard.as_view(), name="leader_board"),
    path("user/tree/", views.UserTree.as_view(), name="tree"),
    path("user/wallet/", views.UserWallet.as_view(), name="wallet"),
]
