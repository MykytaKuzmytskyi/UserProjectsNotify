import datetime

from django.db import transaction
from user.models import UserNotificationSetting, UserNotification, UserNotificationOption, User, NotificationTemplate


class NotificationService:
    @staticmethod
    def create_notification(user: User, notification_template: NotificationTemplate, options=None):
        """
        Створює нотифікацію для користувача, якщо вона дозволена в налаштуваннях.

        :param user: екземпляр моделі User
        :param notification_template: екземпляр моделі NotificationTemplate
        :param options: список опцій для нотифікації (UserNotificationOption)
        :return: екземпляр UserNotification або None, якщо нотифікація не створена
        """
        try:
            settings = UserNotificationSetting.objects.get(user=user, notification_template=notification_template)
        except UserNotificationSetting.DoesNotExist:
            return None

        notification_type = None
        if settings.push_notification:
            notification_type = 1
        elif settings.system_notification:
            notification_type = 2
        else:
            return None

        try:
            with transaction.atomic():
                user_notification = UserNotification.objects.create(
                    user=user,
                    notification_template=notification_template,
                    notification_type=notification_type,
                    status=0,
                    created=datetime.datetime.now()
                )

                if options:
                    for option in options:
                        UserNotificationOption.objects.create(
                            user_notification=user_notification,
                            field_id=option.get("field_id"),
                            txt=option.get("txt"),
                        )
            return user_notification
        except Exception as e:
            return None

    @staticmethod
    def update_notification_status(notification_ids: list, new_status: int):
        if not isinstance(new_status, int) or new_status not in [0, 1]:
            raise ValueError("Invalid status value. Status must be 0 or 1.")

        updated_count = UserNotification.objects.filter(id__in=notification_ids).update(status=new_status)
        return updated_count
