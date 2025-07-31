from django.urls import path
from .views import UserRegistrationView, LoginView, LogoutView, UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
]