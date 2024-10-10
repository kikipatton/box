# models.py
from django.db import models
from django.core.exceptions import ValidationError

class Subscription(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)