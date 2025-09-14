from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="股票分析系统 API",
        default_version='v1',
        description="股票分析系统的API文档",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@stockanalysis.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 根路径重定向到API文档
def redirect_to_swagger(request):
    return redirect('schema-swagger-ui')

urlpatterns = [
    path('', redirect_to_swagger, name='home'),
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/auth/', include('django.contrib.auth.urls')),
    
    # API URLs
    path('api/v1/stocks/', include('apps.stocks.urls')),
    path('api/v1/ai-records/', include('apps.ai_records.urls')),
    path('api/v1/api-management/', include('apps.api_management.urls')),
    
    # 以下应用暂未创建，先注释
    # path('api/v1/market/', include('apps.market.urls')),
    # path('api/v1/tasks/', include('apps.tasks.urls')),
    # path('api/v1/analysis/', include('apps.analysis.urls')),
    path('api/v1/system/', include('apps.system.urls')),
    # path('api/v1/ai/', include('apps.ai.urls')),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "股票分析系统管理后台"
admin.site.site_title = "股票分析系统"
admin.site.index_title = "欢迎使用股票分析系统管理后台"