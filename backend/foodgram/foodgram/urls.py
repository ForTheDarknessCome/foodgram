from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from cooking.views import RecipeGetFullLinkView
from django.conf import settings
from django.conf.urls.static import static

api_patterns = [
    # path('users/', include('account.urls')),
    # path('auth/', include('account.urls')),
    path('', include('account.urls')),
    path('', include('cooking.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    re_path(r'^s/([a-f0-9]{3})/$', RecipeGetFullLinkView.as_view(), name='full-link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

schema_view = get_schema_view(
    openapi.Info(
        title="Agenda API",
        default_version='v1',
        description="Документация для проекта Nex Agenda",
        contact=openapi.Contact(email="i.nuyanzin@yandex.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
]