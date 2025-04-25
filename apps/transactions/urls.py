from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('borrow/', views.borrow_book, name='borrow_book'),
    path('return/', views.return_book, name='return_book'),
    path('reserve/', views.reserve_book, name='reserve_book'),
    path('memberships/', views.membership_list, name='membership_list'),
    path('memberships/<str:membership_number>/', views.membership_detail, name='membership_detail'),
    path('memberships/new/', views.new_membership, name='new_membership'),
    path('reports/', views.transaction_reports, name='transaction_reports'),
]
