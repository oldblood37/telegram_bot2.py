# telegram_auth/views.py
import json
from django.shortcuts import render
import logging
import secrets
import hashlib
import requests
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.apps import AppConfig
from django.core.signals import request_started
from django.contrib.auth import login
from django.shortcuts import redirect
from .models import TelegramProfile, UserLogin, ParserSetting
from saite.models import City, TelegramGroup  # Импорт моделей из saite
from django.contrib.auth.models import User
import secrets
from django.dispatch import receiver
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def logout_view(request):
    logout(request)
    return redirect('/')


class TelegramAuthConfig(AppConfig):
    name = 'telegram_auth'

    def ready(self):
        request_started.connect(set_webhook)


@receiver(request_started)
def set_webhook(**kwargs):
    print("Setting webhook...")
    try:
        response = requests.post(f"{TELEGRAM_API}{TELEGRAM_TOKEN}/setWebhook", data={'url': WEBHOOK_URL})
        logger.info("Webhook set successfully. Response: %s", response.json())
    except Exception as e:
        logger.error("Error setting webhook: %s", e)


TELEGRAM_API = 'https://api.telegram.org/bot'
TELEGRAM_TOKEN = '6794656536:AAHRrqdax_iANoWmeAeMbX6C_YomWgWxsDw'
WEBHOOK_URL = 'https://7f8c-178-76-218-138.ngrok-free.app/telegram-webhook'
BASE_URL = WEBHOOK_URL.rsplit('/', 1)[0]


def send_telegram_message(chat_id, text):
    send_url = f'{TELEGRAM_API}{TELEGRAM_TOKEN}/sendMessage'
    response = requests.post(send_url, data={'chat_id': chat_id, 'text': text})
    logger.info(f"Message send attempt to chat_id {chat_id} with response: {response.json()}")


def generate_and_save_user_token(telegram_profile):
    salt = secrets.token_hex(16)
    data_to_hash = f"{telegram_profile.chat_id}{salt}"
    token = hashlib.sha256(data_to_hash.encode()).hexdigest()
    telegram_profile.token = token
    telegram_profile.save()
    return token


def get_user_by_chat_id(chat_id):
    try:
        telegram_profile = TelegramProfile.objects.get(chat_id=chat_id)
        return telegram_profile.user
    except TelegramProfile.DoesNotExist:
        return None


def send_welcome_message(chat_id):
    welcome_text = (
        "Привет! 👋 Я твой помощник в поиске интересных мероприятий в Телеграм. "
        "На сайте ты сможешь настроить меня, чтобы я автоматически искал для тебя мероприятия и многое другое.\n\n"
        "Чтобы начать, зарегистрируйся на нашем сайте и настрой свои предпочтения поиска. "
        "Я буду присылать тебе уведомления о новых событиях, чтобы ты всегда был в курсе происходящего! 🎉\n\n"
        "Чтобы войти на сайт, используй команду /vhod."
    )
    send_telegram_message(chat_id, welcome_text)


@require_POST
@csrf_exempt
def update_parser_settings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Пользователь не аутентифицирован'}, status=403)

    user = request.user
    custom_settings = request.POST.get('custom-settings-checkbox') == 'on'
    city_id = request.POST.get('city')
    keywords = request.POST.get('keywords')
    excludes = request.POST.get('excludes')
    groups = request.POST.get('groups')

    # Удаляем старые настройки
    ParserSetting.objects.filter(user=user).delete()

    if custom_settings:
        print("proverka")
        # Создаем настройки с кастомными параметрами и пустым значением для города
        parser = ParserSetting.objects.create(
            user=user,
            city=None,
            keywords=keywords,
            excludes=excludes,
            groups=groups,
        )
    else:
        if not city_id:
            return JsonResponse({'status': 'error', 'message': 'Город не указан'}, status=400)

        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Некорректный город'}, status=400)

        # Создаем новые настройки с указанным городом
        parser = ParserSetting.objects.create(
            user=user,
            city=city,
            keywords=keywords,
            excludes=excludes,
        )

    message = "Настройки парсера обновлены."
    if custom_settings:
        message += f" Ключевые слова: {keywords}, исключающие слова: {excludes}, группы: {groups}."
    else:
        message += f" Город: {city.name}, ключевые слова: {keywords}, исключающие слова: {excludes}."

    telegram_profile = TelegramProfile.objects.get(user=user)
    send_telegram_message(telegram_profile.chat_id, message)

    return JsonResponse({'status': 'success', 'message': message})








@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', {})

        if 'text' in message:
            chat_id = message['chat']['id']
            message_text = message['text']
            first_name = message['from'].get('first_name', '')

            if 'text' in message and message['text'] == '/start':
                send_welcome_message(chat_id)

            if message_text == '/vhod':
                username = f"tg_{chat_id}"
                user, user_created = User.objects.get_or_create(username=username)

                if user_created:
                    user.set_password(secrets.token_urlsafe(16))  # Установка безопасного пароля
                user.first_name = first_name  # Обновляем имя при каждом входе
                user.save()

                telegram_profile, profile_created = TelegramProfile.objects.get_or_create(
                    user=user,
                    defaults={'chat_id': chat_id}
                )

                secure_token = generate_and_save_user_token(telegram_profile)
                login_url = f'{BASE_URL}/login/?token={secure_token}'
                send_telegram_message(chat_id, f'Используйте эту ссылку для входа на сайт: {login_url}')
                return JsonResponse({'status': 'success'})

        return JsonResponse({})
    else:
        return HttpResponseNotAllowed(['POST'])


def login_by_token(request):
    token = request.GET.get('token')
    if not token:
        return HttpResponse('Токен не предоставлен', status=400)

    try:
        telegram_profile = TelegramProfile.objects.get(token=token)
        user = telegram_profile.user
        login(request, user)  # Аутентификация пользователя
        UserLogin.objects.create(user=user)  # Создание записи о входе ТОЛЬКО после успешного входа
        return redirect('/')  # Перенаправление на главную страницу
    except TelegramProfile.DoesNotExist:
        return HttpResponse('Неверный токен', status=400)


