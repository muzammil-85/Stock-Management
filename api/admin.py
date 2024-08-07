from django.contrib import admin

from api.models import Product, SubVariant, Variant

# Register your models here.
admin.site.register(Product)
admin.site.register(Variant)
admin.site.register(SubVariant)