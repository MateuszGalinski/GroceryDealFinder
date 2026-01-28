from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiExample

from .serializers import (
    RegisterSerializer,
    GlossarySerializer,
    ProductSerializer,
    ShoppingListRequestSerializer,
    ShoppingPriceResponseSerializer,
    RegisterResponseSerializer,
    ErrorSerializer,
)
from .models import Product, Glossary

import re


class ShoppingPriceCalculator(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get_user_glossary(self, user) -> dict:
        """Get user's glossary translations or empty dict"""
        if not user.is_authenticated:
            return {}
        try:
            glossary = Glossary.objects.get(user=user)
            return glossary.translations or {}
        except Glossary.DoesNotExist:
            return {}

    def translate_item(self, item: str, glossary: dict):
        """Translate item using glossary, return original if not found"""
        return glossary.get(item, item)

    def parse_price(self, price_str):
        """Extract numeric price from string like '15.99 /szt.'"""
        if not price_str:
            return None
        try:
            match = re.search(r'[\d,\.]+', price_str)
            if match:
                return float(match.group().replace(',', '.'))
        except (ValueError, AttributeError):
            return None
        return None

    def get_product_price(self, product):
        """Get the effective price (discounted if available)"""
        if product.is_discounted and product.discounted_price:
            return self.parse_price(product.discounted_price)
        return self.parse_price(product.price)

    @extend_schema(
        summary="Calculate shopping prices across shops",
        description="Finds the cheapest shop that has all requested products. "
                    "Uses user's glossary for term translation if authenticated.",
        request=ShoppingListRequestSerializer,
        responses={
            200: ShoppingPriceResponseSerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                "Example shopping list",
                value={
                    "products": ['kiełbasa', 'jajka']
                },
                request_only=True,
            )
        ]

    )
    def post(self, request, format=None):
        serializer = ShoppingListRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request data'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list = serializer.validated_data['products']

        if not shopping_list:
            return Response(
                {'error': 'No products provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        glossary = self.get_user_glossary(request.user)
        all_shops = Product.objects.values_list('shop', flat=True).distinct()

        shop_results = {}

        for shop in all_shops:
            shop_products = []
            shop_complete = True

            for item in shopping_list:
                search_term = self.translate_item(item, glossary)

                matching = Product.objects.filter(
                    shop=shop,
                    name__icontains=search_term
                )

                if not matching.exists():
                    shop_complete = False
                    break

                cheapest = None
                cheapest_price = float('inf')

                for product in matching:
                    price = self.get_product_price(product)
                    if price and price < cheapest_price:
                        cheapest = product
                        cheapest_price = price

                if not cheapest:
                    shop_complete = False
                    break

                shop_products.append({
                    'original_term': item,
                    'searched_term': search_term,
                    'name': cheapest.name,
                    'price': cheapest_price,
                    'is_discounted': cheapest.is_discounted,
                    'url': cheapest.url,
                })

            if shop_complete and shop_products:
                total = round(sum(p['price'] for p in shop_products), 2)
                shop_results[shop] = {
                    'products': shop_products,
                    'total': total
                }

        cheapest = None
        if shop_results:
            cheapest_entry = min(shop_results.items(), key=lambda x: x[1]['total'])
            cheapest = {
                'shop': cheapest_entry[0],
                'total': cheapest_entry[1]['total'],
                'products': cheapest_entry[1]['products']
            }

        return Response({
            'shopping_list': shopping_list,
            'complete_shops': shop_results,
            'cheapest': cheapest,
            'shops_compared': len(shop_results)
        })


class ProductView(APIView):
    @extend_schema(
        summary="List all products",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class GlossaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user's glossary",
        responses={200: GlossarySerializer},
        
    )
    def get(self, request, format=None):
        try:
            glossary = Glossary.objects.get(user=request.user)
            serializer = GlossarySerializer(glossary)
            return Response(serializer.data)
        except Glossary.DoesNotExist:
            return Response(
                {'translations': {}},
                status=status.HTTP_200_OK
            )

    @extend_schema(
        summary="Update user's glossary",
        request=GlossarySerializer,
        responses={200: GlossarySerializer},
        examples=[
            OpenApiExample(
                "Example glossary",
                value={
                    "translations": {
                        "mleko": "mleko 2%",
                        "chleb": "chleb pszenny"
                    }
                },
                request_only=True,
            )
        ]
    )
    def put(self, request, format=None):
        try:
            glossary = Glossary.objects.get(user=request.user)
            serializer = GlossarySerializer(glossary, data=request.data, partial=True)
        except Glossary.DoesNotExist:
            serializer = GlossarySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: ErrorSerializer,
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful.",
                "tokens": get_token_for_user(user)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)