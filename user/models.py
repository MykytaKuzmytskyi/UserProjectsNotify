from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=25, blank=True, null=True)
    code = models.CharField(max_length=5, blank=True, null=True)
    code_exp = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        db_table = 'country'


class Language(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    title = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'language'

    def __str__(self):
        return f"ID-{self.id}: {self.name}"


class NotificationCategory(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    title = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'notification_category'


class NotificationTemplate(models.Model):
    notification_category = models.ForeignKey(NotificationCategory, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    txt = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'notification_template'


class TranslationString(models.Model):
    content_type = models.ForeignKey(ContentType, models.DO_NOTHING, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    related_item = GenericForeignKey("content_type", "object_id")

    translation_field_id = models.IntegerField(blank=True, null=True)
    language = models.ForeignKey(Language, models.DO_NOTHING, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'translation_string'


class User(AbstractUser):
    role_id = models.PositiveIntegerField(blank=True, null=True)
    verified = models.IntegerField(blank=True, null=True)
    language = models.ForeignKey(Language, models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'user'


class UserNotification(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    notification_template = models.ForeignKey(NotificationTemplate, models.DO_NOTHING, blank=True, null=True)
    notification_type = models.IntegerField()
    status = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'user_notification'

    def get_processed_translation(self):
        translation = TranslationString.objects.filter(
            object_id=self.notification_template.id,
            language=self.user.language
        ).first() or TranslationString.objects.filter(
            object_id=self.notification_template.id,
            language__title='EN'
        ).first()

        if not translation:
            return "Translation missing"

        options = UserNotificationOption.objects.filter(user_notification=self).values('field_id', 'txt')
        translation_text = translation.text

        for option in options:
            placeholder = f"{{{option['field_id']}}}"
            translation_text = translation_text.replace(placeholder, option['txt'])

        if translation.language.title != self.user.language.title:
            translation_text += " (translation missing, English version used)"

        return translation_text


class UserNotificationOption(models.Model):
    user_notification = models.ForeignKey(UserNotification, models.DO_NOTHING, blank=True, null=True)
    field_id = models.IntegerField(blank=True, null=True)
    txt = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'user_notification_option'


class UserNotificationSetting(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    notification_template = models.ForeignKey(NotificationTemplate, models.DO_NOTHING, blank=True, null=True)
    system_notification = models.IntegerField()
    push_notification = models.IntegerField()

    class Meta:
        db_table = 'user_notification_setting'


class UserRole(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'user_role'


class Project(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=510, blank=True, null=True)
    address = models.CharField(max_length=510, blank=True, null=True)
    started = models.DateTimeField()
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    country = models.ForeignKey(Country, models.DO_NOTHING)
    archived = models.IntegerField()

    class Meta:
        db_table = 'project'
