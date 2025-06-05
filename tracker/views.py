from django.shortcuts import render, redirect
from .models import Category, Transaction
from datetime import date
from decimal import Decimal



def home(request):
    income_categories = Category.objects.filter(type='income').order_by('name')
    expense_categories = Category.objects.filter(type='expense').order_by('name')
    
    transactions = Transaction.objects.all().order_by('date')
    
    return render(
        request, 'tracker/home.html',
        {
            'transactions': transactions, 
            'income_categories': income_categories,
            'expense_categories': expense_categories,
            'today': date.today().isoformat()
        }
    )
    


def add_transaction(request):
    if request.method == 'POST':
        date = request.POST.get("date")
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        note = request.POST.get("note")
        tx_type = request.POST.get("tx_type")
        
        # Add to Category DB
        cat = Category.objects.get(name=category, type=tx_type)
        cat.total += Decimal(amount)
        cat.save()
        
        # Add to transactions DB
        Transaction.objects.create(
            date=date, 
            category=cat,
            amount=amount,
            type=tx_type,
            note=note,
        )
        
        return redirect("home")




