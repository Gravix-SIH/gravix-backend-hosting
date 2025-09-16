from django.urls import path
from .views import SignupView, LoginView, MeView, UserDetailView, AnonymousSessionView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me', MeView.as_view(), name='user-me'),
    path('users/<uuid:id>', UserDetailView.as_view(), name='user-detail'),
    path('anon', AnonymousSessionView.as_view(), name='anon-session'),

]
