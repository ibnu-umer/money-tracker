from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Transaction
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils.timezone import now
import datetime
from decimal import Decimal
import ast



def home(request):
    income_categories = Category.objects.filter(type='income').order_by('name')
    expense_categories = Category.objects.filter(type='expense').order_by('name')
    
    # Retrieve transaction data for the current month
    current_month_start = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    transactions = Transaction.objects.filter(date__gte=current_month_start).order_by('-date')
    
    #! Pie Chart Data
    # Expense data for pie chart
    breakdown = (
        transactions
        .filter(type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    pie_chart_lables = [item['category__name'] for item in breakdown]
    pie_chart_data = [float(item['total']) for item in breakdown]
    
    
    #! Bar Chart Data
    # Get Incomes and Expeneses for the past 3 and currnet month
    start_month = current_month_start - relativedelta(months=3)
    monthly_expenses = (
        Transaction.objects.filter(
            type='expense',
            date__gte=start_month,
            date__lte=datetime.date.today()
        )
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    
    monthly_incomes = (
        Transaction.objects.filter(
            type='income',
            date__gte=start_month,
            date__lte=datetime.date.today()
        )
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    
    expense_dict = {e['month'].strftime('%b'): e['total'] for e in monthly_expenses}
    income_dict = {i['month'].strftime('%b'): i['total'] for i in monthly_incomes}
    bar_chart_labels = [  # Get last 4 month names
        (datetime.datetime.today() - relativedelta(months=i)).strftime('%b')
        for i in range(3, -1, -1)
    ]
    
    bar_chart_data = [ # Get last 4 months data, if not exists, create with 0
        [float(income_dict.get(month, 0)), float(expense_dict.get(month, 0))]
        for month in bar_chart_labels
    ]
    
    
    
    return render(
        request, 'tracker/home.html',
        {
            'transactions': transactions, 
            'income_categories': income_categories,
            'expense_categories': expense_categories,
            'today': datetime.date.today().isoformat(),
            'pie_chart_labels': pie_chart_lables,
            'pie_chart_data': pie_chart_data,
            'bar_chart_labels': bar_chart_labels,
            'bar_chart_data': bar_chart_data
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




