import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import logging
import requests

import os
import pandas as pd


url = 'https://hipad.uz'
# url = 'https://30ab-84-54-83-43.ngrok-free.app'
API_URL_CHECK_ID = f"{url}/api/check_id/"
API_URL_CHECK_PHONE = f"{url}/api/phone/"
API_URL_CHECK_CODE = f"{url}/api/check_code/"
API_URL_FEEDBACK = f"{url}/api/feedback/"
API_URL_REGISTER = f"{url}/api/register/"
API_URL_PROMOCODE = f"{url}/api/code/"
API_URL_PRODUCTS = f"{url}/api/products/"
API_URL_BUY_PRODUCTS = f"{url}/api/buy_product/"
API_URL_PURCHASE = f"{url}/api/purchase/"
API_URL_PURCHASE_UPDATE = f"{url}/api/purchase_update/"
API_URL_STATUS = f"{url}/api/status/"


TOKEN = "7451986125:AAEykGVq6ZNjnUaUZLc8TTof-TN8P8y77K4"
# TOKEN = "7832802417:AAHd6atjmzCKdx4IgnOJLB7EIsvUrP9Mu7U"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class RegistrationStates(StatesGroup):
    fullname = State()
    phone_number = State()
    region = State()
    district = State()
    street = State()


class FeedbackStates(StatesGroup):
    feedback = State()

class PromocodeStates(StatesGroup):
    waiting_for_promocode = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    telegram_id = str(message.from_user.id)
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        if data['exists']:
            if data['is_registered']:
                await message.answer(
                    f"Assalomu alaykum! Siz avval ro'yxatdan o'tgansiz ✅\n📊Umumiy bonus ballar: {data['points']}"
                )
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                promocode_button = types.KeyboardButton("Promokod yuborish")
                products_button = types.KeyboardButton("Mahsulotlar")
                feedback_button = types.KeyboardButton("Izoh")
                order_button = types.KeyboardButton("Buyurtmalar Tarixi")
                status_button = types.KeyboardButton("Ballar")
                res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
                if res.status_code == 200:
                    markup.add(promocode_button, products_button, feedback_button, order_button, status_button)
                    await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)
                else:
                    markup.add(promocode_button)
                    await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)

            else:
                await message.answer("Siz ro'yxatdan o'tmagansiz. Iltimos, to'liq ismingizni kiriting:")
                await RegistrationStates.fullname.set()
        else:
            await message.answer("Assalomu alaykum! To'liq ismingizni kiriting:")
            await RegistrationStates.fullname.set()
    else:
        await message.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring. \n\t\t/start")


@dp.message_handler(state=RegistrationStates.fullname)
async def get_fullname(message: types.Message, state: FSMContext):
    await state.update_data(fullname=message.text)  # Ismni saqlash
    await message.answer("Telefon raqamingizni kiriting (misol: +998932608005).")
    await RegistrationStates.phone_number.set()  # Keyingi holatga o'tish


@dp.message_handler(state=RegistrationStates.phone_number)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)  # Telefon raqamini saqlash
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    regions = os.listdir("address_data")
    for region in regions:
        keyboard.add(KeyboardButton(region))
    await message.answer("Viloyatingizni tanlang:", reply_markup=keyboard)
    await RegistrationStates.region.set()


@dp.message_handler(state=RegistrationStates.region)
async def select_district(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    district_path = f"address_data/{region}/districts.csv"

    if os.path.exists(district_path):
        df = pd.read_csv(district_path)
        for district in df["name"]:
            keyboard.add(KeyboardButton(district))

    await message.answer("Tumanni tanlang:", reply_markup=keyboard)
    await RegistrationStates.district.set()


@dp.message_handler(state=RegistrationStates.district)
async def select_street(message: types.Message, state: FSMContext):
    data = await state.get_data()
    region = data["region"]
    district = message.text
    await state.update_data(district=district)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    street_path = f"address_data/{region}/{district}.csv"

    if os.path.exists(street_path):
        df = pd.read_csv(street_path)
        for street in df["name"]:
            keyboard.add(KeyboardButton(street))

    await message.answer("Ko‘chani tanlang:", reply_markup=keyboard)
    await RegistrationStates.street.set()


@dp.message_handler(state=RegistrationStates.street)
async def confirm_address(message: types.Message, state: FSMContext):
    # Ma'lumotlarni olish
    user_data = await state.get_data()
    telegram_id = str(message.from_user.id)
    fullname = user_data['fullname']
    phone_number = user_data['phone_number']
    region = user_data["region"]
    district = user_data["district"]
    street = message.text
    address = f"{region}, {district}, {street}"
    await state.update_data(street=street)

    # API ga so'rov yuborish
    payload = {
        "telegram_id": telegram_id,
        "fullname": fullname,
        "phone_number": phone_number,
        "address": address
    }

    response = requests.post(API_URL_REGISTER, json=payload)
    if response.status_code == 201:
        await message.answer("Ro'yxatdan muvaffaqiyatli o'tdingiz ✅\nBotni qayta  ishga tushuring: 🟢/start")
    else:
        error_message = response.json().get('error', 'Xato yuz berdi.')
        await message.answer(f"Xatolik: {error_message}")

    await state.finish()

@dp.message_handler(lambda message: message.text == "Ballar")
async def show_points(message: types.Message):
    response = requests.get(API_URL_STATUS)
    if response.status_code == 200 and len(response.json()) != 0:
        await message.answer(f"{response.json()[0]['message']}")
    else:
        await message.answer("Malumot topilmadi.")


@dp.message_handler(lambda message: message.text == "Promokod yuborish")
async def promocode_start(message: types.Message):
    await message.answer("Promokodni kiriting:")
    await PromocodeStates.waiting_for_promocode.set()


@dp.message_handler(state=PromocodeStates.waiting_for_promocode)
async def check_promocode(message: types.Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    promocode = message.text
    payload = {
        "telegram_id": telegram_id,
        "promo_code": promocode
    }
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        if data['exists']:
            res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
            if res.status_code == 200:
                response = requests.post(API_URL_PROMOCODE, json=payload)
                if response.status_code == 200:
                    data = response.json()['data']
                    await message.answer(
                        f"✅Promokod muvaffaqiyatli qo'llanildi:\nBonus ball: {data.get('added_points')}\nUmumiy bonus ballar: {data.get('total_points')}")
                elif response.status_code == 400:
                    await message.answer(f"{response.json()['message']}")
                else:
                    await message.answer(f"Siz noto`gri promokod kiritingiz")
            elif requests.post(API_URL_CHECK_CODE, json={'promo_code': promocode}).status_code == 404:
                await message.answer("Siz noto`gri promokod kiritingiz")
            else:
                await message.answer("✅Siz siftali maxsulot xarid qildingiz")
    await state.finish()


@dp.message_handler(lambda message: message.text == "Buyurtmalar Tarixi")
async def orders(message: types.Message):
    telegram_id = message.from_user.id
    response = requests.get(API_URL_PURCHASE, params={"telegram_id": telegram_id})

    if response.status_code == 200:
        data = response.json()
        print(data)
        if isinstance(data, dict) and "message" in data:
            await message.answer("📦 Buyurtmalar topilmadi!")
        else:
            for item in data:
                product_name = item.get("product_name", "Noma'lum mahsulot")
                product_image = item.get("product_image", None)
                purchase_date = item.get("purchase_date", "Sana mavjud emas")
                status = item.get("status", "pending")  # Buyurtma holati

                # Buyurtma avval tasdiqlangan yoki rad etilgan bo‘lsa, button qo‘shilmaydi
                if status in ["accepted", "rejected"]:
                    status_text = "✅ Qabul qilingan" if status == "accepted" else "❌ Rad etilgan"
                    text = f"🛒 *Mahsulot*: {product_name}\n📅 *Sana*: {purchase_date}\n📌 *Holat*: {status_text}"
                    keyboard = None
                else:
                    text = f"🛒 *Mahsulot*: {product_name}\n📅 *Sana*: {purchase_date}\n📌 *Holat*: ⏳ Kutish holatida"
                    buttons = [
                        InlineKeyboardButton(text="✅ Qabul qildim", callback_data=f"accept_{product_name}"),
                        InlineKeyboardButton(text="❌ Rad etdim", callback_data=f"reject_{product_name}")
                    ]
                    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)

                if product_image:
                    await bot.send_photo(message.chat.id, photo=product_image, caption=text,
                                         reply_markup=keyboard, parse_mode="Markdown")
                else:
                    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer("❌ Ma'lumotlarni olishda xatolik yuz berdi. Keyinroq urinib ko'ring!")


@dp.callback_query_handler(lambda call: call.data.startswith("accept_") or call.data.startswith("reject_"))
async def update_purchase_status(call: types.CallbackQuery):
    telegram_id = call.from_user.id
    action, product_name = call.data.split("_", 1)
    status = "accepted" if action == "accept" else "rejected"

    response = requests.post(API_URL_PURCHASE_UPDATE, json={
        "telegram_id": telegram_id,
        "product_name": product_name,
        "status": status
    })

    if response.status_code == 200:
        new_status_text = f"\n📌 *Holat*: {'✅ Qabul qilingan' if status == 'accepted' else '❌ Rad etilgan'}"

        if call.message.photo:
            new_caption = (call.message.caption or "") + new_status_text
            await call.message.edit_caption(new_caption, parse_mode="Markdown", reply_markup=None)  # Tugmalarni olib tashlaymiz
        else:
            new_text = (call.message.text or "") + new_status_text
            await call.message.edit_text(new_text, parse_mode="Markdown", reply_markup=None)  # Tugmalarni olib tashlaymiz

        await call.answer(f"Buyurtma {status} statusiga o‘zgartirildi ✅")
    else:
        await call.answer("❌ Xatolik yuz berdi, keyinroq urinib ko‘ring.")


@dp.message_handler(lambda message: message.text == "Izoh")
async def feedback(message: types.Message):
    await message.answer("Izoh yozish uchun matn yuboring:")
    await FeedbackStates.feedback.set()

@dp.message_handler(state=FeedbackStates.feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    telegram_id = str(message.from_user.id)
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        payload = {
            "user": data.get("fullname"),
            "message": feedback_text,
            "phone": data.get("phone_number")
        }
        response = requests.post(API_URL_FEEDBACK, json=payload)
        # await message.answer(f'{check_response.status_code}')
        if response.status_code == 201:
            await message.answer("Izohingiz uchun rahmat!")
        else:
            await message.answer("Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.\n\t\t/start")

        await state.finish()


@dp.message_handler(lambda message: message.text == "Mahsulotlar")
async def show_products(message: types.Message):
    telegram_id = str(message.from_user.id)
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
        if res.status_code == 200:
            response = requests.get(API_URL_PRODUCTS)
            if response.status_code == 200:
                products = response.json()
                if products:
                    for product in products:
                        markup = types.InlineKeyboardMarkup()
                        print(product)
                        product_name = product['name']
                        points = product['points']
                        image_url = url + product['image']
                        button = types.InlineKeyboardButton(
                            text=f"{product_name} - {points} ball",
                            callback_data=f"buy_{product['id']}")
                        markup.add(button)
                        await bot.send_photo(message.chat.id, image_url, reply_markup=markup)
                else:
                    await message.answer("Mahsulotlar mavjud emas.")

@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def buy_product(call: types.CallbackQuery):
    product_id = call.data.split('_')[1]
    telegram_id = str(call.from_user.id)
    response = requests.post(API_URL_BUY_PRODUCTS, json={"telegram_id": telegram_id, "product_id": product_id})
    if response.status_code == 200:
        data = response.json()
        product_name = data.get('purchase', {}).get('product_name', 'Unknown product')
        remaining_points = data.get('remaining_points', 0)
        await call.message.answer(
            f"Mahsulot muvaffaqiyatli xarid qilindi!\nMahsulot: {product_name}\nQolgan ballaringiz: {remaining_points}"
        )
    else:
        if response.status_code == 400:
            await call.message.answer("Ball yetarli emas!")
        else:
            await call.message.answer(f"Xatolik...\nIltimos botga qatadan /start buyruguni bosing!")


@dp.message_handler(lambda message: message.text is not None)
async def echo(message: types.Message):
    telegram_id = str(message.from_user.id)
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        if data['exists']:
            if data['is_registered']:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                promocode_button = types.KeyboardButton("Promokod yuborish")
                products_button = types.KeyboardButton("Mahsulotlar")
                feedback_button = types.KeyboardButton("Izoh")
                order_button = types.KeyboardButton("Buyurtmalar Tarixi")
                status_button = types.KeyboardButton("Ballar")
                res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
                if res.status_code == 200:
                    markup.add(promocode_button, products_button, feedback_button, order_button, status_button)
                    await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)
                else:
                    markup.add(promocode_button)
                    await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
