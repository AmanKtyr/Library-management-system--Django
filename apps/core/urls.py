from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('mission/', views.mission, name='mission'),
    path('contact/', views.contact, name='contact'),

    # Custom Admin Panel URLs
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/libraries/', views.admin_libraries, name='admin_libraries'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/books/', views.admin_books, name='admin_books'),
    path('admin-panel/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),

    # Library Admin Panel URLs
    path('library-admin-panel/', views.library_admin_panel, name='library_admin_panel'),

    # Admin Login/Logout
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # User Login/Logout
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
]
