from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ApiProviderViewSet, ApiTokenViewSet, ApiInterfaceViewSet,
    ApiCallLogViewSet, ApiCallViewSet, CSRFTokenView
)
from .auth_views import LoginView, LogoutView, UserInfoView, RegisterView

router = DefaultRouter()
router.register(r'providers', ApiProviderViewSet)
router.register(r'tokens', ApiTokenViewSet, basename='apitoken')
router.register(r'interfaces', ApiInterfaceViewSet, basename='apiinterface')
router.register(r'logs', ApiCallLogViewSet, basename='apicalllog')
router.register(r'call', ApiCallViewSet, basename='apicall')

urlpatterns = [
    path('', include(router.urls)),
    # CSRF token endpoint
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf_token'),
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),
    path('auth/user/', UserInfoView.as_view(), name='api_user_info'),
    path('auth/register/', RegisterView.as_view(), name='api_register'),
]