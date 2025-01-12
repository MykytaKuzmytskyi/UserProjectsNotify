from rest_framework.routers import DefaultRouter

from user.views import ProjectViewSet

router = DefaultRouter()

router.register("projects", ProjectViewSet, basename="projects")
urlpatterns = router.urls

app_name = "user"
