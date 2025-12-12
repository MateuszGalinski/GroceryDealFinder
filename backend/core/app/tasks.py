from celery import shared_task
from .scraper.scraper import get_shops_data
from .serializers import ProductSerializer
from .models import Product

@shared_task
def debug_task():
    print("20 seconds later")


@shared_task
def update_discount_database():
    shops_data = get_shops_data()
    
    for shop_name, products in shops_data.items():
        for p in products:
            data = {
                'url': p['Url'],
                'name': p['Name'],
                'price': p['Price'],
                'details': p['Details'],
                'is_discounted': p['Is_Discounted'],
                'discounted_price': p.get('Discounted_Price'),
                'shop': shop_name,
            }
            
            try:
                product = Product.objects.get(url=p['Url'])
                serializer = ProductSerializer(product, data=data)
            except Product.DoesNotExist:
                serializer = ProductSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
            else:
                print(f"Error saving {p['Name']}: {serializer.errors}")
    
    print("Shops updated")