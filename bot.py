import telebot
import schedule
import time
import random
import datetime
import os
from threading import Thread
import google.generativeai as genai
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Настройки API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Проверка наличия обязательных переменных
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Пожалуйста, убедитесь, что TELEGRAM_TOKEN и GEMINI_API_KEY заданы в файле .env")

# Инициализация API Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Инициализация бота Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Словарь для хранения пользователей, которые подписались на рассылку
subscribed_users = {}

# Использование Gemini для генерации мотивационных текстов и пожеланий
def generate_morning_wish():
    prompt = "Напиши короткое и воодушевляющее утреннее пожелание (1-2 предложения). Начни с приветствия 'Доброе утро!'"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при генерации утреннего пожелания: {e}")
        return "Доброе утро! Пусть этот день принесет тебе радость и успех."

def generate_evening_wish():
    prompt = "Напиши короткое и теплое вечернее пожелание (1-2 предложения). Начни с приветствия 'Добрый вечер!'"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при генерации вечернего пожелания: {e}")
        return "Добрый вечер! Пусть этот вечер будет наполнен теплом и уютом."

def generate_motivational_quote():
    prompt = "Напиши мотивирующую цитату с указанием автора (1-2 предложения)."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при генерации мотивационной цитаты: {e}")
        return "Успех — это способность шагать от одной неудачи к другой, не теряя энтузиазма. — Уинстон Черчилль"

def generate_weekly_reflection():
    prompt = "Напиши короткое мотивирующее сообщение о начале новой недели (1-2 предложения)."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при генерации еженедельного сообщения: {e}")
        return "Новая неделя — новые возможности! Что ты хочешь достичь на этой неделе?"

def generate_custom_motivation(topic):
    prompt = f"Напиши короткую мотивационную фразу на тему: {topic} (максимум 2 предложения)"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Ошибка при генерации мотивации по теме '{topic}': {e}")
        return f"Верь в себя! Ты справишься со всем, что связано с '{topic}'."

# Приветственное сообщение при старте бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот ежедневных мотиваций и пожеланий. "
                         "Я буду отправлять тебе мотивирующие сообщения и добрые пожелания каждый день, "
                         "используя технологию Google Gemini. "
                         "Чтобы подписаться, используй команду /subscribe. "
                         "Для получения дополнительной информации используй /help.")

# Обработка команды помощи
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Вот команды, которые ты можешь использовать:
/start - Начать работу с ботом
/help - Показать эту справку
/subscribe - Подписаться на ежедневные сообщения
/unsubscribe - Отписаться от ежедневных сообщений
/motivate - Получить мотивирующую цитату прямо сейчас
/wish - Получить доброе пожелание прямо сейчас
/custom <тема> - Получить мотивацию на указанную тему
/settings - Настройки времени отправки сообщений
    """
    bot.reply_to(message, help_text)

# Подписка на рассылку
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        subscribed_users[user_id] = {
            'morning_time': '08:00',
            'evening_time': '20:00',
            'send_morning': True,
            'send_evening': True,
            'send_motivation': True
        }
        bot.reply_to(message, "Вы успешно подписались на ежедневные мотивационные сообщения! "
                             "По умолчанию вы будете получать утренние пожелания в 08:00 и вечерние в 20:00. "
                             "Для изменения настроек используйте команду /settings.")
    else:
        bot.reply_to(message, "Вы уже подписаны на рассылку. Для изменения настроек используйте команду /settings.")

# Отписка от рассылки
@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    user_id = message.from_user.id
    if user_id in subscribed_users:
        del subscribed_users[user_id]
        bot.reply_to(message, "Вы успешно отписались от рассылки. Если захотите вернуться, используйте команду /subscribe.")
    else:
        bot.reply_to(message, "Вы не были подписаны на рассылку.")

# Немедленная мотивация
@bot.message_handler(commands=['motivate'])
def send_motivation_now(message):
    bot.send_message(message.chat.id, "Генерирую мотивирующую цитату...")
    quote = generate_motivational_quote()
    bot.send_message(message.chat.id, quote)

# Немедленное пожелание
@bot.message_handler(commands=['wish'])
def send_wish_now(message):
    bot.send_message(message.chat.id, "Генерирую пожелание...")
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        wish = generate_morning_wish()
    else:
        wish = generate_evening_wish()
    bot.send_message(message.chat.id, wish)

# Мотивация по заданной теме
@bot.message_handler(commands=['custom'])
def custom_motivation(message):
    try:
        # Извлекаем тему из сообщения (все, что идет после команды /custom)
        topic = message.text.split('/custom', 1)[1].strip()
        if not topic:
            bot.reply_to(message, "Пожалуйста, укажите тему для мотивации. Например: /custom учеба")
            return

        bot.send_message(message.chat.id, f"Генерирую мотивацию на тему '{topic}'...")
        motivation = generate_custom_motivation(topic)
        bot.send_message(message.chat.id, motivation)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите тему для мотивации. Например: /custom спорт")
    except Exception as e:
        print(f"Ошибка в custom_motivation: {e}")
        bot.reply_to(message, "Произошла ошибка при генерации мотивации. Пожалуйста, попробуйте позже.")

# Настройки времени рассылки
@bot.message_handler(commands=['settings'])
def settings(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    settings_text = """
Настройки рассылки:
1. Для установки времени утреннего сообщения отправьте: /set_morning ЧЧ:ММ
2. Для установки времени вечернего сообщения отправьте: /set_evening ЧЧ:ММ
3. Чтобы включить/выключить утренние сообщения: /toggle_morning
4. Чтобы включить/выключить вечерние сообщения: /toggle_evening
5. Чтобы включить/выключить мотивационные цитаты: /toggle_motivation

Текущие настройки:
- Утренние пожелания: {0} ({1})
- Вечерние пожелания: {2} ({3})
- Мотивационные цитаты: {4}
    """.format(
        "включены" if subscribed_users[user_id]['send_morning'] else "выключены",
        subscribed_users[user_id]['morning_time'],
        "включены" if subscribed_users[user_id]['send_evening'] else "выключены",
        subscribed_users[user_id]['evening_time'],
        "включены" if subscribed_users[user_id]['send_motivation'] else "выключены"
    )
    
    bot.reply_to(message, settings_text)

# Установка времени утреннего сообщения
@bot.message_handler(commands=['set_morning'])
def set_morning_time(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    try:
        time_str = message.text.split()[1]
        # Проверка формата времени
        datetime.datetime.strptime(time_str, '%H:%M')
        subscribed_users[user_id]['morning_time'] = time_str
        bot.reply_to(message, f"Время утреннего сообщения установлено на {time_str}.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Пожалуйста, укажите время в формате ЧЧ:ММ. Например: /set_morning 07:30")

# Установка времени вечернего сообщения
@bot.message_handler(commands=['set_evening'])
def set_evening_time(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    try:
        time_str = message.text.split()[1]
        # Проверка формата времени
        datetime.datetime.strptime(time_str, '%H:%M')
        subscribed_users[user_id]['evening_time'] = time_str
        bot.reply_to(message, f"Время вечернего сообщения установлено на {time_str}.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Пожалуйста, укажите время в формате ЧЧ:ММ. Например: /set_evening 20:30")

# Включение/выключение утренних сообщений
@bot.message_handler(commands=['toggle_morning'])
def toggle_morning(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    subscribed_users[user_id]['send_morning'] = not subscribed_users[user_id]['send_morning']
    status = "включены" if subscribed_users[user_id]['send_morning'] else "выключены"
    bot.reply_to(message, f"Утренние сообщения {status}.")

# Включение/выключение вечерних сообщений
@bot.message_handler(commands=['toggle_evening'])
def toggle_evening(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    subscribed_users[user_id]['send_evening'] = not subscribed_users[user_id]['send_evening']
    status = "включены" if subscribed_users[user_id]['send_evening'] else "выключены"
    bot.reply_to(message, f"Вечерние сообщения {status}.")

# Включение/выключение мотивационных цитат
@bot.message_handler(commands=['toggle_motivation'])
def toggle_motivation(message):
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        bot.reply_to(message, "Сначала подпишитесь на рассылку с помощью команды /subscribe.")
        return
    
    subscribed_users[user_id]['send_motivation'] = not subscribed_users[user_id]['send_motivation']
    status = "включены" if subscribed_users[user_id]['send_motivation'] else "выключены"
    bot.reply_to(message, f"Мотивационные цитаты {status}.")

# Обработка неизвестных команд
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Извини, я не понимаю эту команду. Используй /help для получения списка доступных команд.")

# Функция для отправки утренних сообщений
def send_morning_messages():
    current_time = datetime.datetime.now().strftime('%H:%M')
    for user_id, settings in subscribed_users.items():
        if settings['send_morning'] and settings['morning_time'] == current_time:
            try:
                wish = generate_morning_wish()
                bot.send_message(user_id, wish)
                
                # Если включены мотивационные цитаты, отправляем одну из них
                if settings['send_motivation']:
                    time.sleep(2)  # небольшая пауза между сообщениями
                    quote = generate_motivational_quote()
                    bot.send_message(user_id, quote)
                    
                # Проверяем, не понедельник ли сегодня
                if datetime.datetime.now().weekday() == 0:  # 0 - понедельник
                    time.sleep(2)
                    weekly_message = generate_weekly_reflection()
                    bot.send_message(user_id, weekly_message)
            except Exception as e:
                print(f"Ошибка при отправке утреннего сообщения пользователю {user_id}: {e}")

# Функция для отправки вечерних сообщений
def send_evening_messages():
    current_time = datetime.datetime.now().strftime('%H:%M')
    for user_id, settings in subscribed_users.items():
        if settings['send_evening'] and settings['evening_time'] == current_time:
            try:
                wish = generate_evening_wish()
                bot.send_message(user_id, wish)
                
                # Если включены мотивационные цитаты, отправляем одну из них
                if settings['send_motivation']:
                    time.sleep(2)  # небольшая пауза между сообщениями
                    quote = generate_motivational_quote()
                    bot.send_message(user_id, quote)
            except Exception as e:
                print(f"Ошибка при отправке вечернего сообщения пользователю {user_id}: {e}")

# Функция для работы планировщика
def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(30)  # проверка каждые 30 секунд

# Настраиваем планировщик
schedule.every().minute.at(":00").do(send_morning_messages)
schedule.every().minute.at(":00").do(send_evening_messages)

if __name__ == "__main__":
    # Запускаем планировщик в отдельном потоке
    scheduler_thread = Thread(target=schedule_checker)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Запускаем бота
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.polling(none_stop=True)