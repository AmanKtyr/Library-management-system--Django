from django.urls import path
from . import views

app_name = 'library_admin'

urlpatterns = [
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('statistics/', views.statistics, name='statistics'),

    # Catalog Management URLs
    path('books/', views.manage_books, name='books'),

    # Categories URLs
    path('categories/', views.manage_categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/<slug:slug>/edit/', views.edit_category, name='edit_category'),

    # Authors URLs
    path('authors/', views.authors_collection, name='authors_collection'),
    path('authors/add/', views.add_author, name='add_author'),
    path('authors/<slug:slug>/edit/', views.edit_author, name='edit_author'),
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),

    # Publishers URLs
    path('publishers/', views.manage_publishers, name='publishers'),
    path('publishers/add/', views.add_publisher, name='add_publisher'),
    path('publishers/<slug:slug>/edit/', views.edit_publisher, name='edit_publisher'),
    path('publishers/<slug:slug>/', views.publisher_detail, name='publisher_detail'),

    # People Management URLs
    path('staff/', views.manage_staff, name='staff'),

    # Circulation URLs
    path('circulation/', views.circulation, name='circulation'),
    path('circulation/issue-book/', views.issue_book, name='issue_book'),
    path('circulation/return-book/', views.return_book, name='return_book'),
    path('transactions/', views.manage_transactions, name='transactions'),
    path('reservations/', views.manage_reservations, name='reservations'),
    path('reservations/confirm/<int:reservation_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),

    # Membership request URLs
    path('membership-requests/', views.membership_requests, name='membership_requests'),
    path('membership-requests/approve/', views.approve_membership_request, name='approve_membership_request'),
    path('membership-requests/reject/', views.reject_membership_request, name='reject_membership_request'),

    # Membership Management URLs
    path('membership/', views.membership_dashboard, name='membership_dashboard'),

    path('membership-plans/', views.membership_plans, name='membership_plans'),
    path('membership-plans/add/', views.add_membership_plan, name='add_membership_plan'),
    path('membership-plans/<int:plan_id>/edit/', views.edit_membership_plan, name='edit_membership_plan'),
    path('membership-plans/<int:plan_id>/delete/', views.delete_membership_plan, name='delete_membership_plan'),

    path('members/', views.members, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/renew/', views.renew_membership, name='renew_membership'),
    path('members/<int:member_id>/profile/', views.member_profile, name='member_profile'),

    path('member-attendance/', views.member_attendance, name='member_attendance'),
    path('member-attendance/record/', views.record_attendance, name='record_attendance'),
    path('member-attendance/report/', views.attendance_report, name='attendance_report'),

    # Reports & Analytics URLs
    path('reports/', views.reports, name='reports'),
    path('reports/transactions/', views.transaction_reports, name='transaction_reports'),
    path('reports/custom/', views.custom_reports, name='custom_reports'),
    path('reports/export/', views.export_reports, name='export_reports'),

    # Administration URLs
    path('settings/', views.settings, name='settings'),
    path('settings/general/', views.general_settings, name='general_settings'),
    path('settings/circulation/', views.circulation_settings, name='circulation_settings'),
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/appearance/', views.appearance_settings, name='appearance_settings'),

    path('notifications/', views.notifications, name='notifications'),
    path('help/', views.help_documentation, name='help'),
    path('system-status/', views.system_status, name='system_status'),

    # Library Details URL - accessible at both paths
    path('', views.library_details, name='library_details'),  # Root path
    path('library/', views.library_details, name='library_details_alt'),
    path('edit/', views.edit_library, name='edit_library'),
    path('library/edit/', views.edit_library, name='edit_library_alt'),
]
