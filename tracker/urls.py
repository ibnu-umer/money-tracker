from django.urls import path
from . import views



urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('edit-transaction/', views.edit_transaction, name='edit_transaction'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('fetch-monthly-data/', views.fetch_monthly_data, name='fetch_monthly_data'),
]
