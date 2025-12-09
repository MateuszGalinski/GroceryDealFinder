from django.contrib import admin
from .models import Product, Disscount, Glossary

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "price")
    search_fields = ("name",)


@admin.register(Disscount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "discounted_price", "old_price")
    search_fields = ("product__name",)


@admin.register(Glossary)
class GlossaryAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username",)
