from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    url = models.URLField()
    name = models.CharField(max_length = 300)
    price = models.FloatField()

class Disscount(models.Model):
    product = models.OneToOneField(Product, on_delete = models.DO_NOTHING)
    discounted_price = models.FloatField()
    old_price = models.FloatField()

class Glossary(models.Model):
    user = models.OneToOneField(User, on_delete = models.DO_NOTHING)
    translations = models.JSONField()