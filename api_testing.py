import requests

# promocode api testing
# data = {
#     'telegram_id': '112233',
#     'promo_code': 'LSJZ0W',
# }
# #
# res = requests.post('http://127.0.0.1:8000/api/code/', json=data)
# print(res.status_code)
# print(res.text)

# feedback api testing
# data = {
#     'user': 'Nora Tomson',
#     'message': 'I like it'
# }
# res = requests.post('http://127.0.0.1:8000/api/feedback/', json=data)
# # print(res.text)
# print(res.status_code)


# phone api testing
# data = {
#     # 'phone': '+998932608005',  # bazada mavjud bolgan raqam
#     'phone': '+998909001122',  # bazada mavjud bolmagan raqam
# }
# res = requests.post('http://127.0.0.1:8000/api/phone/', json=data)
# print(res.status_code)
# print(res.json().get('exists'))


# register api testing
url = 'http://127.0.0.1:8000/api/register/'

data = {
        "telegram_id": "112233",
        "fullname": "Nora",
        "phone_number": "+998909001122",
        "address": "Toshkent, Yunusobod"
    }
response = requests.post(url, json=data)
print("Status code:", response.status_code)
print("Response data:", response.json())


# product api testing
# url = "http://127.0.0.1:8000/api/products/"
# params = {'name': 'Soat'}
#
# try:
#     response = requests.get(url, params=params)
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


