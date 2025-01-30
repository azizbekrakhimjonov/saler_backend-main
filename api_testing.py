import requests

# promocode api testing
# data = {
#     'telegram_id': '1486580350',
#     'promo_code': 'DSV5Q7',
# }
# #
# res = requests.post('https://softools.uz/api/code/', json=data)
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
# res = requests.post('https://softools.uz/api/phone/', json=data)
# print(res.status_code)
# print(res.json().get('exists'))


# register api testing
# url = 'https://softools.uz/api/register/'
#
# data = {
#         "telegram_id": "1486580350",
#         "fullname": "Azizbek Rahimjonov",
#         "phone_number": "+998932608005",
#         "address": "Toshkent, Yunusobod"
#     }
# response = requests.post(url, json=data)
# print("Status code:", response.status_code)
# print("Response data:", response.json())


# product api testing
# url = "http://softools.uz/api/products/"
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


