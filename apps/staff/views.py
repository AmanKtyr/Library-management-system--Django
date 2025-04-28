from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.libraries.models import Library
from apps.books.models import Book, BookCopy
from apps.transactions.models import Transaction, Membership

def is_staff_member(user):
    """Check if user is a staff member."""
    return user.is_authenticated and user.is_staff_member

@login_required
@user_passes_test(is_staff_member)
def dashboard(request):
    """View function for the staff dashboard."""
    user = request.user

    # Get libraries where the user is a staff member
    libraries = Library.objects.filter(staff=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get statistics for the staff dashboard
    total_books = BookCopy.objects.filter(library=library).count()
    total_members = Membership.objects.filter(library=library, is_active=True).count()

    # Get recent transactions processed by this staff member
    recent_transactions = Transaction.objects.filter(
        library=library,
        processed_by=user
    ).order_by('-transaction_date')[:10]

    # Get books due for return today
    today = timezone.now().date()
    due_today = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date=today,
        return_date__isnull=True
    )

    context = {
        'library': library,
        'total_books': total_books,
        'total_members': total_members,
        'recent_transactions': recent_transactions,
        'due_today': due_today,
    }

    return render(request, 'staff/dashboard/index.html', context)

@login_required
@user_passes_test(is_staff_member)
def manage_books(request):
    """View function for managing books as a staff member."""
    user = request.user

    # Get libraries where the user is a staff member
    libraries = Library.objects.filter(staff=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get book copies in this library
    book_copies = BookCopy.objects.filter(library=library)

    context = {
        'library': library,
        'book_copies': book_copies,
    }

    return render(request, 'staff/books/book_list.html', context)

@login_required
@user_passes_test(is_staff_member)
def manage_transactions(request):
    """View function for managing transactions as a staff member."""
    user = request.user

    # Get libraries where the user is a staff member
    libraries = Library.objects.filter(staff=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get transactions in this library
    transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')

    context = {
        'library': library,
        'transactions': transactions,
    }

    return render(request, 'staff/transactions/transaction_list.html', context)

@login_required
@user_passes_test(is_staff_member)
def issue_book(request):
    """View function for issuing a book to a member."""
    # Implementation will be added later
    return render(request, 'staff/transactions/issue_book.html')

@login_required
@user_passes_test(is_staff_member)
def return_book(request):
    """View function for processing a book return."""
    # Implementation will be added later
    return render(request, 'staff/transactions/return_book.html')

@login_required
@user_passes_test(is_staff_member)
def manage_members(request):
    """View function for managing library members."""
    user = request.user

    # Get libraries where the user is a staff member
    libraries = Library.objects.filter(staff=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get memberships for this library
    memberships = Membership.objects.filter(library=library, is_active=True)

    context = {
        'library': library,
        'memberships': memberships,
    }

    return render(request, 'staff/transactions/member_list.html', context)
