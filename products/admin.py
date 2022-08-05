from django.contrib import admin
from .models import Product, Comment, Offer
from mptt.admin import MPTTModelAdmin
# Register your models here.

admin.site.register(Comment, MPTTModelAdmin)
admin.site.register(Product)
admin.site.register(Offer)