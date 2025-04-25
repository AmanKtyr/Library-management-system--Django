from django.contrib import admin
from .models import Author, Category, Book, BookCopy

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin configuration for the Author model."""
    list_display = ('name', 'date_of_birth', 'date_of_death')
    list_filter = ('date_of_birth', 'date_of_death')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'biography', 'photo')}),
        ('Dates', {'fields': ('date_of_birth', 'date_of_death')}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class BookCopyInline(admin.TabularInline):
    """Inline admin configuration for BookCopy model."""
    model = BookCopy
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for the Book model."""
    list_display = ('title', 'display_authors', 'isbn', 'display_categories')
    list_filter = ('publication_date', 'language')
    search_fields = ('title', 'authors__name', 'isbn')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'authors', 'categories', 'isbn')}),
        ('Details', {'fields': ('publisher', 'publication_date', 'language', 'pages')}),
        ('Content', {'fields': ('summary', 'cover_image')}),
    )

    filter_horizontal = ('authors', 'categories')
    inlines = [BookCopyInline]

    def display_authors(self, obj):
        """Create a string for the authors (for display in Admin)."""
        return ', '.join([author.name for author in obj.authors.all()[:3]])

    display_authors.short_description = 'Authors'

    def display_categories(self, obj):
        """Create a string for the categories (for display in Admin)."""
        return ', '.join([category.name for category in obj.categories.all()[:3]])

    display_categories.short_description = 'Categories'

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    """Admin configuration for the BookCopy model."""
    list_display = ('inventory_number', 'book', 'library', 'status', 'condition')
    list_filter = ('status', 'condition', 'library')
    search_fields = ('inventory_number', 'book__title', 'library__name')

    fieldsets = (
        (None, {'fields': ('book', 'library', 'inventory_number')}),
        ('Status', {'fields': ('status', 'condition')}),
        ('Details', {'fields': ('acquisition_date', 'price', 'notes')}),
    )
