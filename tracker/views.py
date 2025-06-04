from django.shortcuts import render, redirect
from .forms import IncomeForm
from .models import Category, Income, Expense
from datetime import date



def home(request):
    income_categories = Category.objects.filter(type='income').order_by('name')
    expense_categories = Category.objects.filter(type='expense').order_by('name')
    
    transactions = [
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Health', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Health', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
        {'icon': '🛒', 'category': 'Groceries', 'note': '01 Jun - Bought vegetables', 'amount': 300, 'type': 'income'},
        {'icon': '🚌', 'category': 'Transport', 'note': '01 Jun - Bus fare', 'amount': 150, 'type': 'expense'},
        {'icon': '💼', 'category': 'Salary', 'note': '02 Jun - Monthly salary', 'amount': 30000, 'type': 'income'},
        {'icon': '☕', 'category': 'Health', 'note': '02 Jun - Evening coffee', 'amount': 100, 'type': 'expense'},
    ]
    
    
    return render(
        request, 'tracker/home.html',
        {
            'transactions': transactions, 
            'income_categories': income_categories,
            'expense_categories': expense_categories,
            'today': date.today().isoformat()
        }
    )
    




def add_income(request):
    if request.method == "POST":
        date = request.POST.get("date")
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        note = request.POST.get("note")
        Income.objects.create(date=date, category=category, amount=amount, note=note)
        return redirect("home") 
    
    
def add_expense(request):
    if request.method == "POST":
        date = request.POST.get("date")
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        note = request.POST.get("note")
        Expense.objects.create(date=date, category=category, amount=amount, note=note)
        return redirect("home") 




def income_list_create(request):
    form = IncomeForm()
    incomes = Income.objects.all()

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income')  # replace with your actual URL name

    return render(request, 'tracker/income.html', {'form': form, 'incomes': incomes})



def dashboard(request):
    context = {
        'income_categories': ['Salary', 'Freelance', 'Bonus'],
        'expense_categories': ['Food', 'Rent', 'Transport'],
        'today': date.today().isoformat()
    }
    return render(request, 'tracker/home.html', context)