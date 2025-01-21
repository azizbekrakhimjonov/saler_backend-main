from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Category")
    point = models.IntegerField(verbose_name="Points")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Promocode(models.Model):
    code = models.CharField(max_length=6, unique=True, verbose_name="Promo Code")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Category")
    point = models.IntegerField(verbose_name="Points")
    used_by = models.CharField(max_length=255, null=True, blank=True, verbose_name="Used By")

    def save(self, *args, **kwargs):
        if not self.pk:  # Agar yangi yaratilayotgan bo‘lsa
            self.point = self.category.point  # Ballarni kategoriyadan olamiz
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Promocode"
        verbose_name_plural = "Promocodes"


class PhoneNumber(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone

class FeedBack(models.Model):
    user = models.CharField(max_length=100)
    message = models.TextField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.created_at}"

class User(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True)
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    is_registered = models.BooleanField(default=False)
    points = models.IntegerField(default=5)  # Ro'yxatdan o'tganida 5 ball beriladi

    def __str__(self):
        return self.fullname

class Product(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField(max_length=200)  # URL for the product image
    points = models.IntegerField()  # Points required to purchase the product

    def __str__(self):
        return self.name

class Purchase(models.Model):
    def __str__(self):
        return "Purchase Model"
