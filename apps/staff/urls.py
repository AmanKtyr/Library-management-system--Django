from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.manage_books, name='books'),
    path('transactions/', views.manage_transactions, name='transactions'),
    path('issue-book/', views.issue_book, name='issue_book'),
    path('return-book/', views.return_book, name='return_book'),
    path('members/', views.manage_members, name='members'),
]
