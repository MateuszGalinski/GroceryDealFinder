from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Glossary

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class GlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = ['translations']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )

# --- Request/Response serializers ---

class ShoppingListRequestSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of product names to search for"
    )


class MatchedProductSerializer(serializers.Serializer):
    original_term = serializers.CharField()
    searched_term = serializers.CharField()
    name = serializers.CharField()
    price = serializers.FloatField()
    is_discounted = serializers.BooleanField()
    url = serializers.URLField(allow_null=True)


class ShopResultSerializer(serializers.Serializer):
    products = MatchedProductSerializer(many=True)
    total = serializers.FloatField()


class CheapestShopSerializer(serializers.Serializer):
    shop = serializers.CharField()
    total = serializers.FloatField()
    products = MatchedProductSerializer(many=True)


class ShoppingPriceResponseSerializer(serializers.Serializer):
    shopping_list = serializers.ListField(child=serializers.CharField())
    complete_shops = serializers.DictField(child=ShopResultSerializer())
    cheapest = CheapestShopSerializer(allow_null=True)
    shops_compared = serializers.IntegerField()


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    tokens = TokenSerializer()


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()