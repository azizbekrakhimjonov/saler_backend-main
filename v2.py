from aiogram import Bot, Dispatcher, executor, types
import requests
import logging
TOKEN = "7832802417:AAHd6atjmzCKdx4IgnOJLB7EIsvUrP9Mu7U"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print('bot started')
    telegram_id = message.from_user.id
    url = 'https://hipad.uz/api/register/'

    data = {
            "telegram_id": f'{telegram_id}',
        }
    response = requests.post(url, json=data)
    print("Status code:", response.status_code)
    print("Response data:", response.json())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)



