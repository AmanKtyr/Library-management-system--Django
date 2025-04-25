from django.urls import path
from . import views

app_name = 'library_admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/', views.manage_staff, name='staff'),
    path('books/', views.manage_books, name='books'),
    path('members/', views.manage_members, name='members'),
    path('transactions/', views.manage_transactions, name='transactions'),
    path('reports/', views.reports, name='reports'),
]
