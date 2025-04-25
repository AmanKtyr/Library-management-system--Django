from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('memberships/', views.memberships, name='memberships'),
    path('transactions/', views.transactions, name='transactions'),
    path('borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('reserved-books/', views.reserved_books, name='reserved_books'),
    path('fines/', views.fines, name='fines'),
]
