from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
]
