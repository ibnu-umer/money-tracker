from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, LoginForm
from django.http import JsonResponse
from django.contrib import messages
from .models import Category, Transaction, HiddenCategory
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Sum
from django.utils.timezone import now
import datetime
import calendar
import ast



@login_required(login_url='login') 
def dashboard(request):
    
    # Get selected month/year from query params (or use current)
    month = int(request.GET.get('month', datetime.date.today().month))
    year = int(request.GET.get('year', datetime.date.today().year))
    
    # Define date range for the selected month
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    
    hidden_ids = HiddenCategory.objects.filter(user=request.user).values_list('category_id', flat=True)
    
    income_categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True),
        type='income'
    ).exclude(id__in=hidden_ids).order_by('name')

    expense_categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True),
        type='expense'
    ).exclude(id__in=hidden_ids).order_by('name')
    
    
    # Retrieve transaction data for the current month
    current_month_start = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    transactions = Transaction.objects.filter(
        user=request.user,
        date__range=(start_date, end_date)
    ).order_by('-date')
    
    
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
            user=request.user,
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
            user=request.user,
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
        request, 'tracker/dashboard.html',
        {
            'transactions': transactions, 
            'income_categories': table_data['income'],
            'expense_categories': table_data['expense'],
            'table_data': table_data,
            'today': datetime.date.today().isoformat(),
            'selected_month': month,
            'selected_year': year,
            'pie_chart_labels': pie_chart_lables,
            'pie_chart_data': pie_chart_data,
            'chart_labels': chart_labels,
            'bar_chart_data': bar_chart_data,
            'balance_data': balance_data,
            'months': [(i, calendar.month_abbr[i]) for i in range(1, 13)]
        }
    )
    
    
    
    


def fetch_monthly_data(request):
    month = int(request.GET.get('month'))
    year = int(request.GET.get('year'))

    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    transactions = (
        Transaction.objects.filter(
            user=request.user,
            type='expense',
            date__range=(start_date, end_date)
        )
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    return JsonResponse(list(transactions), safe=False)

    
    
    
    
    

@login_required(login_url='login')
def add_transaction(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        tx_type = request.POST.get('tx_type')
        
    
        # Add to transactions DB
        
        # Check category in user created
        cat = Category.objects.get(name=category, type=tx_type, user_id=request.user)
        if not cat: # If not found, check in default
            cat = Category.objects.get(name=category, type=tx_type)

        Transaction.objects.create(
            date=date, 
            category=cat,
            amount=amount,
            type=tx_type,
            note=note,
            user= request.user

        )
        
        return redirect('dashboard')
    
    
@login_required(login_url='login')
def edit_transaction(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        tx_id = request.POST.get('tx_id')
        
        if action == 'save':
            old_data = ast.literal_eval(request.POST.get('old_data'))
            category_name = request.POST.get('category')
            note = request.POST.get('note')
            amount = request.POST.get('amount')
            date = request.POST.get('date')
            
            transaction = get_object_or_404(Transaction, id=tx_id)
            category_obj = get_object_or_404(
                    Category,
                    user=request.user,
                    name=category_name,
                    type=old_data.get('type')
            )
            
            transaction.category = category_obj
            transaction.note = note
            transaction.amount = amount
            transaction.date = date
            transaction.save()
        
        elif action == 'delete':
           Transaction.objects.filter(id=tx_id).delete()
           messages.success(request, "Transaction deleted successfully.")
        
        return redirect('dashboard')


@login_required(login_url='login')
def manage_categories(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        icon = request.POST.get('icon')
        name = request.POST.get('name')
        category_id = request.POST.get('id')
        tx_type = request.POST.get('type')

        if action == 'add':
            cat_exists = Category.objects.filter(name=name, user=request.user, type=tx_type).exists()
            if cat_exists:
                messages.error(request, 'The category name is already used.')
            else:
                Category.objects.create(user=request.user, name=name, icon=icon, type=tx_type)  
                messages.success(request, f'Successfully created categroy {name}')
            
        elif action == 'edit' and category_id:
            Category.objects.filter(id=category_id, user=request.user).update(name=name, icon=icon, type=tx_type)
            
        elif action == 'delete' and category_id:
            has_data = Transaction.objects.filter(category_id=category_id, user=request.user).exists()
           
            if has_data: # if the category has no data exist
                messages.error(request, "This category cannot be deleted as it has associated transactions.")
            else:
                messages.success(request, "Category deleted successfull.")
                obj = Category.objects.filter(id=category_id, user=request.user)
                if obj:
                    obj.delete() # delete if user created object
                else:  # Hide from the user by saving the categroy id and user id by filtering 
                    HiddenCategory.objects.create(
                        category=Category.objects.get(id=category_id),
                        user=request.user
                    )

        return redirect('dashboard')  
    
    
    
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('dashboard')  
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')
