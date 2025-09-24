from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("info/", views.api_info, name="api-info"),
    path("ratelimited/", views.ratelimited_view, name="ratelimited"),
    path("time/", views.server_time, name="server-time"),
]
