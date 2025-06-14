from django.db import models
from django.contrib.auth.models import User



class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=10, blank=False, help_text='Emoji or short icon')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def save(self, *args, **kwargs):
        self.name = self.name.capitalize()  
        super().save(*args, **kwargs)
    

    def __str__(self):
        return f'{self.name}'



class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    type = models.CharField(max_length=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


    
class HiddenCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')
