from django.urls import path
from . import views

app_name = 'transactions'


urlpatterns = [
    path('transactions/', views.transaction_list, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('transactions/edit/<int:pk>/', views.transaction_edit, name='transaction_edit'),
    path('transactions/delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
]