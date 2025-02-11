from django.db import models
from users.models import CustomUser

class Analytics(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.IntegerField()
    date = models.DateField()

    class Meta:
        unique_together = ('seller', 'date')

    def __str__(self):
        return f"Analytics for {self.seller.username} on {self.date}"