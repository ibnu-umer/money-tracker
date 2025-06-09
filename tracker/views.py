from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Transaction
from datetime import date
from decimal import Decimal
import ast



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
    
    

def edit_transaction(request):
    if request.method == 'POST':
        old_data = ast.literal_eval(request.POST.get('old_data'))
        tx_id = request.POST.get('tx_id')
        category_name = request.POST.get('category')
        note = request.POST.get('note')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        
        transaction = get_object_or_404(Transaction, id=tx_id)
        category = get_object_or_404(
                Category,
                name=old_data.get('category'),
                type=old_data.get('type')
        )
        
        
        # Update category values if amount or category has any changes
        if category_name != old_data.get('category'):
            # Substract the amount from the old category total
            category.total -= Decimal(old_data.get('amount'))
            category.save()
            
            category = get_object_or_404(Category, name=category_name, type=transaction.type)
            category.total += Decimal(amount)  
            category.save()
            
        elif old_data.get('amount') != amount:
            # No category change, amount changed
            category.total -= Decimal(old_data.get('amount'))
            category.total += Decimal(amount)
            category.save()
            
       

        transaction.category = category
        transaction.note = note
        transaction.amount = amount
        transaction.date = date
        transaction.save()
        
        return redirect('home')




