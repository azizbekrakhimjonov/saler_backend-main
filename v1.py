from aiogram import Bot, Dispatcher, executor, types
import aiohttp

url = 'https://4119-188-113-228-231.ngrok-free.app'
# API endpoints
API_URL_REGISTER = f"{url}/api/register/"
API_URL_PROMOCODE = f"{url}/api/code/"
API_URL_PRODUCTS = f"{url}/api/products/"
API_URL_BUY_PRODUCTS = f"{url}/api/buy_product/"
API_URL_CHECK_PHONE = f"{url}/api/phone/"
API_URL_FEEDBACK = f"{url}/api/feedback/"
TOKEN = "7451986125:AAEykGVq6ZNjnUaUZLc8TTof-TN8P8y77K4"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    telegram_id = str(message.from_user.id)

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_REGISTER, json={"telegram_id": telegram_id}) as response:
            if response.status == 200:
                data = await response.json()
                total_points = data.get('points', 0)  # Assuming the API returns the user's points
                await message.answer(
                    f"Assalomu alaykum! Siz avval ro'yxatdan o'tgansiz.\nJami ballaringiz: {total_points}")

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                promocode_button = types.KeyboardButton("Promokod yuborish")
                products_button = types.KeyboardButton("Mahsulotlar")
                feedback_button = types.KeyboardButton("Fikr bildirish")
                order_button = types.KeyboardButton("Buyurtma qilish")
                markup.add(promocode_button, products_button, feedback_button, order_button)
                await message.answer("Iltimos, kerakli tugmani tanlang.", reply_markup=markup)
            else:
                await message.answer("Assalomu alaykum! Telefon raqamingizni kiriting.")
                user_data[message.from_user.id] = {}


@dp.message_handler(lambda message: message.from_user.id in user_data and 'phone_number' not in user_data[message.from_user.id])
async def get_phone(message: types.Message):
    user_data[message.from_user.id]['phone_number'] = message.text
    # Check if the phone number exists in the database
    telegram_id = str(message.from_user.id)
    phone_number = message.text

    payload = {"phone": phone_number}

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_CHECK_PHONE, json=payload) as response:
            if response.status == 200:
                await message.answer("Telefon raqamingiz bazada topildi. Iltimos, manzilingizni kiriting.")
            else:
                await message.answer("Telefon raqamingiz bazada mavjud emas. Iltimos, ro'yxatdan o'ting.")
                user_data.pop(message.from_user.id, None)
                return


@dp.message_handler(lambda message: message.from_user.id in user_data and 'address' not in user_data[message.from_user.id])
async def get_address(message: types.Message):
    user_data[message.from_user.id]['address'] = message.text
    telegram_id = str(message.from_user.id)
    phone_number = user_data[message.from_user.id]['phone_number']
    address = user_data[message.from_user.id]['address']

    # Send data to the API for registration
    payload = {
        "telegram_id": telegram_id,
        "phone_number": phone_number,
        "address": address
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_REGISTER, json=payload) as response:
            if response.status == 201:
                await message.answer("Ro'yxatdan muvaffaqiyatli o'tdingiz!")
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                promocode_button = types.KeyboardButton("Promokod yuborish")
                markup.add(promocode_button)
                await message.answer("Iltimos, kerakli tugmani tanlang.", reply_markup=markup)
            else:
                error_message = (await response.json()).get('error', 'Xato yuz berdi.')
                await message.answer(f"Xatolik: {error_message}")

    user_data.pop(message.from_user.id, None)


@dp.message_handler(lambda message: message.text == "Promokod yuborish")
async def promocode_start(message: types.Message):
    await message.answer("Promokodingizni kiriting.")


@dp.message_handler(lambda message: message.text.startswith("PROMO"))
async def check_promocode(message: types.Message):
    # Promokodni API ga yuborish
    telegram_id = str(message.from_user.id)
    promocode = message.text

    payload = {
        "telegram_id": telegram_id,
        "promo_code": promocode
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_PROMOCODE, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                await message.answer(f"Promokod muvaffaqiyatli qo'llandi:\nQo'shilgan ballar: {data.get('added_points', 0)}\nUmumiy ballar: {data.get('total_points', 0)}")
            else:
                error_message = (await response.json()).get('error', 'Xato yuz berdi.')
                await message.answer(f"Xatolik: {error_message}")


@dp.message_handler(lambda message: message.text == "Mahsulotlar")
async def show_products(message: types.Message):
    async def fetch_products():
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_PRODUCTS) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    products = await fetch_products()
    if products:
        markup = types.InlineKeyboardMarkup()
        for product in products:
            product_name = product['name']
            points = product['points']
            image_url = product['image_url']

            button = types.InlineKeyboardButton(
                text=f"{product_name} - {points} ball",
                callback_data=f"buy_{product['id']}"
            )
            markup.add(button)
            await bot.send_photo(message.chat.id, image_url, reply_markup=markup)

    else:
        await message.answer("Mahsulotlar mavjud emas.")


@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def buy_product(call: types.CallbackQuery):
    product_id = call.data.split('_')[1]
    telegram_id = str(call.from_user.id)

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL_BUY_PRODUCTS, json={"telegram_id": telegram_id, "product_id": product_id}) as response:
            if response.status == 200:
                data = await response.json()
                product_name = data.get('product', {}).get('name', 'Unknown product')
                remaining_points = data.get('remaining_points', 0)
                await call.message.answer(
                    f"Mahsulot muvaffaqiyatli xarid qilindi!\nMahsulot: {product_name}\nQolgan ballaringiz: {remaining_points}"
                )
            else:
                error_message = (await response.json()).get('error', 'Xato yuz berdi.')
                await call.message.answer(f"Xatolik: {error_message}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
