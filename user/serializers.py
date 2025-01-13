from django.utils.timezone import localtime
from rest_framework import serializers

from user.models import Project, UserNotification


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class UserNotificationSerializer(serializers.ModelSerializer):
    notification_template_name = serializers.CharField(
        source="notification_template.name", read_only=True
    )
    iso_time_created = serializers.SerializerMethodField()
    txt = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            "id",
            "notification_template_name",
            "notification_type",
            "status",
            "iso_time_created",
            "txt",
        ]

    @staticmethod
    def get_iso_time_created(obj):
        return localtime(obj.created).isoformat()

    @staticmethod
    def get_txt(obj):
        notification_template = obj.notification_template
        if (
            hasattr(notification_template, "prefetched_translations")
            and notification_template.prefetched_translations
        ):
            translation = notification_template.prefetched_translations[0]
            translation_text = translation.text
        else:
            translation_text = notification_template.txt

        options = obj.usernotificationoption_set.values("field_id", "txt")
        for option in options:
            placeholder = f"{{{option['field_id']}}}"
            translation_text = translation_text.replace(placeholder, option["txt"])

        return translation_text


class UpdateStatusSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        error_messages={"required": 'The "notification_ids" field is required.'},
    )
    new_status = serializers.ChoiceField(
        choices=[0, 1],
        required=True,
        error_messages={"invalid_choice": '"new_status" must be either 0 or 1.'},
    )
