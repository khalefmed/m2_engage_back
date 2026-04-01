from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin

admin.site.site_header = "Marketing Platform Admin"
admin.site.site_title = "Marketing Portal"
admin.site.index_title = "Bienvenue sur le centre de gestion"

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Modules API
    path('api/', include('marketing.urls')), # Auth & Profil
    path('api/clients/', include('clients.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/segments/', include('segments.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/analytics/', include('analytics.urls')),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]