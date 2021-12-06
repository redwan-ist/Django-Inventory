from django.db import models
from datetime import datetime

from django.db.models.base import Model

# Create your models here.


class cat(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class product(models.Model):
    title = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    total_sell = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    category = models.CharField(max_length=100)
    date = models.DateField(default=datetime.today)

    def __str__(self):
        return self.title


class sell(models.Model):
    product_id = models.IntegerField(default=0)
    product_title = models.CharField(max_length=100)
    buyer = models.CharField(max_length=100, default='buyer')
    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField(default=0)
    delivered = models.BooleanField(default=False)
    category = models.CharField(max_length=100, null=True)
    date = models.DateField(default=datetime.today)

    def __str__(self):
        return self.product_title


class accounts(models.Model):
    total = models.IntegerField(default=0)
    clearence = models.IntegerField(default=0)
