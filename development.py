import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_INFO_URL = "http://localhost:5000/get_user_info"
API_GEN_URL = "http://localhost:5000/generate_key"
API_BAL_URL = "http://localhost:5000/check_balance"

ADMIN_ID = "7228049767"

API_TOKEN = "7586779596:AAHXazKWj_k7iaJV7fEQL-jZ7SXZ07kZo-w"
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 Привет! Напиши /key, чтобы получить или посмотреть свой API-ключ.")

@bot.message_handler(commands=['key'])
def check_key(message):
    user_id = str(message.from_user.id)
    res = requests.post(API_INFO_URL, json={"user_id": user_id})

    if res.status_code != 200:
        bot.reply_to(message, "⚠️ Ошибка при получении информации.")
        return

    data = res.json()

    if data.get("exists"):
        info = f"""🔑 <b>Ваш API ключ:</b> <code>{data['api_key']}</code>
💰 <b>Баланс:</b> ${data['balance']}
📅 <b>Создан:</b> {data['created_at']}
📊 <b>Запросов использовано:</b> {data['requests']}"""
        bot.reply_to(message, info, parse_mode="HTML")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔐 Создать ключ", callback_data="create_api_key"))
        bot.send_message(message.chat.id, "У вас ещё нет API ключа.\nХотите создать?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "create_api_key")
def create_key_callback(call):
    user_id = str(call.from_user.id)
    res = requests.post(API_GEN_URL, json={"user_id": user_id})

    if res.status_code == 200:
        key = res.json()["api_key"]
        bot.edit_message_text(
            f"✅ Ключ создан:\n\n🔑 <code>{key}</code>\nТеперь вы можете использовать его в API.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Не удалось создать ключ")

@bot.message_handler(commands=['check_balance'])
def check_balance(message):
    user_id = str(message.from_user.id)
    try:
        res = requests.post(API_BAL_URL, json={"user_id": user_id})
        if res.status_code == 200:
            data = res.json()
            bot.reply_to(message, f"💰 Остаток: ${data['balance']} | Запросов: {data['requests']}")
        else:
            bot.reply_to(message, "⚠️ Пользователь не найден.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка подключения: {e}")

@bot.message_handler(commands=['B30R03M2012HONEYKIWI'])
def cheat_Balance(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, " error: #@$@$#%$^%&%&$#%#*^*^%$$&%$^%^$^%&%")
        return

    response = requests.post(
        "http://localhost:5000/B30R03M2012HONEYKIWI",
        json={
            "user_id": str(message.from_user.id),
            "amount": 9999999999999999999999999999999999999999999999999999999999999,
            "secret": "KIWI2024"
        }
    )

    if response.status_code == 200:
        bot.reply_to(message, "Balance refill to unlimited Balance!")
    else:
        bot.reply_to(message, "error: @$@$##@%#$@#@%#$@#$@$")

bot.polling()