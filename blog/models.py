import openpyxl
import csv
from random import choices
import os
from string import ascii_uppercase, digits
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class User(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True, verbose_name=_("Telegram ID"))
    fullname = models.CharField(max_length=255, verbose_name=_("Full Name"))
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"))
    address = models.TextField(verbose_name=_("Address"))
    is_registered = models.BooleanField(default=False, verbose_name=_("Is Registered"))
    points = models.IntegerField(default=5, verbose_name=_("Points"))

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['fullname']

class PhoneNumber(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category"))
    point = models.IntegerField(verbose_name=_("Points"))
    count = models.IntegerField(default=1000, verbose_name=_("Promo Code Count"))
    excel_file = models.FileField(upload_to='promocodes/', null=True, blank=True, verbose_name=_("Excel File"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Promocode(models.Model):
    code = models.CharField(max_length=6, unique=True, verbose_name=_("Promo Code"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Category"))
    point = models.IntegerField(verbose_name=_("Points"))
    used_by = models.ForeignKey(User, null=True, blank=True,  on_delete=models.SET_NULL, verbose_name=_("Used By"))

    def save(self, *args, **kwargs):
        if not self.pk:  # Agar yangi yaratilayotgan bo‘lsa
            self.point = self.category.point  # Ballarni kategoriyadan olamiz
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Promocode")
        verbose_name_plural = _("Promocodes")


@receiver(post_save, sender=Category)
def create_promocodes(sender, instance, created, **kwargs):
    if created:
        promocodes = []
        file_name = f"{instance.name}_promocodes.xlsx"
        file_path = os.path.join("/var/www/hipad.uz/media", "promocodes", file_name)
        # file_path = os.path.join(settings.MEDIA_ROOT, "promocodes", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Promocodes"

        sheet.append(["Promocode", "Category Name", "Points"])

        for _ in range(instance.count):  # `count` maydonidan foydalanamiz
            code = ''.join(choices(ascii_uppercase + digits, k=6))
            promocodes.append(
                Promocode(code=code, category=instance, point=instance.point)
            )
            sheet.append([code, instance.name, instance.point])

        Promocode.objects.bulk_create(promocodes)
        workbook.save(file_path)

        instance.excel_file = f'promocodes/{file_name}'
        instance.save()


class FeedBack(models.Model):
    user = models.CharField(max_length=100)
    message = models.TextField(default=None)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.created_at}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')  # Images will be uploaded to 'media/products/'
    points = models.IntegerField()  # Points required to purchase the product

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Purchase by {self.user.fullname} - {self.product.name} at {self.purchase_date} - {self.status}"

class Comment(models.Model):
    message = models.TextField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at}"