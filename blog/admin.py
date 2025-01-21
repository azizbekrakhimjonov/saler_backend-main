from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from .models import User, Product, Purchase, FeedBack, PhoneNumber, Promocode, Category


@receiver(post_save, sender=Category)
def update_promocode_points(sender, instance, **kwargs):
    Promocode.objects.filter(category=instance).update(point=instance.point)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'point')
    search_fields = ('name',)


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'category', 'point', 'used_by')
    search_fields = ('code', 'category__name', 'used_by')
    list_filter = ('category',)


@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'created_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'fullname', 'phone_number', 'points')

# @admin.register(Promocode)
# class PromocodeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'code', 'category', 'point', 'used_by')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'points')

admin.site.register(Purchase)