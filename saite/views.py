from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import City, TelegramGroup
from telegram_auth.views import update_parser_settings
from telegram_auth.models import ParserSetting
import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
def main_page(request):
    return render(request, 'main.html')

def news_page(request):
    return render(request, 'news.html')

def about_page(request):
    user_count = User.objects.count()
    city_count = City.objects.count()
    context = {
        'user_count': user_count,
        'city_count': city_count,
    }
    return render(request, 'about.html', context)

from django.shortcuts import render, redirect
from .models import City
from .forms import ParserForm
from django.contrib.auth.decorators import login_required

@login_required
def manage_keywords(request):
    user = request.user
    existing_parser = ParserSetting.objects.filter(user=user).first()
    existing_city = existing_parser.city if existing_parser else None
    existing_keywords = existing_parser.keywords if existing_parser else ""
    existing_excludes = existing_parser.excludes if existing_parser else ""
    existing_groups = existing_parser.groups if existing_parser else ""

    if request.method == 'POST':
        form = ParserForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            keywords = form.cleaned_data['keywords']
            excludes = form.cleaned_data['excludes']
            groups = form.cleaned_data['groups']
            custom_settings = request.POST.get('custom-settings-checkbox')

            logger.debug(f"Received POST data: city={city}, keywords={keywords}, excludes={excludes}, groups={groups}, custom_settings={custom_settings}")

            # Очистка города, если выбраны кастомные настройки
            if custom_settings:
                city = None

            # Удаление старых настроек парсера для данного пользователя
            ParserSetting.objects.filter(user=user).delete()

            # Создание новой настройки парсера
            parser = ParserSetting.objects.create(
                user=user,
                city=city,
                keywords=keywords,
                excludes=excludes,
                groups=groups,
            )

            request._body = json.dumps({
                'city_id': city.id if city else None,
                'keywords': keywords,
                'excludes': excludes,
                'groups': groups,
            }).encode('utf-8')
            response = update_parser_settings(request)

            return redirect('main-page')
    else:
        form = ParserForm(initial={'city': existing_city, 'keywords': existing_keywords, 'excludes': existing_excludes, 'groups': existing_groups})

    cities = City.objects.all()
    return render(request, 'manage_keywords.html', {
        'form': form,
        'cities': cities,
        'keywords': existing_keywords,
        'existing_city': existing_city,
        'excludes': existing_excludes,
        'groups': existing_groups,
    })



def get_groups(request, city_id):
    groups = TelegramGroup.objects.filter(city_id=city_id).values('group_tag')
    return JsonResponse({'groups': list(groups)})