from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    # path('accounts/', include('accounts.urls', namespace='accounts')),
    # path('doctor/', include('doctor.urls', namespace='doctor')),
    # path('admin/', include('adminApp.urls', namespace='adminApp')),
    # path('patient/', include('patient.urls', namespace='patient')),
    path('accounts/', include('accounts.urls')),
    path('doctor/', include('doctor.urls')),
    path('admin/', include('adminApp.urls')),
    path('patient/', include('patient.urls')),
    path('dj-admin/', admin.site.urls),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
