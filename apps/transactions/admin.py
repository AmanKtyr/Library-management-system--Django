from django.contrib import admin
from .models import Transaction, MembershipPlan, Membership

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for the Transaction model."""
    list_display = ('transaction_id', 'book_copy', 'user', 'transaction_type', 'status', 'transaction_date', 'due_date')
    list_filter = ('transaction_type', 'status', 'transaction_date', 'library')
    search_fields = ('transaction_id', 'book_copy__book__title', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'transaction_date'

    fieldsets = (
        (None, {'fields': ('book_copy', 'library', 'user', 'transaction_type', 'status')}),
        ('Dates', {'fields': ('due_date', 'return_date')}),
        ('Fines', {'fields': ('fine_amount', 'fine_paid', 'fine_payment_date')}),
        ('Additional Information', {'fields': ('notes', 'processed_by')}),
    )

    readonly_fields = ('transaction_id', 'transaction_date')

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    """Admin configuration for the MembershipPlan model."""
    list_display = ('name', 'duration_days', 'max_books_allowed', 'price', 'is_active')
    list_filter = ('is_active', 'duration_days', 'max_books_allowed')
    search_fields = ('name', 'description')

    fieldsets = (
        (None, {'fields': ('name', 'description', 'price', 'is_active')}),
        ('Rules', {'fields': ('duration_days', 'max_books_allowed', 'max_borrowing_days')}),
    )

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Admin configuration for the Membership model."""
    list_display = ('membership_number', 'user', 'library', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date', 'library', 'plan')
    search_fields = ('membership_number', 'user__email', 'user__first_name', 'user__last_name', 'library__name')
    date_hierarchy = 'start_date'

    fieldsets = (
        (None, {'fields': ('user', 'library', 'plan', 'membership_number')}),
        ('Dates', {'fields': ('start_date', 'end_date', 'is_active')}),
    )

    readonly_fields = ('membership_number',)
