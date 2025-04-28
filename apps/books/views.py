from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_GET
from .models import Book, Author, Category, BookCopy
from apps.libraries.models import Library
from .forms import BookForm, BookCopyForm  # AuthorForm and CategoryForm removed - now handled in library_admin app

def book_list(request):
    """View function for listing all books."""
    # Get search query from GET parameters
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    author_slug = request.GET.get('author', '')

    books = Book.objects.all()

    # Apply filters if provided
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        books = books.filter(categories=category)

    if author_slug:
        author = get_object_or_404(Author, slug=author_slug)
        books = books.filter(authors=author)

    # Get all categories and authors for filter sidebar
    categories = Category.objects.annotate(book_count=Count('books'))
    authors = Author.objects.annotate(book_count=Count('books'))

    context = {
        'books': books,
        'categories': categories,
        'authors': authors,
        'query': query,
        'selected_category': category_slug,
        'selected_author': author_slug,
    }

    return render(request, 'books/book_list.html', context)

def book_detail(request, slug):
    """View function for displaying details of a specific book."""
    book = get_object_or_404(Book, slug=slug)

    # Get all copies of this book grouped by library
    copies_by_library = {}
    for copy in book.copies.all():
        if copy.library not in copies_by_library:
            copies_by_library[copy.library] = []
        copies_by_library[copy.library].append(copy)

    context = {
        'book': book,
        'copies_by_library': copies_by_library,
    }

    return render(request, 'books/book_detail.html', context)

def author_list(request):
    """View function for listing all authors."""
    authors = Author.objects.annotate(book_count=Count('books')).order_by('name')

    context = {
        'authors': authors,
    }

    return render(request, 'books/author_list.html', context)

def author_detail(request, slug):
    """View function for displaying details of a specific author."""
    author = get_object_or_404(Author, slug=slug)
    books = author.books.all()

    context = {
        'author': author,
        'books': books,
    }

    return render(request, 'books/author_detail.html', context)

# Category views removed - now handled in library_admin app

@login_required
def manage_books(request):
    """View function for managing books."""
    user = request.user

    # Check if user has permission to manage books
    if not (user.is_super_admin or user.is_library_admin or user.is_staff_member):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get books based on user role
    if user.is_super_admin:
        books = Book.objects.all()
    elif user.is_library_admin:
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
            book_copies = BookCopy.objects.filter(library=library)
            books = Book.objects.filter(copies__in=book_copies).distinct()
        else:
            books = Book.objects.none()
    else:  # Staff
        libraries = user.staffed_libraries.all()
        if libraries.exists():
            library = libraries.first()
            book_copies = BookCopy.objects.filter(library=library)
            books = Book.objects.filter(copies__in=book_copies).distinct()
        else:
            books = Book.objects.none()

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(authors__name__icontains=search_query) |
            Q(isbn__icontains=search_query)
        ).distinct()

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 12)  # Show 12 books per page

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    # Get library for context
    library = None
    if user.is_library_admin:
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
    elif user.is_staff_member:
        libraries = user.staffed_libraries.all()
        if libraries.exists():
            library = libraries.first()

    context = {
        'books': books,
        'library': library,
    }

    return render(request, 'books/manage_books.html', context)

@require_GET
def autocomplete_authors(request):
    """API endpoint for author name autocomplete."""
    query = request.GET.get('q', '')
    if query:
        authors = Author.objects.filter(name__icontains=query)[:10]
        data = [{'id': author.id, 'name': author.name} for author in authors]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@require_GET
def autocomplete_categories(request):
    """API endpoint for category name autocomplete."""
    query = request.GET.get('q', '')
    if query:
        categories = Category.objects.filter(name__icontains=query)[:10]
        data = [{'id': category.id, 'name': category.name} for category in categories]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def add_book(request):
    """View function for adding a new book."""
    user = request.user

    # Check if user has permission to add books
    if not (user.is_super_admin or user.is_library_admin or user.is_staff_member):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get the user's library
    library = None
    if user.is_library_admin:
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
    elif user.is_staff_member:
        libraries = user.staffed_libraries.all()
        if libraries.exists():
            library = libraries.first()

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)

        # Process new authors if any
        new_authors = []
        author_names = request.POST.getlist('new_authors[]', [])
        for author_name in author_names:
            if author_name.strip():
                # Check if author already exists
                author, _ = Author.objects.get_or_create(
                    name=author_name.strip(),
                    defaults={'biography': f'Author of {request.POST.get("title", "a book")}'}
                )
                new_authors.append(author.id)

        # Process new categories if any
        new_categories = []
        category_names = request.POST.getlist('new_categories[]', [])
        for category_name in category_names:
            if category_name.strip():
                # Check if category already exists
                category, _ = Category.objects.get_or_create(
                    name=category_name.strip()
                )
                new_categories.append(category.id)

        if form.is_valid():
            book = form.save(commit=False)
            book.save()  # Save to generate ID

            # Add selected authors from form
            for author_id in form.cleaned_data['authors']:
                book.authors.add(author_id)

            # Add new authors
            for author_id in new_authors:
                book.authors.add(author_id)

            # Add selected categories from form
            for category_id in form.cleaned_data['categories']:
                book.categories.add(category_id)

            # Add new categories
            for category_id in new_categories:
                book.categories.add(category_id)

            messages.success(request, f"Book '{book.title}' added successfully.")
            return redirect('books:book_detail', slug=book.slug)
    else:
        form = BookForm()

    # Get all authors and categories for autocomplete
    all_authors = Author.objects.all().order_by('name')
    all_categories = Category.objects.all().order_by('name')

    context = {
        'form': form,
        'title': 'Add Book',
        'library': library,
        'all_authors': all_authors,
        'all_categories': all_categories,
    }

    return render(request, 'books/book_form.html', context)

@login_required
def edit_book(request, slug):
    """View function for editing a book."""
    user = request.user
    book = get_object_or_404(Book, slug=slug)

    # Check if user has permission to edit books
    if not (user.is_super_admin or user.is_library_admin):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get the user's library
    library = None
    if user.is_library_admin:
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
    elif user.is_staff_member:
        libraries = user.staffed_libraries.all()
        if libraries.exists():
            library = libraries.first()

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)

        # Process new authors if any
        new_authors = []
        author_names = request.POST.getlist('new_authors[]', [])
        for author_name in author_names:
            if author_name.strip():
                # Check if author already exists
                author, _ = Author.objects.get_or_create(
                    name=author_name.strip(),
                    defaults={'biography': f'Author of {request.POST.get("title", "a book")}'}
                )
                new_authors.append(author.id)

        # Process new categories if any
        new_categories = []
        category_names = request.POST.getlist('new_categories[]', [])
        for category_name in category_names:
            if category_name.strip():
                # Check if category already exists
                category, _ = Category.objects.get_or_create(
                    name=category_name.strip()
                )
                new_categories.append(category.id)

        if form.is_valid():
            book = form.save()

            # Add new authors
            for author_id in new_authors:
                book.authors.add(author_id)

            # Add new categories
            for category_id in new_categories:
                book.categories.add(category_id)

            messages.success(request, f"Book '{book.title}' updated successfully.")
            return redirect('books:book_detail', slug=book.slug)
    else:
        form = BookForm(instance=book)

    # Get all authors and categories for autocomplete
    all_authors = Author.objects.all().order_by('name')
    all_categories = Category.objects.all().order_by('name')

    context = {
        'form': form,
        'book': book,
        'title': 'Edit Book',
        'library': library,
        'all_authors': all_authors,
        'all_categories': all_categories,
    }

    return render(request, 'books/book_form.html', context)

@login_required
def delete_book(request, pk):
    """View function for deleting a book."""
    user = request.user
    book = get_object_or_404(Book, pk=pk)

    # Check if user has permission to delete books
    if not (user.is_super_admin or user.is_library_admin):
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f"Book '{book_title}' deleted successfully.")
        return redirect('books:manage_books')

    return redirect('books:manage_books')

@login_required
def manage_book_copies(request):
    """View function for managing book copies."""
    user = request.user

    # Check if user has permission to manage book copies
    if not (user.is_super_admin or user.is_library_admin or user.is_staff_member):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get libraries based on user role
    if user.is_super_admin:
        libraries = Library.objects.all()
    elif user.is_library_admin:
        libraries = Library.objects.filter(admin=user)
    else:  # Staff
        libraries = user.staffed_libraries.all()

    if not libraries.exists():
        messages.warning(request, "You are not associated with any library.")
        return redirect('core:dashboard')

    library = libraries.first()
    book_copies = BookCopy.objects.filter(library=library)

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        book_copies = book_copies.filter(
            Q(book__title__icontains=search_query) |
            Q(inventory_number__icontains=search_query)
        ).distinct()

    # Filter by book if provided
    book_id = request.GET.get('book', '')
    if book_id:
        book_copies = book_copies.filter(book_id=book_id)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(book_copies, 10)  # Show 10 copies per page

    try:
        book_copies = paginator.page(page)
    except PageNotAnInteger:
        book_copies = paginator.page(1)
    except EmptyPage:
        book_copies = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = BookCopyForm(request.POST, user=user)
        if form.is_valid():
            book_copy = form.save(commit=False)
            book_copy.library = library
            book_copy.save()
            messages.success(request, f"Book copy '{book_copy.inventory_number}' added successfully.")
            return redirect('books:manage_book_copies')
    else:
        form = BookCopyForm(user=user)

    context = {
        'library': library,
        'book_copies': book_copies,
        'form': form,
    }

    return render(request, 'books/manage_book_copies.html', context)

@login_required
def delete_book_copy(request, pk):
    """View function for deleting a book copy."""
    user = request.user
    book_copy = get_object_or_404(BookCopy, pk=pk)

    # Check if user has permission to delete book copies
    if not (user.is_super_admin or
            (user.is_library_admin and book_copy.library.admin == user) or
            (user.is_staff_member and user in book_copy.library.staff.all())):
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        inventory_number = book_copy.inventory_number
        book_copy.delete()
        messages.success(request, f"Book copy '{inventory_number}' deleted successfully.")
        return redirect('books:manage_book_copies')

    return redirect('books:manage_book_copies')
