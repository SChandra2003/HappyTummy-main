from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from donations import auth_views
from donations import dashboard_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path("restaurant/login/", auth_views.restaurant_login, name="restaurant_login"),
    path("restaurant/register/", auth_views.restaurant_register, name="restaurant_register"),
    path("volunteer/login/", auth_views.volunteer_login, name="volunteer_login"),
    path("volunteer/register/", auth_views.volunteer_register, name="volunteer_register"),
    path("ngo/login/", auth_views.ngo_login, name="ngo_login"),
    path("ngo/register/", auth_views.ngo_register, name="ngo_register"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("dashboard/", auth_views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/restaurant/", dashboard_views.restaurant_dashboard, name="restaurant_dashboard"),
    path("dashboard/volunteer/", dashboard_views.volunteer_dashboard, name="volunteer_dashboard"),
    path("dashboard/ngo/", dashboard_views.ngo_dashboard, name="ngo_dashboard"),
    path("api/volunteer/location/update/", dashboard_views.volunteer_location_update, name="volunteer_location_update"),
    path("api/ngo/live-volunteers/", dashboard_views.ngo_live_volunteer_locations, name="ngo_live_volunteer_locations"),
    path("donations/", include("donations.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    path("restaurant/login/", auth_views.restaurant_login, name="restaurant_login"),
