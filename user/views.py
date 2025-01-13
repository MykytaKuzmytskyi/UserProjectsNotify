from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import Project, NotificationTemplate, UserNotification
from user.notification import NotificationService
from user.serializers import ProjectSerializer, UserNotificationSerializer, UpdateStatusSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        try:
            project = serializer.save()
            if project.user:
                notification_template = get_object_or_404(NotificationTemplate, id=1)
                NotificationService.create_notification(
                    user=project.user,
                    notification_template=notification_template,
                    options=[
                        {"field_id": 1, "txt": f"{project.id}"},
                        {"field_id": 2, "txt": f"{project.name}"}
                    ]
                )
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListNotificationView(mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'notification_type', 'notification_template__id']

    def get_queryset(self):
        return (
            UserNotification.objects
            .select_related('notification_template')
            .filter(user=self.request.user)
        )

    @action(detail=False, methods=['patch'])
    def update_status(self, request, *args, **kwargs):
        serializer = UpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data['notification_ids']
        new_status = serializer.validated_data['new_status']

        try:
            updated_count = NotificationService.update_notification_status(notification_ids, new_status)
            return Response({'success': True, 'updated_count': updated_count})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
