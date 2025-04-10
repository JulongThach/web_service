from django.contrib import admin

from steakhouse.models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)