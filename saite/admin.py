from django.contrib import admin
from .models import City, TelegramGroup

class TelegramGroupInline(admin.TabularInline):  # или admin.StackedInline для другого стиля отображения
    model = TelegramGroup
    extra = 1  # Количество пустых форм для добавления новых групп

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [TelegramGroupInline]


@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    list_display = ('group_tag', 'channel_id', 'city')
    search_fields = ('group_tag', 'city__name')
    list_filter = ('city',)
