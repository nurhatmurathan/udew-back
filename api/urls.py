from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views.chat import MessageAPIView, ChatLastMessageAPIView, DefaultMessageAPIView

from api.views.compensation import ApplicationCompensationListCreateView
from api.views.gpt import GPTChatAPIView
from api.views.confirmation import (
    SendEmailAPIView,
    ConfirmEmailAPIView,
)
from api.views.user import (
    UserCreateAPIView,
    UserProfileRetrieveUpdateAPIView,
    UserPasswordEditAPIView
)

from api.views.ministry_of_health_api import DataSetOfInsuranceCards


urlpatterns = [
    path('rest/', include('rest_framework.urls')),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('gpt-chat/', GPTChatAPIView.as_view()),

    path('pre-email-confirmation/', SendEmailAPIView.as_view()),
    path('confirm-email/', ConfirmEmailAPIView.as_view()),

    # path('pre-phone-number-confirmation', SendCodeAPIView.as_view()),

    path("register/", UserCreateAPIView.as_view()),
    path("profile/", UserProfileRetrieveUpdateAPIView.as_view()),
    path("profile/password/", UserPasswordEditAPIView.as_view()),

    path("chat/", MessageAPIView.as_view()),
    path("chat/default-messages/", DefaultMessageAPIView.as_view()),
    path("chat/answer/<str:run_id>/", ChatLastMessageAPIView.as_view()),

    path("compensation/", ApplicationCompensationListCreateView.as_view()),

    path('insurance-cards/', DataSetOfInsuranceCards.as_view()),
    path('insurance-cards/<str:iin>/', DataSetOfInsuranceCards.as_view()),
]
