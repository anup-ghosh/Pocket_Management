from django.db import models
from accounts.models import CustomUser
from decimal import Decimal

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense')
    ]
    
    CATEGORY_CHOICES = [
        # Income Categories
        ('SALARY', 'Salary'),
        ('BUSINESS', 'Business'),
        ('FREELANCE', 'Freelance'),
        ('INVESTMENT', 'Investment'),
        ('OTHER_INCOME', 'Other Income'),
        # Expense Categories
        ('FOOD', 'Food & Dining'),
        ('TRANSPORT', 'Transportation'),
        ('UTILITIES', 'Utilities'),
        ('RENT', 'Rent'),
        ('SHOPPING', 'Shopping'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('HEALTHCARE', 'Healthcare'),
        ('EDUCATION', 'Education'),
        ('OTHER_EXPENSE', 'Other Expense'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'INCOME':
            self.user.balance += self.amount
        else:
            if self.amount > self.user.balance:
                raise ValueError("Insufficient balance")
            self.user.balance -= self.amount
        self.user.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.transaction_type == 'INCOME':
            self.user.balance -= self.amount
        else:
            self.user.balance += self.amount
        self.user.save()
        super().delete(*args, **kwargs)

class Budget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=Transaction.CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()

    class Meta:
        unique_together = ['user', 'category', 'month']