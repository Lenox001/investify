from django.db import models
from django.contrib.auth.models import User
from datetime import date  # Import date from the datetime module

# Create your models here.

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class RecentActivity(models.Model):  # Ensure this class is not nested
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Newest activities first

    def __str__(self):
        return self.activity
    
    
class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    maturity_date = models.DateField()
    invested_at = models.DateTimeField(auto_now_add=True)

    @property
    def progress(self):
        """Calculate progress percentage based on the current date and maturity date."""
        if self.maturity_date > self.invested_at.date():
            total_days = (self.maturity_date - self.invested_at.date()).days
            elapsed_days = (date.today() - self.invested_at.date()).days
            return min(100, (elapsed_days / total_days) * 100)
        return 100  # Fully matured

    def __str__(self):
        return f'Investment of {self.amount} by {self.user.username}'
    
 

class Transaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    transaction_type = models.CharField(max_length=50, default='UNKNOWN')

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"

