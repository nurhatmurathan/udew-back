from django.urls import include, path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from api.views.auth import *
from api.views.gpt import *

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('gpt-chat/', GPTChatAPIView.as_view()),

    path('register/', UserCreateCreateAPIView.as_view()),
    path('profile/', UserProfileUpdateAPIView.as_view()),

]
