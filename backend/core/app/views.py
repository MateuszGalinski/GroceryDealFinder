from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    RegisterSerializer,
    GlossarySerializer,
    ProductSerializer
)

from .models import (
    Product,
    Glossary
)

import re
from collections import defaultdict

def parse_price(price_str):
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

def get_product_price(product):
    """Get the effective price (discounted if available)"""
    if product.is_discounted and product.discounted_price:
        return parse_price(product.discounted_price)
    return parse_price(product.price)

# CORE LOGIC ENDPOINTS
class ShoppingPriceCalculator(APIView):
    def post(self, request, format=None):
        '''
        Docstring for post
        
        :param self: Description
        :param request: request in form
            {
                "products": ["item_name1", "item_name2", ...]
            }
            where item_name is string
        :param format: Description
        '''
        shopping_list = request.data.get('products', [])
        
        if not shopping_list:
            return Response(
                {'error': 'No products provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all unique shops
        all_shops = Product.objects.values_list('shop', flat=True).distinct()
        
        shop_results = {}
        
        for shop in all_shops:
            shop_products = []
            shop_complete = True
            
            for item in shopping_list:
                # Find cheapest matching product in this shop
                matching = Product.objects.filter(
                    shop=shop,
                    name__icontains=item
                )
                
                if not matching.exists():
                    shop_complete = False
                    break
                
                # Get the cheapest option for this item
                cheapest = None
                cheapest_price = float('inf')
                
                for product in matching:
                    price = get_product_price(product)
                    if price and price < cheapest_price:
                        cheapest = product
                        cheapest_price = price
                
                if not cheapest:
                    shop_complete = False
                    break
                
                shop_products.append({
                    'searched_term': item,
                    'name': cheapest.name,
                    'price': cheapest_price,
                    'is_discounted': cheapest.is_discounted,
                    'url': cheapest.url,
                })
            
            # Only include shop if it has ALL items
            if shop_complete and shop_products:
                total = round(sum(p['price'] for p in shop_products), 2)
                shop_results[shop] = {
                    'products': shop_products,
                    'total': total
                }
        
        # Find cheapest complete shop
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
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class GlossaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    
# LOGIN/REGISTER ENDPOINTS
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful.",
                "tokens": get_token_for_user(user)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)