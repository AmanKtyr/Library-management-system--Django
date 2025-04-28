from django import forms
from .models import Book, Author, Category, BookCopy

class AuthorForm(forms.ModelForm):
    """Form for creating and updating authors."""

    class Meta:
        model = Author
        fields = ['name', 'biography', 'date_of_birth', 'date_of_death', 'photo']
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date'}),
        }

class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BookForm(forms.ModelForm):
    """Form for creating and updating books."""

    # Custom fields for author and category input
    author_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter author name and press Enter',
            'data-role': 'author-input'
        })
    )

    category_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter category name and press Enter',
            'data-role': 'category-input'
        })
    )

    class Meta:
        model = Book
        fields = [
            'title', 'authors', 'categories', 'isbn', 'publisher',
            'publication_date', 'summary', 'cover_image', 'language', 'pages'
        ]
        widgets = {
            'authors': forms.CheckboxSelectMultiple(attrs={'class': 'author-checkbox-list'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'category-checkbox-list'}),
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

class BookCopyForm(forms.ModelForm):
    """Form for creating and updating book copies."""

    class Meta:
        model = BookCopy
        fields = ['book', 'inventory_number', 'condition', 'status', 'acquisition_date', 'price', 'notes']
        widgets = {
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If the form is being used by a library admin or staff, limit book choices
        # to books that are already in their library or new books
        if user and (user.is_library_admin or user.is_staff_member):
            # This is a simplified approach - in a real app, you might want to show
            # all books but highlight ones already in the library
            pass
