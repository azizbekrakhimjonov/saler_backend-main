from aiogram import Bot, Dispatcher, executor, types
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests

url = ''
# url = 'https://9640-188-113-231-246.ngrok-free.app'
API_URL_CHECK_ID =  f"{url}/api/check_id/"
API_URL_CHECK_PHONE =  f"{url}/api/phone/"
API_URL_CHECK_CODE =  f"{url}/api/check_code/"
API_URL_FEEDBACK =  f"{url}/api/feedback/"
API_URL_REGISTER =  f"{url}/api/register/"
API_URL_PROMOCODE = f"{url}/api/code/"
API_URL_PRODUCTS =  f"{url}/api/products/"
API_URL_BUY_PRODUCTS = f"{url}/api/buy_product/"

# TOKEN = "7832802417:AAHd6atjmzCKdx4IgnOJLB7EIsvUrP9Mu7U"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class RegistrationStates(StatesGroup):
    fullname = State()
    phone_number = State()
    address = State()

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
                res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
                if res.status_code == 200:
                    markup.add(promocode_button, products_button, feedback_button)
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
    await message.answer("Manzilingizni kiriting.")
    await RegistrationStates.address.set()  # Keyingi holatga o'tish

@dp.message_handler(state=RegistrationStates.address)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)  # Manzilni saqlash

    # Ma'lumotlarni olish
    user_data = await state.get_data()
    telegram_id = str(message.from_user.id)
    fullname = user_data['fullname']
    phone_number = user_data['phone_number']
    address = user_data['address']

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


@dp.message_handler(lambda message: message.text == "Promokod yuborish")
async def promocode_start(message: types.Message):
    await message.answer("Promokodni kiriting.")
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

@dp.message_handler(lambda message: message.text == "Izoh")
async def feedback(message: types.Message):
    await message.answer("Izoh yozish uchun matn yuboring:")
    await FeedbackStates.feedback.set()

@dp.message_handler(state=FeedbackStates.feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    telegram_id = str(message.from_user.id)
    print(feedback_text)
    check_response = requests.post(API_URL_CHECK_ID, json={"telegram_id": telegram_id})
    if check_response.status_code == 200:
        data = check_response.json()
        payload = {
            "user": data.get("fullname"),
            "message": feedback_text
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
            if response.status_code==200:
                products = response.json()
                if products:
                    for product in products:
                        markup = types.InlineKeyboardMarkup()
                        print(product)
                        product_name = product['name']
                        points = product['points']
                        image_url = url+product['image']
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
        product_name = data.get('product', {}).get('name', 'Unknown product')
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
      # await message.answer("Kerakli buyruqni tanlang!")
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
                  res = requests.post(API_URL_CHECK_PHONE, json={'phone': data['phone_number']})
                  if res.status_code == 200:
                      markup.add(promocode_button, products_button, feedback_button)
                      await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)
                  else:
                      markup.add(promocode_button)
                      await message.answer("Iltimos, kerakli tugmani tanlang:", reply_markup=markup)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
