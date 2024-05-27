import os
import django
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, Channel
from telethon.tl.functions.channels import JoinChannelRequest
from datetime import datetime, timezone
import telebot
from telebot import types

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diplom.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from saite.models import TelegramGroup
from telegram_auth.models import TelegramProfile, ParserSetting


async def is_recent_message(message):
    now = datetime.now(timezone.utc)
    date = message.date.replace(tzinfo=timezone.utc)
    time_difference = (now - date).total_seconds()
    return time_difference < 30


api_id = 12075432
api_hash = 'f5196f6b68ad458d236ad501c4d90a95'
TOKEN = '6794656536:AAHRrqdax_iANoWmeAeMbX6C_YomWgWxsDw'
bot = telebot.TeleBot(TOKEN)

client = TelegramClient('session_name', api_id, api_hash, system_version="4.16.30-vxCUSTOM")

calendar_button = types.InlineKeyboardButton('Добавить событие в Google Календарь',
                                             callback_data='add_event_to_google_calendar')
keyboard = types.InlineKeyboardMarkup()
keyboard.add(calendar_button)


async def join_channels():
    channels = list(TelegramGroup.objects.all().values_list('channel_id', flat=True))
    for channel_id in channels:
        await join_channel(channel_id)


async def join_channel(channel_id):
    try:
        await client(JoinChannelRequest(channel_id))
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await client(JoinChannelRequest(channel_id))


# @bot.callback_query_handler(func=lambda call: call.data.startswith('add_event_to_google_calendar'))
# def add_event_to_google_calendar_callback(call):
# chat_id = call.message.chat.id
# bot.send_message(chat_id, "Кнопка работает")


async def normal_handler(event):
    if not await is_recent_message(event.message):
        return
    msg = event.message.text
    chan_id = event.chat_id
    chan_id_full = chan_id
    if isinstance(chan_id, int):
        media = event.message.media
        file_path = None

        try:
            telegram_group = TelegramGroup.objects.get(channel_id=chan_id_full)
        except TelegramGroup.DoesNotExist:
            return

        parsers = ParserSetting.objects.filter(city=telegram_group.city)

        for parser in parsers:
            keywords = parser.keywords.split(',')
            found_keywords = [word.strip() for word in keywords if word.strip().casefold() in msg.casefold()]

            if found_keywords:
                keywords_str = ', '.join(found_keywords)
                text_msg = (f"Сообщение из канала {telegram_group.group_tag}:\n\n{msg}\n\n"
                            f"Найдено по ключевым словам: {keywords_str}\n")
                chat_id = parser.user.telegram_profile.chat_id

                try:
                    if media:
                        if isinstance(media, MessageMediaPhoto):
                            file_path = await event.message.download_media()
                            with open(file_path, 'rb') as photo:
                                bot.send_photo(chat_id, photo, caption=text_msg, reply_markup=keyboard)
                            os.remove(file_path)
                        elif isinstance(media, MessageMediaDocument):
                            file_path = await event.message.download_media()
                            with open(file_path, 'rb') as video:
                                bot.send_video(chat_id, video, caption=text_msg, reply_markup=keyboard)
                            os.remove(file_path)
                    else:
                        bot.send_message(chat_id, text_msg, reply_markup=keyboard)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
                    if media:
                        if isinstance(media, MessageMediaPhoto):
                            file_path = await event.message.download_media()
                            with open(file_path, 'rb') as photo:
                                bot.send_photo(chat_id, photo, caption=text_msg, reply_markup=keyboard)
                            os.remove(file_path)
                        elif isinstance(media, MessageMediaDocument):
                            file_path = await event.message.download_media()
                            with open(file_path, 'rb') as video:
                                bot.send_video(chat_id, video, caption=text_msg, reply_markup=keyboard)
                            os.remove(file_path)
                    else:
                        bot.send_message(chat_id, text_msg, reply_markup=keyboard)


async def check_new_groups():
    while True:
        try:
            if client.is_connected():
                current_channels = set(TelegramGroup.objects.all().values_list('channel_id', flat=True))
                subscribed_channels = set(
                    [dialog.entity.id for dialog in await client.get_dialogs() if isinstance(dialog.entity, Channel)])

                new_channels = current_channels - subscribed_channels

                for channel_id in new_channels:
                    await join_channel(channel_id)
        except RpcCallFailError as e:
            await asyncio.sleep(60)
        except Exception as e:
            print(f"Возникла ошибка: {e}")

        await asyncio.sleep(60)


async def main():
    await client.start()
    await join_channels()
    await check_new_groups()
    await client.run_until_disconnected()


if __name__ == '__main__':
    client.add_event_handler(normal_handler, events.NewMessage())
    asyncio.run(main())
