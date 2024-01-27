from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views.auth import *
from api.views.gpt import *

from api.views.gpt import GPTChatAPIView
from api.views.auth import (
    UserCreateAPIView,
    SendEmailAPIView,
    ConfirmEmailAPIView,
    GoogleLoginCallbackView
)

urlpatterns = [
    path('rest/', include('rest_framework.urls')),
    path('auth/', include('social_django.urls', namespace='social')),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('gpt-chat/', GPTChatAPIView.as_view()),

    path('pre-email-confirmation/', SendEmailAPIView.as_view()),
    path('confirm-email/', ConfirmEmailAPIView.as_view()),

    path("register/", UserCreateAPIView.as_view()),
    path("profile/", UserProfileUpdateAPIView.as_view()),
    path("profile/password/", UserPasswordEditAPIView.as_view()),
]

