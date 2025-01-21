from django.urls import path
from .views import *

urlpatterns = [
    path('code/', ValidatePromocodeView.as_view(), name='validate_promocode'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('buy_product/', BuyProductView.as_view(), name='buy_product'),
    path('phone/', CheckPhoneNumberAPIView.as_view(), name='check_phone'),
    path('feedback/', FeedBackAPIView.as_view(), name='user_feedback')
]


