from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('code/', UsePromocodeAPIView.as_view(), name='use_promocode'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('buy_product/', BuyProductView.as_view(), name='buy_product'),
    path('phone/', CheckPhoneNumberAPIView.as_view(), name='check_phone'),
    path('feedback/', FeedBackAPIView.as_view(), name='user_feedback'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('check_id/', CheckTelegramIDView.as_view(), name='check_telegram_id'),
    path('check_code/', CheckPromocodeAPIView.as_view(), name='check_code'),
    path('purchase/', PurchaseAPIView.as_view(), name='purchase_id'),
    path('purchase_update/', UpdatePurchaseStatusAPIView.as_view(), name='purchase_update'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




