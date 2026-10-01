from django.db import models


class Client(models.Model):
    client_name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=50, unique=True)
    client_company = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.client_name


class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=50, unique=True)
    customer_company = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.customer_name


class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateField()
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.order_id