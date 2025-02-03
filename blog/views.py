from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
import json


def home_view(request):
    return render(request, 'index.html')


class UsePromocodeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("telegram_id")
        promo_code = request.data.get("promo_code")

        # Foydalanuvchini topish
        user = get_object_or_404(User, telegram_id=user_id)

        # Promokodni topish
        promocode = get_object_or_404(Promocode, code=promo_code)

        # Promokod ishlatilganligini tekshirish
        if promocode.used_by is not None:
            return Response(
                {
                    "success": False,
                    "message": f"Promo kod allaqachon ishlatilgan.\n"
                               f"Ishlatgan: {promocode.used_by.fullname}, {promocode.used_by.phone_number}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Promokodni ishlatish
        promocode.used_by = user
        promocode.save()

        # Foydalanuvchiga ball qo‘shish
        user.points += promocode.point
        user.save()

        return Response(
            {
                "success": True,
                "message": "Promo kod muvaffaqiyatli ishlatildi!",
                "data": {
                    "fullname": user.fullname,
                    "phone_number": user.phone_number,
                    "added_points": promocode.point,
                    "total_points": user.points,
                }
            },
            status=status.HTTP_200_OK
        )

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

class CheckTelegramIDView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        if not telegram_id:
            return Response({'error': 'telegram_id maydoni kiritilmagan.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_id=telegram_id)
            return Response({
                'exists': True,
                'is_registered': user.is_registered,
                'phone_number': user.phone_number,
                'points': user.points,
                'fullname': user.fullname,
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'exists': False}, status=status.HTTP_200_OK)

class CheckPromocodeAPIView(APIView):
    def post(self, request):
        promo_code = request.data.get("promo_code")
        promocode = Promocode.objects.filter(code=promo_code).first()

        if not promocode:
            return Response({"exists": False, "message": "Promokod topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"exists": True, "message": "Promokod mavjud."}, status=status.HTTP_200_OK)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                # Faqat telegram_id bo'yicha foydalanuvchini topish
                user = User.objects.get(telegram_id=data['telegram_id'])
                if user.is_registered:
                    return Response({'message': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan.'}, status=status.HTTP_200_OK)
                else:
                    # Agar foydalanuvchi ro'yxatdan o'tmagan bo'lsa, uni yangilash
                    user.fullname = data.get('fullname', user.fullname)  # Agar maydon yuborilmasa, eski qiymat saqlanadi
                    user.phone_number = data.get('phone_number', user.phone_number)
                    user.address = data.get('address', user.address)
                    user.is_registered = True
                    user.points = 5
                    user.save()
                    return Response({'message': 'Foydalanuvchi muvaffaqiyatli ro‘yxatdan o‘tdi.'}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                # Agar foydalanuvchi topilmasa, yangi foydalanuvchi yaratish
                User.objects.create(
                    telegram_id=data['telegram_id'],
                    fullname=data.get('fullname', ''),  # Agar maydon yuborilmasa, bo'sh qator saqlanadi
                    phone_number=data.get('phone_number', ''),
                    address=data.get('address', ''),
                    is_registered=True,
                    points=5
                )
                return Response({'message': 'Foydalanuvchi muvaffaqiyatli ro‘yxatdan o‘tdi.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListView(APIView):
    def get(self, request):
        product_name = request.GET.get('name')  # URL parametrlardan 'name' ni olish (ixtiyoriy)
        try:
            if product_name:
                # Agar mahsulot nomi berilgan bo‘lsa, shu nom bo‘yicha qidirish
                products = Product.objects.filter(name__iexact=product_name)  # nomni aniqlik bilan qidirish
                if not products.exists():
                    return Response({'error': 'Bunday mahsulot topilmadi'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Aks holda barcha mahsulotlarni olish
                products = Product.objects.all()

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

class FeedBackAPIView(APIView):
    def post(self, request):
        serializer = FeedBackSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

