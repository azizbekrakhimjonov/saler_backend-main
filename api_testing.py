import requests

# promocode api testing
# data = {
#     # 'code': 'STS0DB',
#     'code': 'U0ITTC',
#     'user': 'Tom Smith'
# }
# res = requests.post('http://127.0.0.1:8000/api/code/', data=data)
# print(res.text)

# feedback api testing
# data = {
#     'user': 'Tom Smith',
#     'message': 'I like it'
# }
# res = requests.post('https://3deb-84-54-83-43.ngrok-free.app/api/feedback/', json=data)
# # print(res.text)
# print(res.status_code)


# phone api testing
# data = {
#     'phone': '+998932608005',  # bazada mavjud bolgan raqam
#     # 'phone': '+998909001122',  # bazada mavjud bolmagan raqam
# }
# res = requests.post('http://127.0.0.1:8000/api/phone/', json=data)
# print(res.status_code)
# print(res.json().get('exists'))


# feedback api testing
# data = {
#     'user': 'Tom Smith',
#     'message': 'cool',
# }
# res = requests.post('http://127.0.0.1:8000/api/feedback/', json=data)
# print(res.status_code)


# register api testing
# url = 'http://127.0.0.1:8000/api/register/'

# data = {
#         "telegram_id": "12345676789",
#         "fullname": "Azizbek Raximjonov",
#         "phone_number": "+998901234567",
#         "address": "Toshkent, Yunusobod"
#     }
# response = requests.post(url, json=data)
# print("Status code:", response.status_code)
# print("Response data:", response.json())
