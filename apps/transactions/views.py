from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from .models import Transaction, Membership, MembershipPlan
from apps.books.models import BookCopy
from apps.libraries.models import Library
from .forms import TransactionForm, MembershipForm  # We'll create these forms later

@login_required
def transaction_list(request):
    """View function for listing transactions."""
    user = request.user

    # Different views based on user role
    if user.is_super_admin:
        # Super admin sees all transactions
        transactions = Transaction.objects.all().order_by('-transaction_date')
    elif user.is_library_admin:
        # Library admin sees transactions for their library
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
            transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')
        else:
            transactions = Transaction.objects.none()
    elif user.is_staff_member:
        # Staff member sees transactions they processed
        transactions = Transaction.objects.filter(processed_by=user).order_by('-transaction_date')
    else:
        # Regular member sees their own transactions
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

    return render(request, 'transactions/transaction_list.html', context)

@login_required
def transaction_detail(request, transaction_id):
    """View function for displaying details of a specific transaction."""
    user = request.user
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)

    # Check if user has permission to view this transaction
    if not (user.is_super_admin or
            (user.is_library_admin and transaction.library.admin == user) or
            (user.is_staff_member and user in transaction.library.staff.all()) or
            transaction.user == user):
        return HttpResponseForbidden("You don't have permission to access this page.")

    context = {
        'transaction': transaction,
    }

    return render(request, 'transactions/transaction_detail.html', context)

@login_required
def borrow_book(request):
    """View function for borrowing a book."""
    user = request.user

    # Check if user is a member
    if not user.is_library_member:
        messages.error(request, "Only library members can borrow books.")
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = TransactionForm(request.POST, transaction_type='BORROW', user=user)
        if form.is_valid():
            book_copy = form.cleaned_data['book_copy']
            library = book_copy.library

            # Check if user has an active membership for this library
            membership = Membership.objects.filter(user=user, library=library, is_active=True).first()
            if not membership:
                messages.error(request, f"You don't have an active membership for {library.name}.")
                return redirect('transactions:borrow_book')

            # Check if book copy is available
            if book_copy.status != 'AVAILABLE':
                messages.error(request, "This book is not available for borrowing.")
                return redirect('transactions:borrow_book')

            # Create transaction
            transaction = Transaction(
                book_copy=book_copy,
                library=library,
                user=user,
                transaction_type='BORROW',
                status='COMPLETED',
                due_date=timezone.now() + timezone.timedelta(days=membership.plan.max_borrowing_days),
                processed_by=form.cleaned_data.get('processed_by')
            )
            transaction.save()

            # Update book copy status
            book_copy.status = 'BORROWED'
            book_copy.save()

            messages.success(request, f"You have successfully borrowed '{book_copy.book.title}'.")
            return redirect('transactions:transaction_detail', transaction_id=transaction.transaction_id)
    else:
        form = TransactionForm(transaction_type='BORROW', user=user)

    context = {
        'form': form,
        'title': 'Borrow Book',
    }

    return render(request, 'transactions/transaction_form.html', context)

@login_required
def return_book(request):
    """View function for returning a book."""
    user = request.user

    # Get all borrowed books for this user
    borrowed_transactions = Transaction.objects.filter(
        user=user,
        transaction_type='BORROW',
        status='COMPLETED',
        return_date__isnull=True
    )

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=user)
            book_copy = transaction.book_copy

            # Create return transaction
            return_transaction = Transaction(
                book_copy=book_copy,
                library=transaction.library,
                user=user,
                transaction_type='RETURN',
                status='COMPLETED',
                processed_by=request.POST.get('processed_by')
            )

            # Check if book is overdue and calculate fine
            if transaction.is_overdue():
                fine_amount = transaction.calculate_fine()
                return_transaction.fine_amount = fine_amount

            return_transaction.save()

            # Update original transaction
            transaction.return_date = timezone.now()
            transaction.save()

            # Update book copy status
            book_copy.status = 'AVAILABLE'
            book_copy.save()

            messages.success(request, f"You have successfully returned '{book_copy.book.title}'.")

            # If there's a fine, redirect to fine payment page
            if return_transaction.fine_amount > 0:
                messages.warning(request, f"You have a fine of ${return_transaction.fine_amount} for returning this book late.")

            return redirect('transactions:transaction_detail', transaction_id=return_transaction.transaction_id)

    context = {
        'borrowed_transactions': borrowed_transactions,
    }

    return render(request, 'transactions/return_book.html', context)

@login_required
def reserve_book(request):
    """View function for reserving a book."""
    user = request.user

    # Check if user is a member
    if not user.is_library_member:
        messages.error(request, "Only library members can reserve books.")
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = TransactionForm(request.POST, transaction_type='RESERVE', user=user)
        if form.is_valid():
            book_copy = form.cleaned_data['book_copy']
            library = book_copy.library

            # Check if user has an active membership for this library
            membership = Membership.objects.filter(user=user, library=library, is_active=True).first()
            if not membership:
                messages.error(request, f"You don't have an active membership for {library.name}.")
                return redirect('transactions:reserve_book')

            # Check if book copy is available for reservation
            if book_copy.status not in ['AVAILABLE', 'BORROWED']:
                messages.error(request, "This book is not available for reservation.")
                return redirect('transactions:reserve_book')

            # Create transaction
            transaction = Transaction(
                book_copy=book_copy,
                library=library,
                user=user,
                transaction_type='RESERVE',
                status='COMPLETED',
                processed_by=form.cleaned_data.get('processed_by')
            )
            transaction.save()

            # Update book copy status if it's available
            if book_copy.status == 'AVAILABLE':
                book_copy.status = 'RESERVED'
                book_copy.save()

            messages.success(request, f"You have successfully reserved '{book_copy.book.title}'.")
            return redirect('transactions:transaction_detail', transaction_id=transaction.transaction_id)
    else:
        form = TransactionForm(transaction_type='RESERVE', user=user)

    context = {
        'form': form,
        'title': 'Reserve Book',
    }

    return render(request, 'transactions/transaction_form.html', context)

@login_required
def membership_list(request):
    """View function for listing memberships."""
    user = request.user

    # Different views based on user role
    if user.is_super_admin:
        # Super admin sees all memberships
        memberships = Membership.objects.all().order_by('-created_at')
    elif user.is_library_admin:
        # Library admin sees memberships for their library
        libraries = Library.objects.filter(admin=user)
        if libraries.exists():
            library = libraries.first()
            memberships = Membership.objects.filter(library=library).order_by('-created_at')
        else:
            memberships = Membership.objects.none()
    elif user.is_staff_member:
        # Staff member sees memberships for their library
        libraries = user.staffed_libraries.all()
        if libraries.exists():
            library = libraries.first()
            memberships = Membership.objects.filter(library=library).order_by('-created_at')
        else:
            memberships = Membership.objects.none()
    else:
        # Regular member sees their own memberships
        memberships = Membership.objects.filter(user=user).order_by('-created_at')

    context = {
        'memberships': memberships,
    }

    return render(request, 'transactions/membership_list.html', context)

@login_required
def membership_detail(request, membership_number):
    """View function for displaying details of a specific membership."""
    user = request.user
    membership = get_object_or_404(Membership, membership_number=membership_number)

    # Check if user has permission to view this membership
    if not (user.is_super_admin or
            (user.is_library_admin and membership.library.admin == user) or
            (user.is_staff_member and user in membership.library.staff.all()) or
            membership.user == user):
        return HttpResponseForbidden("You don't have permission to access this page.")

    context = {
        'membership': membership,
    }

    return render(request, 'transactions/membership_detail.html', context)

@login_required
def new_membership(request):
    """View function for creating a new membership."""
    user = request.user

    if request.method == 'POST':
        form = MembershipForm(request.POST, user=user)
        if form.is_valid():
            membership = form.save(commit=False)

            # Set start and end dates based on plan duration
            membership.start_date = timezone.now().date()
            membership.end_date = membership.start_date + timezone.timedelta(days=membership.plan.duration_days)

            membership.save()
            messages.success(request, f"Your membership for {membership.library.name} has been created successfully.")
            return redirect('transactions:membership_detail', membership_number=membership.membership_number)
    else:
        form = MembershipForm(user=user)

    context = {
        'form': form,
        'title': 'New Membership',
    }

    return render(request, 'transactions/membership_form.html', context)

@login_required
def transaction_reports(request):
    """View function for generating transaction reports."""
    user = request.user

    # Check if user has permission to view reports
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

    # Get date range from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Get transactions for the selected library
    transactions = Transaction.objects.filter(library=library)

    # Apply date filters if provided
    if start_date:
        transactions = transactions.filter(transaction_date__gte=start_date)

    if end_date:
        transactions = transactions.filter(transaction_date__lte=end_date)

    # Group transactions by type
    borrow_transactions = transactions.filter(transaction_type='BORROW')
    return_transactions = transactions.filter(transaction_type='RETURN')
    reserve_transactions = transactions.filter(transaction_type='RESERVE')

    # Calculate statistics
    total_transactions = transactions.count()
    total_borrows = borrow_transactions.count()
    total_returns = return_transactions.count()
    total_reserves = reserve_transactions.count()

    # Calculate total fines
    total_fines = sum(t.fine_amount for t in return_transactions)

    context = {
        'library': library,
        'start_date': start_date,
        'end_date': end_date,
        'total_transactions': total_transactions,
        'total_borrows': total_borrows,
        'total_returns': total_returns,
        'total_reserves': total_reserves,
        'total_fines': total_fines,
        'transactions': transactions,
    }

    return render(request, 'transactions/transaction_reports.html', context)
