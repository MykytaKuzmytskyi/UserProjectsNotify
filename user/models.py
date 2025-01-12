from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Language(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    title = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'language'

    def __str__(self):
        return f"ID-{self.id}: {self.name}"


class User(AbstractUser):
    role_id = models.PositiveIntegerField(blank=True, null=True)
    verified = models.IntegerField(blank=True, null=True)
    language = models.ForeignKey(Language, models.DO_NOTHING, null=True)

    class Meta:
        db_table = 'user'
