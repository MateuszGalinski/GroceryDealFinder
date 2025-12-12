from django.contrib import admin
from .models import Product, Glossary

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "price", "shop")
    search_fields = ("name","shop",)


@admin.register(Glossary)
class GlossaryAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username",)
