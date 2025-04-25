from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator

from accounts.models import User
from libraries.models import Library
from books.models import Book, BookCopy, Author, Category
from transactions.models import Transaction, Membership, MembershipPlan

def is_super_admin(user):
    """Check if user is a super admin."""
    return user.is_super_admin

@login_required
@user_passes_test(is_super_admin)
def dashboard(request):
    """View function for the super admin dashboard."""
    # Get statistics for the admin panel
    total_libraries = Library.objects.count()
    active_libraries = Library.objects.filter(is_active=True).count()
    total_books = Book.objects.count()
    total_book_copies = BookCopy.objects.count()
    total_users = User.objects.count()
    total_transactions = Transaction.objects.count()

    # Get user statistics
    super_admins = User.objects.filter(user_type='SUPER_ADMIN').count()
    library_admins = User.objects.filter(user_type='LIBRARY_ADMIN').count()
    staff_members = User.objects.filter(user_type='STAFF').count()
    members = User.objects.filter(user_type='MEMBER').count()

    # Get transaction statistics
    borrows = Transaction.objects.filter(transaction_type='BORROW').count()
    returns = Transaction.objects.filter(transaction_type='RETURN').count()
    reserves = Transaction.objects.filter(transaction_type='RESERVE').count()
    overdue = Transaction.objects.filter(
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    ).count()

    # Get financial statistics
    total_fines = Transaction.objects.aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0
    paid_fines = Transaction.objects.filter(fine_paid=True).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0

    # Get recent data
    recent_libraries = Library.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_transactions = Transaction.objects.order_by('-transaction_date')[:5]

    # Get top libraries and books
    top_libraries = Library.objects.annotate(book_count=Count('book_copies')).order_by('-book_count')[:5]
    top_books = Book.objects.annotate(borrow_count=Count('copies__transactions', 
                                                        filter=Q(copies__transactions__transaction_type='BORROW'))
                                    ).order_by('-borrow_count')[:5]

    context = {
        'total_libraries': total_libraries,
        'active_libraries': active_libraries,
        'total_books': total_books,
        'total_book_copies': total_book_copies,
        'total_users': total_users,
        'total_transactions': total_transactions,
        'super_admins': super_admins,
        'library_admins': library_admins,
        'staff_members': staff_members,
        'members': members,
        'borrows': borrows,
        'returns': returns,
        'reserves': reserves,
        'overdue': overdue,
        'total_fines': total_fines,
        'paid_fines': paid_fines,
        'recent_libraries': recent_libraries,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions,
        'top_libraries': top_libraries,
        'top_books': top_books,
    }

    return render(request, 'superadmin/dashboard.html', context)

@login_required
@user_passes_test(is_super_admin)
def manage_libraries(request):
    """View function for managing libraries."""
    libraries = Library.objects.all()
    
    context = {
        'libraries': libraries,
    }
    
    return render(request, 'superadmin/libraries.html', context)

@login_required
@user_passes_test(is_super_admin)
def manage_users(request):
    """View function for managing users."""
    users = User.objects.all()
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Filter by user type
    user_type = request.GET.get('user_type', '')
    if user_type:
        users = users.filter(user_type=user_type)
    
    context = {
        'users': users,
        'search_query': search_query,
        'user_type': user_type,
    }
    
    return render(request, 'superadmin/users.html', context)

@login_required
@user_passes_test(is_super_admin)
def manage_books(request):
    """View function for managing books."""
    books = Book.objects.all()
    
    context = {
        'books': books,
    }
    
    return render(request, 'superadmin/books.html', context)

@login_required
@user_passes_test(is_super_admin)
def manage_transactions(request):
    """View function for managing transactions."""
    transactions = Transaction.objects.all().order_by('-transaction_date')
    
    # Filter by transaction type if provided
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Filter by status if provided
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)
    
    context = {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'status': status,
    }
    
    return render(request, 'superadmin/transactions.html', context)

@login_required
@user_passes_test(is_super_admin)
def reports(request):
    """View function for generating reports."""
    # Get report type from GET parameters
    report_type = request.GET.get('type', 'transactions')
    
    context = {
        'report_type': report_type,
    }
    
    if report_type == 'transactions':
        # Transaction report
        transactions = Transaction.objects.all().order_by('-transaction_date')
        
        # Filter by date range if provided
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        if start_date and end_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59)
                
                transactions = transactions.filter(
                    transaction_date__gte=start_date,
                    transaction_date__lte=end_date
                )
                
                context['start_date'] = start_date.strftime('%Y-%m-%d')
                context['end_date'] = end_date.strftime('%Y-%m-%d')
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        
        context['transactions'] = transactions
    
    elif report_type == 'users':
        # User report
        users = User.objects.all().order_by('-date_joined')
        
        # Filter by user type if provided
        user_type = request.GET.get('user_type', '')
        if user_type:
            users = users.filter(user_type=user_type)
            context['user_type'] = user_type
        
        context['users'] = users
    
    elif report_type == 'books':
        # Book report
        books = Book.objects.all()
        
        # Filter by category if provided
        category_id = request.GET.get('category', '')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                books = books.filter(categories=category)
                context['category'] = category
            except (Category.DoesNotExist, ValueError):
                pass
        
        context['books'] = books
        context['categories'] = Category.objects.all()
    
    return render(request, 'superadmin/reports.html', context)
