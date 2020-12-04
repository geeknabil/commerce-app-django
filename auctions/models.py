from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class Product(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    starting_bid = models.IntegerField()
    img = models.TextField()

    def __str__(self):
        return f"{self.title}"

class User(AbstractUser):
    products = models.ManyToManyField(Product, blank=True, related_name="users")
    
    def __str__(self):
        return f"{self.username}"


class WatchList(models.Model):
    products = models.ManyToManyField(Product, blank=True, related_name="watchlists")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="watchList")

    def __str__(self):
        return f"watchlist {self.id}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bid")
    price = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="bid")

    def __str__(self): 
        return f"bid {self.id}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comment")
    comment = models.CharField(max_length=64)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="comment")

    def __str__(self):
        return f"comment {self.id}"