import requests

# promocode api testing
# data = {
#     'telegram_id': '1486580350',
#     'promo_code': '6t7g7',
# }
# #
# res = requests.post('https://hipad.uz/api/code/', json=data)
# print(res.status_code)
# print(res.text)

# check promocode
# res = requests.post('https://hipad.uz/api/check_code/', json={'promo_code': 'LRWMOP'})
# print(res.status_code)
# print(res.text)

# feedback api testing
# data = {
#     'user': 'Nora Tomson',
#     'message': 'I like it'
# }
# res = requests.post('https://softools.uz/api/feedback/', json=data)
# # print(res.text)
# print(res.status_code)


# phone api testing
# data = {
#     'phone': '+998932608005',  # bazada mavjud bolgan raqam
#     # 'phone': '+998909001122',  # bazada mavjud bolmagan raqam
# }
# res = requests.post('https://hipad.uz/api/phone/', json=data)
# print(res.status_code)
# print(res.json().get('exists'))
#

# register api testing
# url = 'https://hipad.uz/api/register/'
# url = 'http://127.0.0.1:8000/api/register/'
#
# data = {
#         "telegram_id": "1486580350",
#         "fullname": "Azizbek Rahimjonov",
#         "phone_number": "+998932608005",
#         "address": "Toshkent, Yunusobod"
#
#     }
# response = requests.post(url, json=data)
# print("Status code:", response.status_code)
# print("Response data:", response.json())

# check_id api

# url = 'http://127.0.0.1:8000/api/check_id/'
# # url = 'http://hipad.uz/api/check_id/'
# data = {
#     "telegram_id": "1486580350"
# }
#
# response = requests.post(url, json=data)
# print("Status code:", response.status_code)
# print("Response data:", response.json())

# product api testing
# url = " https://021c-84-54-83-43.ngrok-free.app/api/products/"
# params = {'name': 'Soat'}
#
# try:
#     response = requests.get(url)
#     response_data = response.json()
#
#     if response.status_code == 200:
#         print("Mahsulot topildi:")
#         print(response_data)
#     elif response.status_code == 400:
#         print("Xatolik:", response_data.get('error', 'Noma’lum xatolik'))
#     elif response.status_code == 404:
#         print("Xatolik:", response_data.get('error', 'Mahsulot topilmadi'))
#     else:
#         print(f"Xatolik: {response.status_code} - {response_data}")
# except requests.exceptions.RequestException as e:
#     print(f"So'rov xatoligi yuz berdi: {e}")


