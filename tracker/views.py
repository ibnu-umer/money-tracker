from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, Transaction
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils.timezone import now
import datetime
import ast



def home(request):
    income_categories = Category.objects.filter(type='income').order_by('name')
    expense_categories = Category.objects.filter(type='expense').order_by('name')
    
    # Retrieve transaction data for the current month
    current_month_start = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    transactions = Transaction.objects.filter(date__gte=current_month_start).order_by('-date')
    
    
    #! Data for Category table
    table_data = {
        'income': {category: float(0) for category in income_categories},
        'expense': {category: float(0) for category in expense_categories}
    }

    for tx in transactions:
        table_data[tx.type][tx.category] += float(tx.amount)
        
    
    #! Pie Chart Data
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
    chart_labels = [  # Get last 4 month names
        (datetime.datetime.today() - relativedelta(months=i)).strftime('%b')
        for i in range(3, -1, -1)
    ]
    
    bar_chart_data = [ # Get last 4 months data, if not exists, create with 0
        [float(income_dict.get(month, 0)), float(expense_dict.get(month, 0))]
        for month in chart_labels
    ]
    
    
    #! Balance chart
    balance_data = [data[0] - data[1] for data in bar_chart_data]

    
    return render(
        request, 'tracker/home.html',
        {
            'transactions': transactions, 
            'income_categories': table_data['income'],
            'expense_categories': table_data['expense'],
            'table_data': table_data,
            'today': datetime.date.today().isoformat(),
            'pie_chart_labels': pie_chart_lables,
            'pie_chart_data': pie_chart_data,
            'chart_labels': chart_labels,
            'bar_chart_data': bar_chart_data,
            'balance_data': balance_data
        }
    )
    


def add_transaction(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        tx_type = request.POST.get('tx_type')
        
    
        # Add to transactions DB
        cat = Category.objects.get(name=category, type=tx_type)
        Transaction.objects.create(
            date=date, 
            category=cat,
            amount=amount,
            type=tx_type,
            note=note,
        )
        
        return redirect('home')
    
    

def edit_transaction(request):
    if request.method == 'POST':
        old_data = ast.literal_eval(request.POST.get('old_data'))
        tx_id = request.POST.get('tx_id')
        category_name = request.POST.get('category')
        note = request.POST.get('note')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        
        transaction = get_object_or_404(Transaction, id=tx_id)
        category_obj = get_object_or_404(
                Category,
                name=category_name,
                type=old_data.get('type')
        )
        
        transaction.category = category_obj
        transaction.note = note
        transaction.amount = amount
        transaction.date = date
        transaction.save()
        
        return redirect('home')



def manage_categories(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        icon = request.POST.get('icon')
        name = request.POST.get('name')
        category_id = request.POST.get('id')
        tx_type = request.POST.get('type')

        if action == 'add':
            Category.objects.create(name=name, icon=icon, type=tx_type)  
            
        elif action == 'edit' and category_id: 
            Category.objects.filter(id=category_id).update(name=name, icon=icon)
            
        elif action == 'delete' and category_id:
            Transaction.objects.filter(category_id=category_id)
            has_data = Transaction.objects.filter(category_id=category_id).exists()
           
            if has_data: # if the category has no data exist
                messages.error(request, "This category cannot be deleted as it has associated transactions.")
            else:
                messages.success(request, "Category deleted successfull.")
                Category.objects.filter(id=category_id).delete()

        return redirect('home')  
