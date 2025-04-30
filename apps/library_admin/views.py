from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, F, Avg
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from datetime import timedelta, datetime
import json
import random
import csv
import io
import psutil
import platform
import os
from django.conf import settings

from apps.accounts.models import User
from apps.libraries.models import Library
from apps.libraries.forms import LibraryForm
from apps.books.models import Book, BookCopy, Author, Category, Publisher
from apps.books.forms import CategoryForm, AuthorForm, PublisherForm
from apps.transactions.models import Transaction, Membership, MembershipPlan, MembershipRequest, Reservation

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
    maintenance_books = BookCopy.objects.filter(library=library, status='MAINTENANCE').count()

    # Get book copies for reference
    book_copies = BookCopy.objects.filter(library=library)

    # Get user statistics
    staff_members_list = library.staff.all()
    staff_members_count = staff_members_list.count()
    members_count = Membership.objects.filter(library=library, is_active=True).count()

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')[:10]
    transactions_count = recent_transactions.count()

    # Get overdue books
    overdue_books = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    )

    # Get pending membership requests
    pending_requests = MembershipRequest.objects.filter(
        library=library,
        status='PENDING'
    ).order_by('-request_date')

    # Count of pending membership requests
    pending_requests_count = pending_requests.count()

    context = {
        'library': library,
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'maintenance_books': maintenance_books,
        'book_copies': book_copies,
        'staff_members': staff_members_count,
        'staff_members_list': staff_members_list,
        'members': members_count,
        'recent_transactions': recent_transactions,
        'transactions_count': transactions_count,
        'overdue_books': overdue_books,
        'pending_requests': pending_requests[:5],
        'pending_requests_count': pending_requests_count,
    }

    # Add welcome back message
    messages.success(request, f"Welcome back, {user.get_full_name() or user.email}! You are logged in as a Library Admin.")

    return render(request, 'library_admin/dashboard/index.html', context)

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

    return render(request, 'library_admin/users/staff_list.html', context)

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

    return render(request, 'library_admin/books/book_list.html', context)

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

    return render(request, 'library_admin/users/member_list.html', context)

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

    return render(request, 'library_admin/transactions/transaction_list.html', context)

@login_required
@user_passes_test(is_library_admin)
def transaction_reports(request):
    """View function for generating transaction reports in the library admin section."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get date range for filtering
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    # Get custom date range if provided
    if request.GET.get('start_date') and request.GET.get('end_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

    # Get transactions for the library within the date range
    transactions = Transaction.objects.filter(
        library=library,
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    ).order_by('-transaction_date')

    # Calculate statistics
    total_transactions = transactions.count()
    total_borrows = transactions.filter(transaction_type='BORROW').count()
    total_returns = transactions.filter(transaction_type='RETURN').count()
    total_reserves = transactions.filter(transaction_type='RESERVE').count()

    # Calculate total fines
    total_fines = transactions.filter(fine_amount__gt=0).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0

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
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/reports/transaction_reports.html', context)

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
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
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

    return render(request, 'library_admin/transactions/transaction_reports.html', context)


@login_required
@user_passes_test(is_library_admin)
def membership_requests(request):
    """View function for managing membership requests."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all membership requests for this library
    membership_requests = MembershipRequest.objects.filter(library=library).order_by('-request_date')

    # Get counts for different statuses
    pending_requests_count = MembershipRequest.objects.filter(library=library, status='PENDING').count()
    approved_requests_count = MembershipRequest.objects.filter(library=library, status='APPROVED').count()
    rejected_requests_count = MembershipRequest.objects.filter(library=library, status='REJECTED').count()

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        membership_requests = membership_requests.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        membership_requests = membership_requests.filter(status=status)

    # Pagination
    paginator = Paginator(membership_requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'library': library,
        'membership_requests': page_obj,
        'search_query': search_query,
        'status': status,
        'pending_requests_count': pending_requests_count,
        'approved_requests_count': approved_requests_count,
        'rejected_requests_count': rejected_requests_count,
    }

    return render(request, 'library_admin/membership_requests.html', context)


@login_required
@user_passes_test(is_library_admin)
def approve_membership_request(request):
    """View function for approving a membership request."""
    if request.method != 'POST':
        return redirect('library_admin:membership_requests')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the membership request
    request_id = request.POST.get('request_id')
    notes = request.POST.get('notes', '')

    try:
        membership_request = MembershipRequest.objects.get(id=request_id, library=library)
    except MembershipRequest.DoesNotExist:
        messages.error(request, "Membership request not found.")
        return redirect('library_admin:membership_requests')

    # Check if the request is already processed
    if membership_request.status != 'PENDING':
        messages.warning(request, "This membership request has already been processed.")
        return redirect('library_admin:membership_requests')

    # Approve the request
    membership_request.status = 'APPROVED'
    membership_request.processed_by = user
    membership_request.processed_date = timezone.now()
    membership_request.notes = notes
    membership_request.save()

    # Update the user's approval status
    member = membership_request.user
    member.approval_status = 'APPROVED'
    member.approved_by = user
    member.approval_date = timezone.now()
    member.save()

    # Create a membership for the user
    # Get the default membership plan (you might want to let the admin choose a plan)
    default_plan = MembershipPlan.objects.filter(is_active=True).first()

    if default_plan:
        # Calculate start and end dates
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=default_plan.duration_days)

        # Create the membership
        membership = Membership(
            user=member,
            library=library,
            plan=default_plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        membership.save()

        messages.success(
            request,
            f"Membership request for {member.first_name} {member.last_name} has been approved. "
            f"A new membership has been created."
        )
    else:
        messages.warning(
            request,
            f"Membership request for {member.first_name} {member.last_name} has been approved, "
            f"but no active membership plan was found. Please create a membership manually."
        )

    return redirect('library_admin:membership_requests')


@login_required
@user_passes_test(is_library_admin)
def reject_membership_request(request):
    """View function for rejecting a membership request."""
    if request.method != 'POST':
        return redirect('library_admin:membership_requests')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the membership request
    request_id = request.POST.get('request_id')
    notes = request.POST.get('notes', '')

    try:
        membership_request = MembershipRequest.objects.get(id=request_id, library=library)
    except MembershipRequest.DoesNotExist:
        messages.error(request, "Membership request not found.")
        return redirect('library_admin:membership_requests')

    # Check if the request is already processed
    if membership_request.status != 'PENDING':
        messages.warning(request, "This membership request has already been processed.")
        return redirect('library_admin:membership_requests')

    # Reject the request
    membership_request.status = 'REJECTED'
    membership_request.processed_by = user
    membership_request.processed_date = timezone.now()
    membership_request.notes = notes
    membership_request.save()

    # Update the user's approval status
    member = membership_request.user
    member.approval_status = 'REJECTED'
    member.approved_by = user
    member.approval_date = timezone.now()
    member.save()

    messages.success(
        request,
        f"Membership request for {member.first_name} {member.last_name} has been rejected."
    )

    return redirect('library_admin:membership_requests')


# New placeholder views for enhanced sidebar functionality

@login_required
@user_passes_test(is_library_admin)
def statistics(request):
    """View function for library statistics dashboard."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Placeholder statistics data
    context = {
        'library': library,
        'page_title': 'Library Statistics',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/statistics.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_category(request, slug):
    """View function for editing a category."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' has been updated successfully.")
            return redirect('library_admin:categories')
    else:
        form = CategoryForm(instance=category)

    context = {
        'library': library,
        'form': form,
        'category': category,
        'title': 'Edit Category',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/books/category_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def manage_publishers(request):
    """View function for managing publishers."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all publishers with book count
    publishers = Publisher.objects.annotate(
        book_count=Count('books', filter=Q(books__copies__library=library), distinct=True)
    ).order_by('name')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        publishers = publishers.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'library': library,
        'publishers': publishers,
        'search_query': search_query,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/books/publisher_list.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_publisher(request):
    """View function for adding a new publisher."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            messages.success(request, f"Publisher '{publisher.name}' has been added successfully.")
            return redirect('library_admin:publishers')
    else:
        form = PublisherForm()

    context = {
        'library': library,
        'form': form,
        'title': 'Add New Publisher',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/books/publisher_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_publisher(request, slug):
    """View function for editing a publisher."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    publisher = get_object_or_404(Publisher, slug=slug)

    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            messages.success(request, f"Publisher '{publisher.name}' has been updated successfully.")
            return redirect('library_admin:publishers')
    else:
        form = PublisherForm(instance=publisher)

    context = {
        'library': library,
        'form': form,
        'publisher': publisher,
        'title': 'Edit Publisher',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/books/publisher_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def publisher_detail(request, slug):
    """View function for displaying details of a specific publisher."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the publisher
    publisher = get_object_or_404(Publisher, slug=slug)

    # Get books by this publisher that are available in the library
    books = Book.objects.filter(
        publisher=publisher,
        copies__library=library
    ).distinct()

    context = {
        'library': library,
        'publisher': publisher,
        'books': books,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/books/publisher_detail.html', context)


@login_required
@user_passes_test(is_library_admin)
def manage_reservations(request):
    """View function for managing book reservations."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all reservations for this library
    reservations = Reservation.objects.filter(library=library).order_by('-reservation_date')

    # Filter by status
    status = request.GET.get('status', '')
    if status:
        reservations = reservations.filter(status=status)

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        reservations = reservations.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(book__title__icontains=search_query)
        )

    context = {
        'library': library,
        'reservations': reservations,
        'status': status,
        'search_query': search_query,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/circulation/reservations.html', context)


@login_required
@user_passes_test(is_library_admin)
def custom_reports(request):
    """View function for generating custom reports."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    context = {
        'library': library,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/reports/custom_reports.html', context)


@login_required
@user_passes_test(is_library_admin)
def export_reports(request):
    """View function for exporting reports to CSV."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get report type from GET parameters
    report_type = request.GET.get('type', 'transactions')

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    if report_type == 'transactions':
        # Write header row
        writer.writerow(['Transaction ID', 'User', 'Book', 'Type', 'Status', 'Date', 'Due Date', 'Return Date'])

        # Get transactions
        transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')

        # Write data rows
        for transaction in transactions:
            writer.writerow([
                transaction.transaction_id,
                transaction.user.email,
                transaction.book_copy.book.title,
                transaction.transaction_type,
                transaction.status,
                transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                transaction.due_date.strftime('%Y-%m-%d') if transaction.due_date else '',
                transaction.return_date.strftime('%Y-%m-%d %H:%M:%S') if transaction.return_date else ''
            ])

    elif report_type == 'members':
        # Write header row
        writer.writerow(['Member ID', 'Name', 'Email', 'Membership Number', 'Plan', 'Start Date', 'End Date', 'Status'])

        # Get memberships
        memberships = Membership.objects.filter(library=library)

        # Write data rows
        for membership in memberships:
            writer.writerow([
                membership.user.id,
                f"{membership.user.first_name} {membership.user.last_name}",
                membership.user.email,
                membership.membership_number,
                membership.plan.name if membership.plan else '',
                membership.start_date.strftime('%Y-%m-%d') if membership.start_date else '',
                membership.end_date.strftime('%Y-%m-%d') if membership.end_date else '',
                'Active' if membership.is_active else 'Inactive'
            ])

    elif report_type == 'books':
        # Write header row
        writer.writerow(['Book ID', 'Title', 'Author(s)', 'ISBN', 'Publisher', 'Publication Year', 'Copies', 'Available Copies'])

        # Get books
        books = Book.objects.filter(copies__library=library).distinct()

        # Write data rows
        for book in books:
            total_copies = book.copies.filter(library=library).count()
            available_copies = book.copies.filter(library=library, status='AVAILABLE').count()

            writer.writerow([
                book.id,
                book.title,
                ', '.join([author.name for author in book.authors.all()]),
                book.isbn,
                book.publisher.name if book.publisher else '',
                book.publication_year,
                total_copies,
                available_copies
            ])

    return response


@login_required
@user_passes_test(is_library_admin)
def general_settings(request):
    """View function for general library settings."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    context = {
        'library': library,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/settings/general.html', context)


@login_required
@user_passes_test(is_library_admin)
def circulation_settings(request):
    """View function for circulation settings."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    context = {
        'library': library,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/settings/circulation.html', context)


@login_required
@user_passes_test(is_library_admin)
def notification_settings(request):
    """View function for notification settings."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    context = {
        'library': library,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/settings/notifications.html', context)


@login_required
@user_passes_test(is_library_admin)
def appearance_settings(request):
    """View function for appearance settings."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    context = {
        'library': library,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/settings/appearance.html', context)


@login_required
@user_passes_test(is_library_admin)
def system_status(request):
    """View function for system status page."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # System information
    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'django_version': settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'Unknown',
    }

    # Resource usage
    try:
        resource_usage = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    except:
        resource_usage = {
            'cpu_percent': 'N/A',
            'memory_percent': 'N/A',
            'disk_percent': 'N/A',
        }

    # Database statistics
    db_stats = {
        'total_books': Book.objects.count(),
        'total_users': User.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'total_libraries': Library.objects.count(),
    }

    context = {
        'library': library,
        'system_info': system_info,
        'resource_usage': resource_usage,
        'db_stats': db_stats,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/system_status.html', context)


@login_required
@user_passes_test(is_library_admin)
def authors_collection(request):
    """View function for displaying the authors page."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all authors with book count
    authors = Author.objects.annotate(
        book_count=Count('books', filter=Q(books__copies__library=library), distinct=True)
    ).order_by('name')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        authors = authors.filter(
            Q(name__icontains=search_query) |
            Q(biography__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(authors, 12)  # Show 12 authors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'library': library,
        'authors': page_obj,
        'search_query': search_query,
    }

    return render(request, 'library_admin/books/author_list.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_author(request):
    """View function for adding a new author."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"Author '{author.name}' added successfully.")
            return redirect('library_admin:authors')
    else:
        form = AuthorForm()

    context = {
        'library': library,
        'form': form,
        'title': 'Add Author',
    }

    return render(request, 'library_admin/books/author_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_author(request, slug):
    """View function for editing an existing author."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    author = get_object_or_404(Author, slug=slug)

    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"Author '{author.name}' updated successfully.")
            return redirect('library_admin:authors')
    else:
        form = AuthorForm(instance=author)

    context = {
        'library': library,
        'form': form,
        'author': author,
        'title': 'Edit Author',
    }

    return render(request, 'library_admin/books/author_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def author_detail(request, slug):
    """View function for displaying details of a specific author."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the author
    author = get_object_or_404(Author, slug=slug)

    # Get books by this author that are available in the library
    books = Book.objects.filter(
        authors=author,
        copies__library=library
    ).distinct()

    context = {
        'library': library,
        'author': author,
        'books': books,
    }

    return render(request, 'library_admin/books/author_detail.html', context)


@login_required
@user_passes_test(is_library_admin)
def circulation(request):
    """View function for circulation dashboard."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get recent transactions (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_transactions = Transaction.objects.filter(
        library=library,
        transaction_date__gte=thirty_days_ago
    ).order_by('-transaction_date')

    # Get statistics
    total_books = BookCopy.objects.filter(library=library).count()
    available_books = BookCopy.objects.filter(library=library, status='AVAILABLE').count()
    borrowed_books = BookCopy.objects.filter(library=library, status='BORROWED').count()
    reserved_books = BookCopy.objects.filter(library=library, status='RESERVED').count()

    # Get overdue books
    overdue_books = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    ).order_by('due_date')

    # Get active members
    active_members = Membership.objects.filter(
        library=library,
        is_active=True
    ).count()

    # Get daily transaction counts for the last 30 days
    daily_transactions = []
    for i in range(30, 0, -1):
        date = timezone.now().date() - timedelta(days=i)
        count = Transaction.objects.filter(
            library=library,
            transaction_date__date=date
        ).count()
        daily_transactions.append({
            'date': date.strftime('%b %d'),
            'count': count
        })

    # Get most borrowed books
    most_borrowed_books = Book.objects.filter(
        copies__library=library,
        copies__transactions__transaction_type='BORROW'
    ).annotate(
        borrow_count=Count('copies__transactions',
                          filter=Q(copies__transactions__transaction_type='BORROW'))
    ).order_by('-borrow_count')[:5]

    context = {
        'library': library,
        'recent_transactions': recent_transactions[:10],
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'overdue_books': overdue_books[:5],
        'active_members': active_members,
        'daily_transactions': daily_transactions,
        'most_borrowed_books': most_borrowed_books,
    }

    return render(request, 'library_admin/circulation/dashboard.html', context)

@login_required
@user_passes_test(is_library_admin)
def issue_book(request):
    """View function for issuing books to members."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        # Get form data
        member_id = request.POST.get('member')
        book_copy_id = request.POST.get('book_copy')
        due_date_str = request.POST.get('due_date')
        notes = request.POST.get('notes')

        # Validate data
        if not all([member_id, book_copy_id, due_date_str]):
            messages.error(request, "Please fill all required fields.")
            return redirect('library_admin:issue_book')

        try:
            member = User.objects.get(id=member_id)
            book_copy = BookCopy.objects.get(id=book_copy_id, library=library)
            due_date = timezone.datetime.strptime(due_date_str, '%Y-%m-%d').date()

            # Check if book is available
            if book_copy.status != 'AVAILABLE':
                messages.error(request, f"Book copy {book_copy.inventory_number} is not available for borrowing.")
                return redirect('library_admin:issue_book')

            # Check if member has an active membership
            if not Membership.objects.filter(user=member, library=library, is_active=True).exists():
                messages.error(request, f"User {member.email} does not have an active membership with this library.")
                return redirect('library_admin:issue_book')

            # Create transaction
            transaction = Transaction.objects.create(
                book_copy=book_copy,
                library=library,
                user=member,
                transaction_type='BORROW',
                status='COMPLETED',
                due_date=timezone.make_aware(timezone.datetime.combine(due_date, timezone.datetime.min.time())),
                notes=notes,
                processed_by=user
            )

            # Update book copy status
            book_copy.status = 'BORROWED'
            book_copy.save()

            messages.success(request, f"Book '{book_copy.book.title}' has been issued to {member.email} successfully.")
            return redirect('library_admin:circulation')

        except (User.DoesNotExist, BookCopy.DoesNotExist, ValueError) as e:
            messages.error(request, f"Error processing request: {str(e)}")
            return redirect('library_admin:issue_book')

    # Get available book copies
    available_copies = BookCopy.objects.filter(library=library, status='AVAILABLE')

    # Get members with active memberships
    members = User.objects.filter(
        memberships__library=library,
        memberships__is_active=True
    ).distinct()

    context = {
        'library': library,
        'available_copies': available_copies,
        'members': members,
    }

    return render(request, 'library_admin/circulation/issue_book.html', context)

@login_required
@user_passes_test(is_library_admin)
def return_book(request):
    """View function for returning books."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        # Get form data
        transaction_id = request.POST.get('transaction')
        condition = request.POST.get('condition')
        fine_amount = request.POST.get('fine_amount', 0)
        fine_paid = request.POST.get('fine_paid', False) == 'on'
        notes = request.POST.get('notes')

        # Validate data
        if not transaction_id:
            messages.error(request, "Please select a transaction.")
            return redirect('library_admin:return_book')

        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            book_copy = transaction.book_copy

            # Update transaction
            transaction.status = 'COMPLETED'
            transaction.return_date = timezone.now()
            transaction.fine_amount = fine_amount
            transaction.fine_paid = fine_paid
            if fine_paid:
                transaction.fine_payment_date = timezone.now()
            transaction.notes = notes
            transaction.save()

            # Update book copy
            book_copy.condition = condition
            book_copy.status = 'AVAILABLE'
            book_copy.save()

            messages.success(request, f"Book '{book_copy.book.title}' has been returned successfully.")
            return redirect('library_admin:circulation')

        except Transaction.DoesNotExist as e:
            messages.error(request, f"Error processing request: {str(e)}")
            return redirect('library_admin:return_book')

    # Get borrowed books
    borrowed_transactions = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        return_date__isnull=True
    ).select_related('book_copy', 'book_copy__book', 'user')

    context = {
        'library': library,
        'borrowed_transactions': borrowed_transactions,
    }

    return render(request, 'library_admin/circulation/return_book.html', context)

@login_required
@user_passes_test(is_library_admin)
def settings(request):
    """View function for library settings page."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Handle form submission for updating library settings
    if request.method == 'POST':
        # Basic library information update
        library.name = request.POST.get('name', library.name)
        library.address = request.POST.get('address', library.address)
        library.city = request.POST.get('city', library.city)
        library.state = request.POST.get('state', library.state)
        library.postal_code = request.POST.get('postal_code', library.postal_code)
        library.country = request.POST.get('country', library.country)
        library.phone = request.POST.get('phone', library.phone)
        library.email = request.POST.get('email', library.email)
        library.website = request.POST.get('website', library.website)
        library.description = request.POST.get('description', library.description)
        library.opening_hours = request.POST.get('opening_hours', library.opening_hours)

        # Handle image upload if provided
        if 'image' in request.FILES:
            library.image = request.FILES['image']

        library.save()
        messages.success(request, "Library settings updated successfully.")
        return redirect('library_admin:settings')

    context = {
        'library': library,
        'page': 'settings',
    }

    return render(request, 'library_admin/settings/index.html', context)


@login_required
@user_passes_test(is_library_admin)
def notifications(request):
    """View function for notifications center."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get overdue books
    overdue_books = Transaction.objects.filter(
        library=library,
        transaction_type='BORROW',
        status='COMPLETED',
        due_date__lt=timezone.now(),
        return_date__isnull=True
    ).order_by('due_date')

    # Get pending membership requests
    pending_requests = MembershipRequest.objects.filter(
        library=library,
        status='PENDING'
    ).order_by('-request_date')

    # Get books that need maintenance (low stock or poor condition)
    maintenance_books = BookCopy.objects.filter(
        library=library,
        status='MAINTENANCE'
    ).order_by('-updated_at')

    # Get books with low inventory (less than 3 copies available)
    books_with_counts = Book.objects.filter(
        copies__library=library
    ).annotate(
        available_count=Count('copies', filter=Q(copies__status='AVAILABLE', copies__library=library))
    ).filter(available_count__lt=3)

    # Get recent transactions (last 7 days)
    recent_date = timezone.now() - timedelta(days=7)
    recent_transactions = Transaction.objects.filter(
        library=library,
        transaction_date__gte=recent_date
    ).order_by('-transaction_date')

    context = {
        'library': library,
        'overdue_books': overdue_books,
        'pending_requests': pending_requests,
        'maintenance_books': maintenance_books,
        'books_with_counts': books_with_counts,
        'recent_transactions': recent_transactions,
        'page': 'notifications',
    }

    return render(request, 'library_admin/notifications/index.html', context)


@login_required
@user_passes_test(is_library_admin)
def help_documentation(request):
    """View function for help and documentation page."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the specific help topic if provided
    topic = request.GET.get('topic', 'general')

    context = {
        'library': library,
        'topic': topic,
        'page': 'help',
    }

    return render(request, 'library_admin/help/index.html', context)


@login_required
@user_passes_test(is_library_admin)
def analytics(request):
    """View function for analytics and reports dashboard with charts."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get date range for filtering
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days

    date_range = request.GET.get('range', '30')
    if date_range == '7':
        start_date = end_date - timedelta(days=7)
    elif date_range == '90':
        start_date = end_date - timedelta(days=90)
    elif date_range == '365':
        start_date = end_date - timedelta(days=365)

    # Transaction statistics
    transactions = Transaction.objects.filter(
        library=library,
        transaction_date__date__gte=start_date,
        transaction_date__date__lte=end_date
    )

    # Count transactions by type
    borrows = transactions.filter(transaction_type='BORROW').count()
    returns = transactions.filter(transaction_type='RETURN').count()
    reserves = transactions.filter(transaction_type='RESERVE').count()
    cancellations = transactions.filter(transaction_type='CANCEL_RESERVATION').count()

    # Count transactions by status
    completed = transactions.filter(status='COMPLETED').count()
    pending = transactions.filter(status='PENDING').count()
    overdue = transactions.filter(status='OVERDUE').count()
    cancelled = transactions.filter(status='CANCELLED').count()

    # Get popular books (most borrowed)
    popular_books = Book.objects.filter(
        copies__transactions__library=library,
        copies__transactions__transaction_type='BORROW',
        copies__transactions__transaction_date__date__gte=start_date,
        copies__transactions__transaction_date__date__lte=end_date
    ).annotate(
        borrow_count=Count('copies__transactions',
                          filter=Q(copies__transactions__transaction_type='BORROW'))
    ).order_by('-borrow_count')[:10]

    # Get active members (most transactions)
    active_members = User.objects.filter(
        transactions__library=library,
        transactions__transaction_date__date__gte=start_date,
        transactions__transaction_date__date__lte=end_date
    ).annotate(
        transaction_count=Count('transactions')
    ).order_by('-transaction_count')[:10]

    # Get daily transaction data for charts
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        day_transactions = transactions.filter(
            transaction_date__date=current_date
        )

        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'borrows': day_transactions.filter(transaction_type='BORROW').count(),
            'returns': day_transactions.filter(transaction_type='RETURN').count(),
            'reserves': day_transactions.filter(transaction_type='RESERVE').count(),
        })

        current_date += timedelta(days=1)

    # Get category distribution data
    categories = Category.objects.filter(
        books__copies__library=library
    ).annotate(
        book_count=Count('books', distinct=True)
    ).order_by('-book_count')[:8]

    category_data = [
        {
            'name': category.name,
            'count': category.book_count
        } for category in categories
    ]

    context = {
        'library': library,
        'start_date': start_date,
        'end_date': end_date,
        'date_range': date_range,
        'transactions_count': transactions.count(),
        'borrows': borrows,
        'returns': returns,
        'reserves': reserves,
        'cancellations': cancellations,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'cancelled': cancelled,
        'popular_books': popular_books,
        'active_members': active_members,
        'daily_data': json.dumps(daily_data),
        'category_data': json.dumps(category_data),
        'page': 'analytics',
    }

    return render(request, 'library_admin/analytics/index.html', context)


@login_required
@user_passes_test(is_library_admin)
def manage_categories(request):
    """View function for managing book categories."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all categories with book count
    categories = Category.objects.annotate(
        book_count=Count('books', filter=Q(books__copies__library=library), distinct=True)
    ).order_by('name')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(categories, 12)  # Show 12 categories per page

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    context = {
        'library': library,
        'categories': categories,
        'search_query': search_query,
    }

    return render(request, 'library_admin/books/category_list.html', context)


@login_required
@user_passes_test(is_library_admin)
def category_detail(request, slug):
    """View function for displaying details of a specific category."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get the category
    category = get_object_or_404(Category, slug=slug)

    # Get books in this category that are available in the library
    books = Book.objects.filter(
        categories=category,
        copies__library=library
    ).distinct()

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

    context = {
        'library': library,
        'category': category,
        'books': books,
        'search_query': search_query,
    }

    return render(request, 'library_admin/books/category_detail.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_category(request):
    """View function for adding a new category."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' added successfully.")
            return redirect('library_admin:categories')
    else:
        form = CategoryForm()

    context = {
        'library': library,
        'form': form,
        'title': 'Add Category',
    }

    return render(request, 'library_admin/books/category_form.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_library(request):
    """View function for editing library details for the library admin."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        form = LibraryForm(request.POST, request.FILES, instance=library)
        if form.is_valid():
            form.save()
            messages.success(request, f"Library '{library.name}' updated successfully.")
            return redirect('library_admin:library_details')
    else:
        form = LibraryForm(instance=library)

    context = {
        'library': library,
        'form': form,
        'title': f'Edit Library: {library.name}',
        'submit_text': 'Update Library',
    }

    return render(request, 'library_admin/libraries/edit_library.html', context)

@login_required
@user_passes_test(is_library_admin)
def library_details(request):
    """View function for displaying library details for the library admin."""
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
    maintenance_books = BookCopy.objects.filter(library=library, status='MAINTENANCE').count()

    # Get user statistics
    staff_members_count = library.staff.count()
    members_count = Membership.objects.filter(library=library, is_active=True).count()

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')[:5]

    context = {
        'library': library,
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'maintenance_books': maintenance_books,
        'staff_members_count': staff_members_count,
        'members_count': members_count,
        'recent_transactions': recent_transactions,
    }

    return render(request, 'library_admin/libraries/library_details.html', context)