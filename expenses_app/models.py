from django.db import models
from accounts_app.models import User
from django.utils import timezone


class Expense(models.Model):
    category = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expense")
    date = models.DateField(null=False, blank=False, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return "{} - {}".format(self.category, self.owner)