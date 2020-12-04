from django.contrib import admin
from .models import User, Product, WatchList, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(WatchList)
admin.site.register(Bid)
admin.site.register(Comment)