from django.contrib import admin
from .models import Library

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    """Admin configuration for the Library model."""
    list_display = ('name', 'city', 'admin', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'country')
    search_fields = ('name', 'address', 'city', 'admin__email')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'image')}),
        ('Contact Information', {'fields': ('address', 'city', 'state', 'postal_code', 'country', 'phone', 'email', 'website')}),
        ('Management', {'fields': ('admin', 'staff', 'opening_hours', 'established_date')}),
        ('Status', {'fields': ('is_active',)}),
    )

    filter_horizontal = ('staff',)
