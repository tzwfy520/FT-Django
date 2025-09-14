from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIAnalysisRecordViewSet, AIModelConfigViewSet

app_name = 'ai_records'

router = DefaultRouter()
router.register(r'analysis-records', AIAnalysisRecordViewSet, basename='analysis-records')
router.register(r'model-configs', AIModelConfigViewSet, basename='model-configs')

urlpatterns = [
    path('api/', include(router.urls)),
]