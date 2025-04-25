from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from accounts.models import User
from libraries.models import Library
from books.models import Book, BookCopy, Author, Category
from transactions.models import Transaction, Membership, MembershipPlan

def is_library_admin(user):
    """Check if user is a library admin."""
    return user.is_library_admin

@login_required
@user_passes_test(is_library_admin)
def dashboard(request):
    """View function for the library admin dashboard."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    
    # Get library statistics
    total_books = BookCopy.objects.filter(library=library).count()
    available_books = BookCopy.objects.filter(library=library, status='AVAILABLE').count()
    borrowed_books = BookCopy.objects.filter(library=library, status='BORROWED').count()
    reserved_books = BookCopy.objects.filter(library=library, status='RESERVED').count()
    
    # Get user statistics
    staff_members = library.staff.count()
    members = Membership.objects.filter(library=library, is_active=True).count()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')[:10]
    
    # Get overdue books
    overdue_books = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    )

    context = {
        'library': library,
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'staff_members': staff_members,
        'members': members,
        'recent_transactions': recent_transactions,
        'overdue_books': overdue_books,
    }

    return render(request, 'library_admin/dashboard.html', context)

@login_required
@user_passes_test(is_library_admin)
def manage_staff(request):
    """View function for managing library staff."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    staff_members = library.staff.all()
    
    context = {
        'library': library,
        'staff_members': staff_members,
    }
    
    return render(request, 'library_admin/staff.html', context)

@login_required
@user_passes_test(is_library_admin)
def manage_books(request):
    """View function for managing library books."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    book_copies = BookCopy.objects.filter(library=library)
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        book_copies = book_copies.filter(
            Q(book__title__icontains=search_query) |
            Q(book__authors__name__icontains=search_query) |
            Q(book__isbn__icontains=search_query) |
            Q(inventory_number__icontains=search_query)
        ).distinct()
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        book_copies = book_copies.filter(status=status)
    
    context = {
        'library': library,
        'book_copies': book_copies,
        'search_query': search_query,
        'status': status,
    }
    
    return render(request, 'library_admin/books.html', context)

@login_required
@user_passes_test(is_library_admin)
def manage_members(request):
    """View function for managing library members."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    memberships = Membership.objects.filter(library=library)
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        memberships = memberships.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(membership_number__icontains=search_query)
        )
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        is_active_bool = is_active.lower() == 'true'
        memberships = memberships.filter(is_active=is_active_bool)
    
    context = {
        'library': library,
        'memberships': memberships,
        'search_query': search_query,
        'is_active': is_active,
    }
    
    return render(request, 'library_admin/members.html', context)

@login_required
@user_passes_test(is_library_admin)
def manage_transactions(request):
    """View function for managing library transactions."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')
    
    # Filter by transaction type if provided
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    # Filter by status if provided
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)
    
    context = {
        'library': library,
        'transactions': transactions,
        'transaction_type': transaction_type,
        'status': status,
    }
    
    return render(request, 'library_admin/transactions.html', context)

@login_required
@user_passes_test(is_library_admin)
def reports(request):
    """View function for generating library reports."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    
    # Get report type from GET parameters
    report_type = request.GET.get('type', 'transactions')
    
    context = {
        'library': library,
        'report_type': report_type,
    }
    
    if report_type == 'transactions':
        # Transaction report
        transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')
        
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
    
    elif report_type == 'members':
        # Member report
        memberships = Membership.objects.filter(library=library)
        
        # Filter by active status
        is_active = request.GET.get('is_active', '')
        if is_active:
            is_active_bool = is_active.lower() == 'true'
            memberships = memberships.filter(is_active=is_active_bool)
            context['is_active'] = is_active
        
        context['memberships'] = memberships
    
    elif report_type == 'books':
        # Book report
        book_copies = BookCopy.objects.filter(library=library)
        
        # Filter by status
        status = request.GET.get('status', '')
        if status:
            book_copies = book_copies.filter(status=status)
            context['status'] = status
        
        context['book_copies'] = book_copies
    
    return render(request, 'library_admin/reports.html', context)
