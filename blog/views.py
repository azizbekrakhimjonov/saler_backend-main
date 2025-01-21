from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
import json


class FeedBackAPIView(APIView):
    def post(self, request):
        serializer = FeedBackSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPhoneNumberAPIView(APIView):
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            exists = PhoneNumber.objects.filter(phone=phone).exists()
            if exists:
                return Response({"exists": True, "message": "Telefon raqami bazada topildi."}, status=status.HTTP_200_OK)
            else:
                return Response({"exists": False, "message": "Telefon raqami bazada mavjud emas."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user, created = User.objects.get_or_create(
                telegram_id=data['telegram_id'],
                defaults={
                    'fullname': data['fullname'],
                    'phone_number': data['phone_number'],
                    'address': data['address'],
                    'is_registered': True,
                    'points': 5
                }
            )
            if not created and user.is_registered:
                return Response({'message': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan.'}, status=status.HTTP_200_OK)
            return Response({'message': 'Foydalanuvchi muvaffaqiyatli ro‘yxatdan o‘tdi.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidatePromocodeView(View):
    def post(self, request):
        try:
            # Read JSON data
            data = json.loads(request.body)
            code = data.get('code')
            telegram_id = data.get('telegram_id')

            if not code or not telegram_id:
                return JsonResponse({'error': 'Code and Telegram ID are required.'}, status=400)

            user = User.objects.filter(telegram_id=telegram_id).first()
            if not user:
                return JsonResponse({'error': 'User not found.'}, status=404)

            promocode = Promocode.objects.filter(code=code).first()
            if not promocode:
                return JsonResponse({'error': 'Invalid promocode.'}, status=404)

            if promocode.used_by:
                return JsonResponse({'error': f'{promocode.used_by}'}, status=203)

            promocode.used_by = user.fullname  # Full name of the user
            user.points += promocode.point
            promocode.save()
            user.save()

            return JsonResponse({
                'message': 'Promocode applied successfully.',
                'category': promocode.category,
                'added_points': promocode.point,
                'total_points': user.points
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)


class ProductListView(APIView):
    def get(self, request):
        product_name = request.GET.get('name')  # URL parametrlardan 'name' ni olish
        if not product_name:
            return Response({'error': 'Mahsulot nomini ko‘rsating'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Mahsulotni nomi bilan qidirish
            products = Product.objects.filter(name__iexact=product_name)  # nomni aniqlik bilan qidirish
            if not products.exists():
                return Response({'error': 'Bunday mahsulot topilmadi'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ProductSerializer(products, many=True)  # Serializatsiya qilish
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # Xatolikni qaytarish


class BuyProductView(View):
    def post(self, request):
        try:
            # JSON ma'lumotlarni pars qilish
            data = json.loads(request.body)
            product_id = data.get('product_id')
            telegram_id = data.get('telegram_id')

            # Kiritilgan ma'lumotlarni tekshirish
            if not product_id or not telegram_id:
                return JsonResponse({"error": "Product ID and Telegram ID are required."}, status=400)

            # Mahsulotni olish
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({"error": "Product not found."}, status=404)

            # Foydalanuvchini olish
            user = User.objects.filter(telegram_id=telegram_id).first()
            if not user:
                return JsonResponse({"error": "User not found."}, status=404)

            # Ballarni tekshirish
            if user.points < product.points:
                return JsonResponse({"error": "Not enough points."}, status=400)

            # Ballarni kamaytirish va saqlash
            user.points -= product.points
            user.save()

            # Javob qaytarish
            return JsonResponse({
                "message": "Product purchased successfully.",
                "remaining_points": user.points,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "points": product.points,
                },
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
