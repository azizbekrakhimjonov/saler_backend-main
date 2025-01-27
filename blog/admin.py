from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.contrib import admin
from .models import User, Product, Purchase, FeedBack, PhoneNumber, Promocode, Category
import openpyxl
from django.utils.html import format_html

@receiver(post_save, sender=Category)
def update_promocode_points(sender, instance, **kwargs):
    Promocode.objects.filter(category=instance).update(point=instance.point)

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'category', 'point', 'used_by')
    actions = ['export_to_excel']

    def export_to_excel(self, request, queryset):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Promocodes"

        # Sarlavhalarni qo'shish
        sheet.append(['Promocode', 'Category', 'Points', 'Used By'])

        # Ma'lumotlarni qo'shish
        for promocode in queryset:
            sheet.append([
                promocode.code,
                promocode.category.name,
                promocode.point,
                promocode.used_by.fullname if promocode.used_by else 'Not Used'
            ])

        # Excel faylni HTTP javob orqali qaytarish
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=promocodes.xlsx'
        workbook.save(response)
        return response

    export_to_excel.short_description = "Export selected Promocodes to Excel"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'point', 'excel_file_link')  # Excel fayl uchun havola chiqariladi
    readonly_fields = ('excel_file',)  # Excel fayl faqat o'qish rejimida bo'ladi

    def excel_file_link(self, obj):
        if obj.excel_file:
            # Fayl uchun havola yaratiladi
            return format_html('<a href="{}" download>{}</a>', obj.excel_file.url, obj.excel_file.name)
        return "No file available"

    excel_file_link.short_description = "Excel File"

@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'created_at')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'fullname', 'phone_number', 'points')

admin.site.register(Purchase)