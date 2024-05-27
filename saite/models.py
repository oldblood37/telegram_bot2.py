from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class TelegramGroup(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='telegram_groups')
    group_tag = models.CharField(max_length=255, unique=True)
    channel_id = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.group_tag} ({self.city.name})(id:{self.channel_id})"
