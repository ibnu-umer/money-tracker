from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('edit-transaction/', views.edit_transaction, name='edit_transaction'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
