from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import ProjectViewSet, ListNotificationView

router = DefaultRouter()

router.register("projects", ProjectViewSet, basename="projects")
router.register("notifications", ListNotificationView, basename="user-notification")

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls

app_name = "user"
