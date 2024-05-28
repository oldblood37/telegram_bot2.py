from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

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

class News(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field('Text', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title