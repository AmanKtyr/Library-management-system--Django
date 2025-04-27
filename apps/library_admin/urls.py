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

    # Membership request URLs
    path('membership-requests/', views.membership_requests, name='membership_requests'),
    path('membership-requests/approve/', views.approve_membership_request, name='approve_membership_request'),
    path('membership-requests/reject/', views.reject_membership_request, name='reject_membership_request'),
]
