# from django.core.management.base import BaseCommand
# from random import choices
# from string import ascii_uppercase, digits
# from blog.models import Promocode
#
# class Command(BaseCommand):
#     help = "Generate and populate promocodes"
#
#     def handle(self, *args, **kwargs):
#         categories = {
#             'category1': 5,
#             'category2': 10,
#             'category3': 15,
#             'category4': 20,
#             'category5': 25,
#             'category6': 30,
#             'category7': 35,
#             'category8': 40,
#             'category9': 45,
#             'category10': 50
#         }
#
#         for category, point in categories.items():
#             for _ in range(100):  # Generate 100 promocodes per category
#                 code = ''.join(choices(ascii_uppercase + digits, k=6))
#                 Promocode.objects.get_or_create(
#                     code=code,
#                     defaults={'category': category, 'point': point}
#                 )
#
#         self.stdout.write(self.style.SUCCESS("Promocodes generated successfully!"))


from django.core.management.base import BaseCommand
from random import choices
from string import ascii_uppercase, digits
from blog.models import Promocode, Category

class Command(BaseCommand):
    help = "Generate and populate promocodes"

    def handle(self, *args, **kwargs):
        categories = {
            'category1': 5,
            'category2': 10,
            'category3': 15,
            'category4': 20,
            'category5': 25,
            'category6': 30,
            'category7': 35,
            'category8': 40,
            'category9': 45,
            'category10': 50
        }

        for name, point in categories.items():
            category, created = Category.objects.get_or_create(name=name, defaults={'point': point})
            for _ in range(100):  # Generate 100 promocodes per category
                code = ''.join(choices(ascii_uppercase + digits, k=6))
                Promocode.objects.get_or_create(
                    code=code,
                    defaults={'category': category}
                )

        self.stdout.write(self.style.SUCCESS("Promocodes generated successfully!"))
