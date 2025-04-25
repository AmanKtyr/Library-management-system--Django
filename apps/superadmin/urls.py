from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('libraries/', views.manage_libraries, name='libraries'),
    path('users/', views.manage_users, name='users'),
    path('books/', views.manage_books, name='books'),
    path('transactions/', views.manage_transactions, name='transactions'),
    path('reports/', views.reports, name='reports'),
]
