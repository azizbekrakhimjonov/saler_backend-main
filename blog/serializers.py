from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['telegram_id', 'fullname', 'phone_number', 'address']
        extra_kwargs = {
            'fullname': {'required': False},
            'phone_number': {'required': False},
            'address': {'required': False},
            'telegram_id': {'validators': []},  # Unique tekshiruvini o'chirish
        }
    def validate_phone_number(self, value):
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Telefon raqam xalqaro formatda bo'lishi kerak. Masalan, +998901234567.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Telefon raqam uzunligi 10 dan 15 gacha bo'lishi kerak.")
        return value

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'points']

class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    def validate_phone(self, value):
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Telefon raqam noto'g'ri formatda.")
        return value

class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = ['user', 'message']

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")  # Vaqt formatlash

    class Meta:
        model = Purchase
        fields = ['user', 'product', 'purchase_date', 'status']
