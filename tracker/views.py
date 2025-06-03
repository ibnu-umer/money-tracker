from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm



def home(request):
    transactions = [
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Coffee', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Coffee', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Coffee', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
    ]
    return render(request, 'tracker/home.html', {'transactions': transactions})
    

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'tracker/add_transaction.html', {'form': form})


