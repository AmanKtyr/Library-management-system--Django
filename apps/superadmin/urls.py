from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    # Library management
    path('libraries/', views.manage_libraries, name='libraries'),
    path('libraries/create/', views.create_library, name='create_library'),
    path('libraries/<slug:slug>/edit/', views.edit_library, name='edit_library'),
    path('libraries/<slug:slug>/delete/', views.delete_library, name='delete_library'),

    # User management
    path('users/', views.manage_users, name='users'),

    # Book management
    path('books/', views.manage_books, name='books'),

    # Transaction management
    path('transactions/', views.manage_transactions, name='transactions'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
