from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from apps.libraries.models import Library
from apps.books.models import Book, BookCopy, Author, Category
from apps.transactions.models import Transaction, Membership, MembershipPlan
from apps.accounts.models import User

def home(request):
    """View function for the home page."""
    # Get some stats for the homepage
    total_libraries = Library.objects.filter(is_active=True).count()
    total_books = Book.objects.count()
    total_book_copies = BookCopy.objects.count()

    # Get the latest books added to the system
    latest_books = Book.objects.order_by('-created_at')[:6]

    # Get featured libraries
    featured_libraries = Library.objects.filter(is_active=True).order_by('?')[:3]

    context = {
        'total_libraries': total_libraries,
        'total_books': total_books,
        'total_book_copies': total_book_copies,
        'latest_books': latest_books,
        'featured_libraries': featured_libraries,
    }

    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    """View function for the user dashboard - redirects to role-specific dashboards."""
    user = request.user

    # Redirect to role-specific dashboards
    if user.is_super_admin:
        return redirect('superadmin:dashboard')
    elif user.is_library_admin:
        return redirect('library_admin:dashboard')
    elif user.is_staff_member:
        # For now, staff members still use the core dashboard
        # This could be updated later with a dedicated staff dashboard
        libraries = user.staffed_libraries.all()

        if libraries.exists():
            library = libraries.first()
            book_copies = BookCopy.objects.filter(library=library)
            transactions = Transaction.objects.filter(library=library, processed_by=user)

            context = {
                'library': library,
                'book_copies': book_copies,
                'transactions': transactions,
            }

            return render(request, 'member/dashboard/staff.html', context)
        else:
            messages.warning(request, "You are not assigned to any library yet.")
            return redirect('core:home')
    else:  # Regular member
        return redirect('member:dashboard')

def about(request):
    """View function for the about page."""
    return render(request, 'core/about.html')

def contact(request):
    """View function for the contact page."""
    return render(request, 'core/contact.html')

def admin_login(request):
    """View function for the custom admin login page."""
    if request.user.is_authenticated:
        if request.user.is_super_admin:
            return redirect('superadmin:dashboard')
        elif request.user.is_library_admin:
            return redirect('library_admin:dashboard')
        else:
            return redirect('core:dashboard')

    return render(request, 'superadmin/auth/login.html')

def admin_logout(request):
    """View function for the custom admin logout page."""
    if not request.user.is_authenticated:
        return redirect('core:admin_login')

    if request.user.is_super_admin:
        return render(request, 'superadmin/auth/logout.html')
    elif request.user.is_library_admin:
        return render(request, 'library_admin/auth/logout.html')
    else:
        return redirect('account_logout')

def user_logout(request):
    """View function for the custom user logout page."""
    if not request.user.is_authenticated:
        return redirect('account_login')

    return render(request, 'member/auth/logout.html')

def user_login(request):
    """View function for the custom user login page."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    return render(request, 'member/auth/login.html')

# Custom Admin Panel Views
def is_super_admin(user):
    """Check if user is a super admin."""
    return user.is_authenticated and user.is_super_admin

def is_library_admin(user):
    """Check if user is a library admin."""
    return user.is_authenticated and user.is_library_admin

@login_required
@user_passes_test(is_super_admin)
def admin_panel(request):
    """View function for the custom super admin panel - redirects to superadmin dashboard."""
    return redirect('superadmin:dashboard')

@login_required
@user_passes_test(is_super_admin)
def admin_libraries(request):
    """View function for managing libraries in the admin panel."""
    libraries = Library.objects.all()

    # Search by name, city, or country if provided
    query = request.GET.get('q', '')
    if query:
        libraries = libraries.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(country__icontains=query)
        ).distinct()

    # Filter by status if provided
    status = request.GET.get('status', '')
    if status == 'active':
        libraries = libraries.filter(is_active=True)
    elif status == 'inactive':
        libraries = libraries.filter(is_active=False)

    # Sort libraries
    sort = request.GET.get('sort', 'name')
    if sort == 'name':
        libraries = libraries.order_by('name')
    elif sort == 'city':
        libraries = libraries.order_by('city', 'name')
    elif sort == 'books':
        libraries = libraries.annotate(book_count=Count('book_copies')).order_by('-book_count')
    elif sort == 'members':
        libraries = libraries.annotate(member_count=Count('memberships')).order_by('-member_count')
    else:
        libraries = libraries.order_by('name')

    # Pagination
    paginator = Paginator(libraries, 10)  # Show 10 libraries per page
    page_number = request.GET.get('page')
    libraries = paginator.get_page(page_number)

    context = {
        'libraries': libraries,
        'query': query,
        'status': status,
        'sort': sort,
    }

    return render(request, 'superadmin/libraries/library_list.html', context)

@login_required
@user_passes_test(is_super_admin)
def admin_users(request):
    """View function for managing users in the admin panel."""
    # Redirect to our custom user list page
    return redirect('accounts:user_list')

@login_required
@user_passes_test(is_super_admin)
def admin_books(request):
    """View function for managing books in the admin panel."""
    books = Book.objects.all().order_by('title')

    # Get all authors and categories for filters
    authors = Author.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')

    # Search by title, author, or ISBN if provided
    query = request.GET.get('q', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()

    # Filter by category if provided
    category_slug = request.GET.get('category', '')
    if category_slug:
        books = books.filter(categories__slug=category_slug)

    # Filter by author if provided
    author_slug = request.GET.get('author', '')
    if author_slug:
        books = books.filter(authors__slug=author_slug)

    # Pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    context = {
        'books': books,
        'authors': authors,
        'categories': categories,
        'query': query,
    }

    return render(request, 'superadmin/books/book_list.html', context)

@login_required
@user_passes_test(is_super_admin)
def admin_transactions(request):
    """View function for managing transactions in the admin panel."""
    transactions = Transaction.objects.all().order_by('-transaction_date')

    # Get all libraries for filter
    libraries = Library.objects.all().order_by('name')

    # Filter by transaction type if provided
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Filter by status if provided
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)

    # Filter by library if provided
    library_id = request.GET.get('library', '')
    if library_id:
        transactions = transactions.filter(library_id=library_id)

    # Filter by date if provided
    date = request.GET.get('date', '')
    if date:
        transactions = transactions.filter(transaction_date__date=date)

    # Search by user or book if provided
    query = request.GET.get('q', '')
    if query:
        transactions = transactions.filter(
            Q(user__email__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(book_copy__book__title__icontains=query) |
            Q(transaction_id__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(transactions, 15)  # Show 15 transactions per page
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)

    context = {
        'transactions': transactions,
        'libraries': libraries,
        'transaction_type': transaction_type,
        'status': status,
    }

    return render(request, 'superadmin/transactions/transaction_list.html', context)

@login_required
@user_passes_test(is_super_admin)
def admin_reports(request):
    """View function for generating reports in the admin panel."""
    # Get date range from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Get all libraries for filter
    libraries = Library.objects.all().order_by('name')

    # Get transactions based on date range
    transactions = Transaction.objects.all()

    if start_date:
        transactions = transactions.filter(transaction_date__gte=start_date)

    if end_date:
        transactions = transactions.filter(transaction_date__lte=end_date)

    # Filter by library if provided
    library_id = request.GET.get('library', '')
    if library_id:
        transactions = transactions.filter(library_id=library_id)

    # Group transactions by type
    borrow_transactions = transactions.filter(transaction_type='BORROW')
    return_transactions = transactions.filter(transaction_type='RETURN')
    reserve_transactions = transactions.filter(transaction_type='RESERVE')
    cancel_transactions = transactions.filter(transaction_type='CANCEL_RESERVATION')

    # Calculate statistics
    total_transactions = transactions.count()
    total_borrows = borrow_transactions.count()
    total_returns = return_transactions.count()
    total_reserves = reserve_transactions.count()
    total_cancellations = cancel_transactions.count()

    # Calculate total fines
    total_fines = sum(t.fine_amount or 0 for t in return_transactions)

    # Get report type
    report_type = request.GET.get('report_type', 'transactions')

    # Prepare data based on report type
    if report_type == 'books':
        # Get books with transaction counts
        books = Book.objects.all()
        for book in books:
            book.available_copies = BookCopy.objects.filter(book=book, status='AVAILABLE').count()
            book.borrowed_copies = BookCopy.objects.filter(book=book, status='BORROWED').count()
            book.reserved_copies = BookCopy.objects.filter(book=book, status='RESERVED').count()
            book.borrow_count = Transaction.objects.filter(
                book_copy__book=book,
                transaction_type='BORROW'
            ).count()

            # Filter by date range if provided
            if start_date:
                book.borrow_count = Transaction.objects.filter(
                    book_copy__book=book,
                    transaction_type='BORROW',
                    transaction_date__gte=start_date
                ).count()

            if end_date:
                book.borrow_count = Transaction.objects.filter(
                    book_copy__book=book,
                    transaction_type='BORROW',
                    transaction_date__lte=end_date
                ).count()
    else:
        books = None

    if report_type == 'users':
        # Get users with transaction counts
        users = User.objects.all()
        for user in users:
            user.total_borrows = Transaction.objects.filter(
                user=user,
                transaction_type='BORROW'
            ).count()

            user.current_borrows = Transaction.objects.filter(
                user=user,
                transaction_type='BORROW',
                status='COMPLETED',
                return_date__isnull=True
            ).count()

            user.overdue_books = Transaction.objects.filter(
                user=user,
                transaction_type='BORROW',
                status='COMPLETED',
                due_date__lt=timezone.now(),
                return_date__isnull=True
            ).count()

            user.total_fines = sum(t.fine_amount or 0 for t in Transaction.objects.filter(
                user=user,
                fine_amount__gt=0
            ))

            user.paid_fines = sum(t.fine_amount or 0 for t in Transaction.objects.filter(
                user=user,
                fine_amount__gt=0,
                fine_paid=True
            ))

            # Filter by date range if provided
            if start_date:
                user.total_borrows = Transaction.objects.filter(
                    user=user,
                    transaction_type='BORROW',
                    transaction_date__gte=start_date
                ).count()

            if end_date:
                user.total_borrows = Transaction.objects.filter(
                    user=user,
                    transaction_type='BORROW',
                    transaction_date__lte=end_date
                ).count()
    else:
        users = None

    if report_type == 'fines':
        # Get transactions with fines
        fines = Transaction.objects.filter(fine_amount__gt=0)

        # Filter by date range if provided
        if start_date:
            fines = fines.filter(transaction_date__gte=start_date)

        if end_date:
            fines = fines.filter(transaction_date__lte=end_date)

        # Calculate days overdue
        for fine in fines:
            if fine.return_date and fine.due_date:
                fine.days_overdue = (fine.return_date.date() - fine.due_date.date()).days
            elif fine.due_date:
                fine.days_overdue = (timezone.now().date() - fine.due_date.date()).days
            else:
                fine.days_overdue = 0
    else:
        fines = None

    # Generate daily transaction data for chart
    daily_data = []
    if start_date and end_date:
        current_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

        while current_date <= end:
            count = transactions.filter(transaction_date__date=current_date).count()
            daily_data.append({
                'date': current_date,
                'count': count
            })
            current_date += timezone.timedelta(days=1)

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'libraries': libraries,
        'total_transactions': total_transactions,
        'total_borrows': total_borrows,
        'total_returns': total_returns,
        'total_reserves': total_reserves,
        'total_cancellations': total_cancellations,
        'total_fines': total_fines,
        'transactions': transactions,
        'books': books,
        'users': users,
        'fines': fines,
        'daily_data': daily_data,
    }

    return render(request, 'superadmin/transactions/transaction_reports.html', context)

@login_required
@user_passes_test(is_library_admin)
def library_admin_panel(request):
    """View function for the custom library admin panel - redirects to library_admin dashboard."""
    return redirect('library_admin:dashboard')
