from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User
from apps.libraries.models import Library
from apps.books.models import Book, BookCopy, Author, Category
from apps.transactions.models import Transaction, Membership

@login_required
def dashboard(request):
    """View function for the member dashboard."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    # Get user's memberships
    memberships = Membership.objects.filter(user=user, is_active=True)

    # Get user's transactions
    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')[:5]

    # Get borrowed books
    borrowed_books = Transaction.objects.filter(
        user=user,
        transaction_type='BORROW',
        status='COMPLETED',
        return_date__isnull=True
    )

    # Get reserved books
    reserved_books = Transaction.objects.filter(
        user=user,
        transaction_type='RESERVE',
        status='COMPLETED'
    )

    # Get overdue books
    overdue_books = Transaction.objects.filter(
        user=user,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    )

    context = {
        'memberships': memberships,
        'transactions': transactions,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'overdue_books': overdue_books,
    }

    # Add welcome back message
    messages.success(request, f"Welcome back, {user.get_full_name() or user.email}! We're glad to see you again.")

    return render(request, 'member/dashboard.html', context)

def is_member(user):
    """Check if user is a regular member (not a library admin or super admin)."""
    return not (user.is_library_admin or user.is_super_admin)

@login_required
def profile(request):
    """View function for the member profile."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    context = {
        'user': user,
    }

    return render(request, 'member/profile.html', context)

@login_required
def memberships(request):
    """View function for the member's library memberships."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    memberships = Membership.objects.filter(user=user)

    context = {
        'memberships': memberships,
    }

    return render(request, 'member/memberships.html', context)

@login_required
def transactions(request):
    """View function for the member's transactions."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')

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

    return render(request, 'member/transactions.html', context)

@login_required
def borrowed_books(request):
    """View function for the member's borrowed books."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    borrowed_books = Transaction.objects.filter(
        user=user,
        transaction_type='BORROW',
        status='COMPLETED',
        return_date__isnull=True
    ).order_by('due_date')

    context = {
        'borrowed_books': borrowed_books,
    }

    return render(request, 'member/borrowed_books.html', context)

@login_required
def reserved_books(request):
    """View function for the member's reserved books."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    reserved_books = Transaction.objects.filter(
        user=user,
        transaction_type='RESERVE',
        status='COMPLETED'
    ).order_by('transaction_date')

    context = {
        'reserved_books': reserved_books,
    }

    return render(request, 'member/reserved_books.html', context)

@login_required
def fines(request):
    """View function for the member's fines."""
    user = request.user

    # Check if the user is a library admin or super admin
    if user.is_library_admin:
        messages.warning(request, "You are logged in as a Library Admin. Please use the Library Admin dashboard.")
        return redirect('library_admin:dashboard')
    elif user.is_super_admin:
        messages.warning(request, "You are logged in as a Super Admin. Please use the Super Admin dashboard.")
        return redirect('superadmin:dashboard')

    fines = Transaction.objects.filter(
        user=user,
        fine_amount__gt=0
    ).order_by('-transaction_date')

    # Calculate total fines
    total_fines = sum(fine.fine_amount for fine in fines)

    # Calculate unpaid fines
    unpaid_fines = sum(fine.fine_amount for fine in fines if not fine.fine_paid)

    context = {
        'fines': fines,
        'total_fines': total_fines,
        'unpaid_fines': unpaid_fines,
    }

    return render(request, 'member/fines.html', context)
