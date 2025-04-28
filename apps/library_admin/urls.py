from django.urls import path
from . import views

app_name = 'library_admin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/', views.manage_staff, name='staff'),
    path('books/', views.manage_books, name='books'),
    path('categories/', views.manage_categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('members/', views.manage_members, name='members'),
    path('transactions/', views.manage_transactions, name='transactions'),
    path('reports/', views.reports, name='reports'),

    # New pages
    path('settings/', views.settings, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('help/', views.help_documentation, name='help'),
    path('analytics/', views.analytics, name='analytics'),

    # Membership request URLs
    path('membership-requests/', views.membership_requests, name='membership_requests'),
    path('membership-requests/approve/', views.approve_membership_request, name='approve_membership_request'),
    path('membership-requests/reject/', views.reject_membership_request, name='reject_membership_request'),
]
