from django.contrib import admin
from .models import cat, product, sell, accounts
# Register your models here.
admin.site.register(cat)
admin.site.register(product)
admin.site.register(sell)
admin.site.register(accounts)
