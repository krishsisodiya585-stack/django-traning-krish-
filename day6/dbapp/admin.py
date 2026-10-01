from django.contrib import admin
from .models import Client, Customer, Order

admin.site.register(Client)
admin.site.register(Customer)
admin.site.register(Order)
