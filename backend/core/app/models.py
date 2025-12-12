from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    url = models.URLField()
    name = models.CharField(max_length = 300)
    price = models.CharField(max_length = 200)
    details = models.TextField(null = True, blank = True)
    is_discounted = models.BooleanField()
    discounted_price = models.CharField(max_length = 200, null = True, blank = True)
    shop = models.CharField(max_length = 200)

class Glossary(models.Model):
    user = models.OneToOneField(User, on_delete = models.DO_NOTHING)
    translations = models.JSONField()