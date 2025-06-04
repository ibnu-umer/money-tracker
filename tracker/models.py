from django.db import models




class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=10, blank=False, help_text="Emoji or short icon")

    def __str__(self):
        return f"{self.name}"




class Income(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=500)
    
    
    
class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=500)
    
    
    
