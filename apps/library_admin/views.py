from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from datetime import timedelta, datetime
import json
import csv
import random
import platform
import psutil
from django.conf import settings

from apps.accounts.models import User
from apps.libraries.models import Library
from apps.libraries.forms import LibraryForm
from apps.books.models import Book, BookCopy, Author, Category, Publisher
from apps.books.forms import CategoryForm, AuthorForm, PublisherForm
from apps.transactions.models import (
    Transaction, Membership, MembershipPlan, MembershipRequest, Reservation,
    MemberAttendance, LibraryPlan
)

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

    if request.method == 'POST':
        action = request.POST.get('action', 'add')

        if action == 'add':
            # Process the add staff form
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number', '')
            password = request.POST.get('password')

            # Check if user with this email already exists
            if User.objects.filter(email=email).exists():
                existing_user = User.objects.get(email=email)
                if existing_user.user_type == 'STAFF':
                    # Add existing staff to this library
                    library.staff.add(existing_user)
                    messages.success(request, f"Existing staff member {existing_user.get_full_name()} has been added to your library.")
                else:
                    messages.error(request, f"A user with email {email} already exists but is not a staff member.")
            else:
                # Create a new staff user
                new_staff = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    user_type='STAFF',
                    approval_status='APPROVED',
                    approved_by=user,
                    approval_date=timezone.now()
                )
                # Add the new staff to this library
                library.staff.add(new_staff)
                messages.success(request, f"New staff member {new_staff.get_full_name()} has been created and added to your library.")

            return redirect('library_admin:staff')

        elif action == 'edit':
            # Process the edit staff form
            staff_id = request.POST.get('staff_id')
            try:
                staff_member = User.objects.get(id=staff_id, user_type='STAFF')

                # Update staff details
                staff_member.first_name = request.POST.get('first_name')
                staff_member.last_name = request.POST.get('last_name')
                staff_member.phone_number = request.POST.get('phone_number', '')
                staff_member.is_active = request.POST.get('status') == 'active'

                # Update password if provided
                new_password = request.POST.get('password')
                if new_password:
                    staff_member.set_password(new_password)

                staff_member.save()
                messages.success(request, f"Staff member {staff_member.get_full_name()} has been updated successfully.")
            except User.DoesNotExist:
                messages.error(request, "Staff member not found.")

            return redirect('library_admin:staff')

        elif action == 'remove':
            # Process the remove staff form
            staff_id = request.POST.get('staff_id')
            try:
                staff_member = User.objects.get(id=staff_id, user_type='STAFF')
                library.staff.remove(staff_member)
                messages.success(request, f"Staff member {staff_member.get_full_name()} has been removed from your library.")
            except User.DoesNotExist:
                messages.error(request, "Staff member not found.")

            return redirect('library_admin:staff')

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

    # Handle POST requests for adding/editing/removing members
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_new':
            # Process the add new member form
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number', '')
            address = request.POST.get('address', '')
            notes = request.POST.get('notes', '')
            membership_plan_id = request.POST.get('membership_plan')
            start_date_str = request.POST.get('start_date')
            send_welcome_email = request.POST.get('send_welcome_email') == 'on'

            # Validate required fields
            if not all([email, first_name, last_name, membership_plan_id, start_date_str]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('library_admin:members')

            try:
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    existing_user = User.objects.get(email=email)
                    # Check if user is already a member of this library
                    if Membership.objects.filter(user=existing_user, library=library).exists():
                        messages.error(request, f"User with email {email} is already a member of this library.")
                        return redirect('library_admin:members')

                    member = existing_user
                else:
                    # Create a new user with a random password
                    import random
                    import string
                    random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

                    # Create user with only the fields that exist in the User model
                    member = User.objects.create_user(
                        email=email,
                        password=random_password,
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        address=address,
                        user_type='MEMBER',
                        approval_status='APPROVED',
                        approved_by=user,
                        approval_date=timezone.now()
                    )

                # Get the membership plan
                try:
                    # Debug message to see what plan ID we're looking for
                    messages.info(request, f"Looking for membership plan with ID: {membership_plan_id}")

                    # Get all available plans for debugging
                    all_plans = MembershipPlan.objects.all()
                    plan_info = ", ".join([f"ID: {p.id}, Name: {p.name}" for p in all_plans])
                    messages.info(request, f"Available plans: {plan_info}")

                    membership_plan = MembershipPlan.objects.get(id=membership_plan_id)
                except MembershipPlan.DoesNotExist:
                    messages.error(request, "Selected membership plan does not exist.")
                    return redirect('library_admin:members')

                # Parse start date
                try:
                    start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    # Calculate end date based on plan duration
                    end_date = start_date + timezone.timedelta(days=membership_plan.duration_days)
                except ValueError:
                    messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                    return redirect('library_admin:members')

                # Create the membership - let the model's save method generate the membership number
                membership = Membership(
                    user=member,
                    library=library,
                    plan=membership_plan,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                membership.save()

                messages.success(request, f"New member {member.get_full_name()} has been added successfully.")

                # TODO: Send welcome email if requested
                if send_welcome_email:
                    # Implement email sending logic here
                    pass

            except Exception as e:
                messages.error(request, f"Error adding member: {str(e)}")

            return redirect('library_admin:members')

        elif action == 'add_existing':
            # Process the add existing user form
            existing_user_id = request.POST.get('existing_user')
            membership_plan_id = request.POST.get('membership_plan')
            start_date_str = request.POST.get('start_date')
            notes = request.POST.get('notes', '')
            send_welcome_email = request.POST.get('send_welcome_email') == 'on'

            # Validate required fields
            if not all([existing_user_id, membership_plan_id, start_date_str]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('library_admin:members')

            try:
                # Get the user
                existing_user = User.objects.get(id=existing_user_id)

                # Check if user is already a member of this library
                if Membership.objects.filter(user=existing_user, library=library).exists():
                    messages.error(request, f"User {existing_user.email} is already a member of this library.")
                    return redirect('library_admin:members')

                # Get the membership plan
                membership_plan = MembershipPlan.objects.get(id=membership_plan_id)

                # Parse start date
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                # Calculate end date based on plan duration
                end_date = start_date + timezone.timedelta(days=membership_plan.duration_days)

                # Create the membership - let the model's save method generate the membership number
                membership = Membership(
                    user=existing_user,
                    library=library,
                    plan=membership_plan,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True
                )
                membership.save()

                messages.success(request, f"User {existing_user.get_full_name()} has been added as a member successfully.")

                # TODO: Send welcome email if requested
                if send_welcome_email:
                    # Implement email sending logic here
                    pass

            except User.DoesNotExist:
                messages.error(request, "Selected user does not exist.")
            except MembershipPlan.DoesNotExist:
                messages.error(request, "Selected membership plan does not exist.")
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            except Exception as e:
                messages.error(request, f"Error adding member: {str(e)}")

            return redirect('library_admin:members')

        elif action == 'edit':
            # Process the edit member form
            membership_id = request.POST.get('membership_id')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number', '')
            status = request.POST.get('status') == 'active'
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')

            try:
                membership = Membership.objects.get(id=membership_id, library=library)
                member = membership.user

                # Update user details
                member.first_name = first_name
                member.last_name = last_name
                member.phone_number = phone_number
                member.save()

                # Update membership details
                membership.is_active = status

                # Parse dates
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

                membership.start_date = start_date
                membership.end_date = end_date
                membership.save()

                messages.success(request, f"Member {member.get_full_name()} has been updated successfully.")

            except Membership.DoesNotExist:
                messages.error(request, "Membership not found.")
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            except Exception as e:
                messages.error(request, f"Error updating member: {str(e)}")

            return redirect('library_admin:members')

        elif action == 'remove':
            # Process the remove member form
            membership_id = request.POST.get('membership_id')

            try:
                membership = Membership.objects.get(id=membership_id, library=library)
                member_name = membership.user.get_full_name()

                # Delete the membership
                membership.delete()

                messages.success(request, f"Member {member_name} has been removed successfully.")

            except Membership.DoesNotExist:
                messages.error(request, "Membership not found.")
            except Exception as e:
                messages.error(request, f"Error removing member: {str(e)}")

            return redirect('library_admin:members')

    # Get all memberships for this library
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

    # Get membership plans for the form
    membership_plans = MembershipPlan.objects.filter(is_active=True)

    # Get today's date for the form
    today = timezone.now().date()

    # Get pending membership requests count
    pending_requests_count = MembershipRequest.objects.filter(library=library, status='PENDING').count()

    context = {
        'library': library,
        'memberships': memberships,
        'search_query': search_query,
        'is_active': is_active,
        'membership_plans': membership_plans,
        'today': today,
        'pending_requests_count': pending_requests_count,
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
def confirm_reservation(request, reservation_id):
    """View function for confirming a book reservation."""
    if request.method != 'POST':
        return redirect('library_admin:reservations')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        # Get the reservation
        reservation = Reservation.objects.get(id=reservation_id, library=library)

        # Check if the reservation is already processed
        if reservation.status != 'PENDING':
            messages.warning(request, "This reservation has already been processed.")
            return redirect('library_admin:reservations')

        # Confirm the reservation
        reservation.status = 'CONFIRMED'
        reservation.processed_by = user
        reservation.processed_date = timezone.now()
        reservation.save()

        messages.success(request, f"Reservation for '{reservation.book.title}' has been confirmed.")

    except Reservation.DoesNotExist:
        messages.error(request, "Reservation not found.")

    return redirect('library_admin:reservations')


@login_required
@user_passes_test(is_library_admin)
def cancel_reservation(request, reservation_id):
    """View function for canceling a book reservation."""
    if request.method != 'POST':
        return redirect('library_admin:reservations')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        # Get the reservation
        reservation = Reservation.objects.get(id=reservation_id, library=library)

        # Check if the reservation can be canceled
        if reservation.status not in ['PENDING', 'CONFIRMED']:
            messages.warning(request, "This reservation cannot be canceled.")
            return redirect('library_admin:reservations')

        # Cancel the reservation
        reservation.status = 'CANCELLED'
        reservation.processed_by = user
        reservation.processed_date = timezone.now()
        reservation.save()

        messages.success(request, f"Reservation for '{reservation.book.title}' has been canceled.")

    except Reservation.DoesNotExist:
        messages.error(request, "Reservation not found.")

    return redirect('library_admin:reservations')


@login_required
@user_passes_test(is_library_admin)
def confirm_reservation(request, reservation_id):
    """View function for confirming a book reservation."""
    if request.method != 'POST':
        return redirect('library_admin:reservations')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        # Get the reservation
        reservation = Reservation.objects.get(id=reservation_id, library=library)

        # Check if the reservation is already processed
        if reservation.status != 'PENDING':
            messages.warning(request, "This reservation has already been processed.")
            return redirect('library_admin:reservations')

        # Confirm the reservation
        reservation.status = 'CONFIRMED'
        reservation.processed_by = user
        reservation.processed_date = timezone.now()
        reservation.save()

        messages.success(request, f"Reservation for '{reservation.book.title}' has been confirmed.")

    except Reservation.DoesNotExist:
        messages.error(request, "Reservation not found.")

    return redirect('library_admin:reservations')


@login_required
@user_passes_test(is_library_admin)
def cancel_reservation(request, reservation_id):
    """View function for canceling a book reservation."""
    if request.method != 'POST':
        return redirect('library_admin:reservations')

    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        # Get the reservation
        reservation = Reservation.objects.get(id=reservation_id, library=library)

        # Check if the reservation can be canceled
        if reservation.status not in ['PENDING', 'CONFIRMED']:
            messages.warning(request, "This reservation cannot be canceled.")
            return redirect('library_admin:reservations')

        # Cancel the reservation
        reservation.status = 'CANCELLED'
        reservation.processed_by = user
        reservation.processed_date = timezone.now()
        reservation.save()

        messages.success(request, f"Reservation for '{reservation.book.title}' has been canceled.")

    except Reservation.DoesNotExist:
        messages.error(request, "Reservation not found.")

    return redirect('library_admin:reservations')


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


# Membership Management Views
@login_required
@user_passes_test(is_library_admin)
def membership_dashboard(request):
    """View function for the membership management dashboard."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()
    today = timezone.now().date()

    # Get membership stats
    total_members = Membership.objects.filter(library=library).count()
    active_members = Membership.objects.filter(library=library, is_active=True, end_date__gte=today).count()

    # Get expiring memberships (within next 7 days)
    expiry_threshold = today + timezone.timedelta(days=7)
    expiring_soon = Membership.objects.filter(
        library=library,
        is_active=True,
        end_date__gte=today,
        end_date__lte=expiry_threshold
    ).count()

    # Get expiring memberships with details
    expiring_memberships = Membership.objects.filter(
        library=library,
        is_active=True,
        end_date__gte=today,
        end_date__lte=expiry_threshold
    ).order_by('end_date')[:5]

    # Calculate days left for each membership
    for membership in expiring_memberships:
        membership.days_left = (membership.end_date - today).days

    # Calculate total revenue (last 30 days)
    # In a real implementation, this would come from a payment/transaction model
    # For now, we'll just use a placeholder value
    total_revenue = 25000

    # Get reading hall attendance stats
    today_attendance = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date=today
    ).count()

    current_attendance = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date=today,
        check_out_time__isnull=True
    ).count()

    # Get current visitors
    current_visitors = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date=today,
        check_out_time__isnull=True
    ).order_by('check_in_time')

    # Calculate current duration for each visitor
    now = timezone.now()
    for visitor in current_visitors:
        duration = now - visitor.check_in_time
        visitor.current_duration = int(duration.total_seconds() / 60)

    # Calculate average daily attendance (last 30 days)
    thirty_days_ago = today - timezone.timedelta(days=30)
    attendance_by_day = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date__gte=thirty_days_ago
    ).values('check_in_time__date').annotate(count=Count('id'))

    if attendance_by_day:
        avg_daily_attendance = sum(day['count'] for day in attendance_by_day) / len(attendance_by_day)
        avg_daily_attendance = round(avg_daily_attendance)
    else:
        avg_daily_attendance = 0

    # Calculate average duration
    attendances_with_duration = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date__gte=thirty_days_ago,
        check_out_time__isnull=False
    )

    if attendances_with_duration:
        total_duration_minutes = 0
        count = 0

        for attendance in attendances_with_duration:
            duration = attendance.check_out_time - attendance.check_in_time
            total_duration_minutes += duration.total_seconds() / 60
            count += 1

        avg_duration = round(total_duration_minutes / count)
    else:
        avg_duration = 0

    # Get popular plans
    popular_plans = MembershipPlan.objects.filter(is_active=True).annotate(
        member_count=Count('memberships')
    ).order_by('-member_count')[:4]

    # Get active members list for check-in
    active_memberships_list = Membership.objects.filter(
        library=library,
        is_active=True,
        end_date__gte=today
    )
    active_members_list = [membership.user for membership in active_memberships_list]

    # Get active plans for renewal
    active_plans = MembershipPlan.objects.filter(is_active=True)

    # Get recent activities
    # In a real implementation, this would come from an activity log model
    # For now, we'll just use placeholder data
    recent_activities = [
        {
            'type': 'new',
            'title': 'New Member Joined',
            'description': 'Rahul Sharma joined with Student Monthly Membership',
            'timestamp': timezone.now() - timezone.timedelta(hours=2)
        },
        {
            'type': 'renew',
            'title': 'Membership Renewed',
            'description': 'Priya Patel renewed General Quarterly Membership',
            'timestamp': timezone.now() - timezone.timedelta(hours=5)
        },
        {
            'type': 'checkin',
            'title': 'Reading Hall Check-in',
            'description': 'Amit Kumar checked in for Competitive Exam Preparation',
            'timestamp': timezone.now() - timezone.timedelta(hours=6)
        },
        {
            'type': 'checkout',
            'title': 'Reading Hall Check-out',
            'description': 'Neha Singh checked out after 3 hours 45 minutes',
            'timestamp': timezone.now() - timezone.timedelta(hours=7)
        },
        {
            'type': 'expire',
            'title': 'Membership Expired',
            'description': 'Vikram Joshi\'s Student Monthly Membership expired',
            'timestamp': timezone.now() - timezone.timedelta(days=1)
        }
    ]

    context = {
        'library': library,
        'total_members': total_members,
        'active_members': active_members,
        'expiring_soon': expiring_soon,
        'total_revenue': total_revenue,
        'today_attendance': today_attendance,
        'current_attendance': current_attendance,
        'current_visitors': current_visitors,
        'avg_daily_attendance': avg_daily_attendance,
        'avg_duration': avg_duration,
        'expiring_memberships': expiring_memberships,
        'popular_plans': popular_plans,
        'recent_activities': recent_activities,
        'active_members_list': active_members_list,
        'active_plans': active_plans,
        'today': today,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/dashboard.html', context)


@login_required
@user_passes_test(is_library_admin)
def membership_plans(request):
    """View function for managing membership plans."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all membership plans
    plans = MembershipPlan.objects.all().order_by('-is_active', 'name')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        plans = plans.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        is_active_bool = is_active.lower() == 'true'
        plans = plans.filter(is_active=is_active_bool)

    # Get membership counts for each plan
    for plan in plans:
        plan.member_count = Membership.objects.filter(plan=plan, library=library).count()
        plan.active_member_count = Membership.objects.filter(plan=plan, library=library, is_active=True).count()

    context = {
        'library': library,
        'plans': plans,
        'search_query': search_query,
        'is_active': is_active,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/plans.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_membership_plan(request):
    """View function for adding a new membership plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        duration_days = request.POST.get('duration_days')
        max_books_allowed = request.POST.get('max_books_allowed')
        max_borrowing_days = request.POST.get('max_borrowing_days')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, description, duration_days, max_books_allowed, max_borrowing_days, price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:add_membership_plan')

        try:
            # Create the membership plan
            plan = MembershipPlan.objects.create(
                name=name,
                description=description,
                duration_days=int(duration_days),
                max_books_allowed=int(max_books_allowed),
                max_borrowing_days=int(max_borrowing_days),
                price=float(price),
                is_active=is_active
            )

            messages.success(request, f"Membership plan '{plan.name}' has been created successfully.")
            return redirect('library_admin:membership_plans')

        except Exception as e:
            messages.error(request, f"Error creating membership plan: {str(e)}")
            return redirect('library_admin:add_membership_plan')

    context = {
        'library': library,
        'page_title': 'Add Membership Plan',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/add_plan.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_membership_plan(request, plan_id):
    """View function for editing a membership plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        plan = MembershipPlan.objects.get(id=plan_id)
    except MembershipPlan.DoesNotExist:
        messages.error(request, "Membership plan not found.")
        return redirect('library_admin:membership_plans')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        duration_days = request.POST.get('duration_days')
        max_books_allowed = request.POST.get('max_books_allowed')
        max_borrowing_days = request.POST.get('max_borrowing_days')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, description, duration_days, max_books_allowed, max_borrowing_days, price]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:edit_membership_plan', plan_id=plan.id)

        try:
            # Update the membership plan
            plan.name = name
            plan.description = description
            plan.duration_days = int(duration_days)
            plan.max_books_allowed = int(max_books_allowed)
            plan.max_borrowing_days = int(max_borrowing_days)
            plan.price = float(price)
            plan.is_active = is_active
            plan.save()

            messages.success(request, f"Membership plan '{plan.name}' has been updated successfully.")
            return redirect('library_admin:membership_plans')

        except Exception as e:
            messages.error(request, f"Error updating membership plan: {str(e)}")
            return redirect('library_admin:edit_membership_plan', plan_id=plan.id)

    context = {
        'library': library,
        'plan': plan,
        'page_title': 'Edit Membership Plan',
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/edit_plan.html', context)


@login_required
@user_passes_test(is_library_admin)
def delete_membership_plan(request, plan_id):
    """View function for deleting a membership plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        plan = MembershipPlan.objects.get(id=plan_id)

        # Check if the plan is being used by any memberships
        if Membership.objects.filter(plan=plan).exists():
            messages.error(request, f"Cannot delete plan '{plan.name}' as it is being used by existing memberships.")
            return redirect('library_admin:membership_plans')

        plan_name = plan.name
        plan.delete()

        messages.success(request, f"Membership plan '{plan_name}' has been deleted successfully.")

    except MembershipPlan.DoesNotExist:
        messages.error(request, "Membership plan not found.")

    return redirect('library_admin:membership_plans')


@login_required
@user_passes_test(is_library_admin)
def members(request):
    """View function for managing library members."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all memberships for this library
    memberships = Membership.objects.filter(library=library).order_by('-is_active', '-end_date')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        memberships = memberships.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(membership_number__icontains=search_query)
        )

    # Filter by status
    status = request.GET.get('status', '')
    today = timezone.now().date()

    if status == 'active':
        memberships = memberships.filter(is_active=True, end_date__gte=today)
    elif status == 'expired':
        memberships = memberships.filter(Q(is_active=False) | Q(end_date__lt=today))
    elif status == 'expiring':
        # Expiring in the next 7 days
        expiry_threshold = today + timezone.timedelta(days=7)
        memberships = memberships.filter(is_active=True, end_date__gte=today, end_date__lte=expiry_threshold)

    # Mark memberships as expiring soon (within 7 days)
    expiry_threshold = today + timezone.timedelta(days=7)
    for membership in memberships:
        membership.expiring_soon = membership.is_active and membership.end_date <= expiry_threshold and membership.end_date >= today

    # Get active plans for the form
    active_plans = MembershipPlan.objects.filter(is_active=True)

    context = {
        'library': library,
        'memberships': memberships,
        'active_plans': active_plans,
        'search_query': search_query,
        'status': status,
        'today': today,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/members.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_member(request):
    """View function for adding a new member."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        id_proof = request.POST.get('id_proof', '')
        id_number = request.POST.get('id_number', '')
        plan_id = request.POST.get('plan_id')
        start_date_str = request.POST.get('start_date')
        notes = request.POST.get('notes', '')

        # Validate required fields
        if not all([first_name, last_name, email, phone, plan_id, start_date_str]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:members')

        try:
            # Check if user already exists
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                # Check if user already has a membership in this library
                if Membership.objects.filter(user=existing_user, library=library).exists():
                    messages.error(request, f"User with email {email} already has a membership in this library.")
                    return redirect('library_admin:members')

                member = existing_user
            else:
                # Create a new user
                username = email.split('@')[0] + str(random.randint(100, 999))
                password = User.objects.make_random_password()

                member = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    user_type='MEMBER'
                )

                # Update user profile fields
                member.phone_number = phone
                member.address = address
                # Store ID proof info in the address field for now
                if id_proof and id_number:
                    member.address = f"{address}\n\nID Proof: {id_proof} - {id_number}"
                member.save()

            # Get the membership plan
            plan = MembershipPlan.objects.get(id=plan_id)

            # Parse start date
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()

            # Calculate end date based on plan duration
            end_date = start_date + timezone.timedelta(days=plan.duration_days)

            # Create the membership
            membership = Membership.objects.create(
                user=member,
                library=library,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )

            messages.success(request, f"Member {member.get_full_name()} has been added successfully with membership ID: {membership.membership_number}.")

            # Send welcome email with credentials if it's a new user
            if not existing_user:
                # In a real implementation, you would send an email with the credentials
                messages.info(request, f"New user created with username: {username} and a random password. Please ask the member to check their email or reset their password.")

            return redirect('library_admin:members')

        except Exception as e:
            messages.error(request, f"Error adding member: {str(e)}")
            return redirect('library_admin:members')

    return redirect('library_admin:members')


@login_required
@user_passes_test(is_library_admin)
def renew_membership(request):
    """View function for renewing a membership."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        membership_id = request.POST.get('membership_id')
        plan_id = request.POST.get('plan_id')
        start_date_str = request.POST.get('start_date')
        payment_method = request.POST.get('payment_method', 'Cash')
        payment_reference = request.POST.get('payment_reference', '')

        # Validate required fields
        if not all([membership_id, plan_id, start_date_str]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:members')

        try:
            # Get the membership
            membership = Membership.objects.get(id=membership_id, library=library)

            # Get the new plan
            plan = MembershipPlan.objects.get(id=plan_id)

            # Parse start date
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()

            # Calculate end date based on plan duration
            end_date = start_date + timezone.timedelta(days=plan.duration_days)

            # Update the membership
            membership.plan = plan
            membership.start_date = start_date
            membership.end_date = end_date
            membership.is_active = True
            membership.save()

            # In a real implementation, you would record the payment details

            messages.success(request, f"Membership for {membership.user.get_full_name()} has been renewed successfully until {end_date.strftime('%B %d, %Y')}.")

            return redirect('library_admin:members')

        except Membership.DoesNotExist:
            messages.error(request, "Membership not found.")
        except MembershipPlan.DoesNotExist:
            messages.error(request, "Membership plan not found.")
        except Exception as e:
            messages.error(request, f"Error renewing membership: {str(e)}")

    return redirect('library_admin:members')


@login_required
@user_passes_test(is_library_admin)
def member_attendance(request):
    """View function for managing member attendance in the reading hall."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all attendance records for this library
    attendances = MemberAttendance.objects.filter(library=library).order_by('-check_in_time')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        attendances = attendances.filter(
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(purpose__icontains=search_query)
        )

    # Filter by date
    date_filter = request.GET.get('date', '')
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            attendances = attendances.filter(check_in_time__date=filter_date)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")

    # Get active members for the form
    active_memberships = Membership.objects.filter(library=library, is_active=True)
    active_members = [membership.user for membership in active_memberships]

    context = {
        'library': library,
        'attendances': attendances,
        'active_members': active_members,
        'search_query': search_query,
        'date_filter': date_filter,
        'today': timezone.now().date(),
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/attendance.html', context)


@login_required
@user_passes_test(is_library_admin)
def record_attendance(request):
    """View function for recording member attendance."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'check_in':
            member_id = request.POST.get('member_id')
            purpose = request.POST.get('purpose', '')
            notes = request.POST.get('notes', '')

            try:
                member = User.objects.get(id=member_id)

                # Check if member has an active membership
                if not Membership.objects.filter(user=member, library=library, is_active=True).exists():
                    messages.error(request, f"User {member.get_full_name()} does not have an active membership.")
                    return redirect('library_admin:member_attendance')

                # Check if member already has an open attendance record
                if MemberAttendance.objects.filter(user=member, library=library, check_out_time__isnull=True).exists():
                    messages.error(request, f"Member {member.get_full_name()} already has an open attendance record.")
                    return redirect('library_admin:member_attendance')

                # Create attendance record
                attendance = MemberAttendance.objects.create(
                    user=member,
                    library=library,
                    purpose=purpose,
                    notes=notes,
                    recorded_by=user
                )

                messages.success(request, f"Member {member.get_full_name()} has been checked in successfully.")

            except User.DoesNotExist:
                messages.error(request, "Member not found.")
            except Exception as e:
                messages.error(request, f"Error recording attendance: {str(e)}")

        elif action == 'check_out':
            attendance_id = request.POST.get('attendance_id')

            try:
                attendance = MemberAttendance.objects.get(id=attendance_id, library=library)

                if attendance.check_out_time:
                    messages.error(request, "This attendance record has already been checked out.")
                    return redirect('library_admin:member_attendance')

                attendance.check_out_time = timezone.now()
                attendance.save()

                duration = attendance.duration()
                member_name = attendance.user.get_full_name()

                messages.success(request, f"Member {member_name} has been checked out successfully. Duration: {duration} minutes.")

            except MemberAttendance.DoesNotExist:
                messages.error(request, "Attendance record not found.")
            except Exception as e:
                messages.error(request, f"Error checking out: {str(e)}")

    return redirect('library_admin:member_attendance')


@login_required
@user_passes_test(is_library_admin)
def attendance_report(request):
    """View function for generating attendance reports."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get date range for report
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    if not start_date_str or not end_date_str:
        # Default to last 30 days
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
    else:
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('library_admin:member_attendance')

    # Get attendance records for the date range
    attendances = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date__gte=start_date,
        check_in_time__date__lte=end_date
    ).order_by('-check_in_time')

    # Calculate statistics
    total_visits = attendances.count()
    unique_visitors = attendances.values('user').distinct().count()

    # Calculate average visit duration
    total_duration = 0
    visits_with_duration = 0

    for attendance in attendances:
        if attendance.duration():
            total_duration += attendance.duration()
            visits_with_duration += 1

    avg_duration = total_duration / visits_with_duration if visits_with_duration > 0 else 0

    # Get most frequent visitors
    frequent_visitors = User.objects.filter(
        attendances__library=library,
        attendances__check_in_time__date__gte=start_date,
        attendances__check_in_time__date__lte=end_date
    ).annotate(
        visit_count=Count('attendances')
    ).order_by('-visit_count')[:10]

    # Get visits by purpose
    visits_by_purpose = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date__gte=start_date,
        check_in_time__date__lte=end_date,
        purpose__isnull=False
    ).exclude(
        purpose=''
    ).values('purpose').annotate(
        count=Count('id')
    ).order_by('-count')

    # Get visits by day of week
    visits_by_day = MemberAttendance.objects.filter(
        library=library,
        check_in_time__date__gte=start_date,
        check_in_time__date__lte=end_date
    ).extra(
        select={'day': "EXTRACT(DOW FROM check_in_time)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Format day names
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for day_data in visits_by_day:
        day_data['day_name'] = day_names[int(day_data['day'])]

    context = {
        'library': library,
        'attendances': attendances,
        'start_date': start_date,
        'end_date': end_date,
        'total_visits': total_visits,
        'unique_visitors': unique_visitors,
        'avg_duration': round(avg_duration, 1),
        'frequent_visitors': frequent_visitors,
        'visits_by_purpose': visits_by_purpose,
        'visits_by_day': visits_by_day,
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/attendance_report.html', context)


@login_required
@user_passes_test(is_library_admin)
def library_plans(request):
    """View function for managing library plans."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    # Get all library plans
    plans = LibraryPlan.objects.filter(library=library).order_by('-is_active', '-start_date')

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        plans = plans.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(target_audience__icontains=search_query)
        )

    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        is_active_bool = is_active.lower() == 'true'
        plans = plans.filter(is_active=is_active_bool)

    context = {
        'library': library,
        'plans': plans,
        'search_query': search_query,
        'is_active': is_active,
        'today': timezone.now().date(),
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/library_plans.html', context)


@login_required
@user_passes_test(is_library_admin)
def add_library_plan(request):
    """View function for adding a new library plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date', '')
        target_audience = request.POST.get('target_audience', '')
        budget = request.POST.get('budget', '')
        success_metrics = request.POST.get('success_metrics', '')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, description, start_date_str]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:add_library_plan')

        try:
            # Parse dates
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = None
            if end_date_str:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Create the library plan
            plan = LibraryPlan.objects.create(
                library=library,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                target_audience=target_audience,
                budget=float(budget) if budget else None,
                success_metrics=success_metrics,
                is_active=is_active,
                created_by=user
            )

            messages.success(request, f"Library plan '{plan.name}' has been created successfully.")
            return redirect('library_admin:library_plans')

        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            messages.error(request, f"Error creating library plan: {str(e)}")

    context = {
        'library': library,
        'page_title': 'Add Library Plan',
        'today': timezone.now().date(),
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/add_library_plan.html', context)


@login_required
@user_passes_test(is_library_admin)
def edit_library_plan(request, plan_id):
    """View function for editing a library plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        plan = LibraryPlan.objects.get(id=plan_id, library=library)
    except LibraryPlan.DoesNotExist:
        messages.error(request, "Library plan not found.")
        return redirect('library_admin:library_plans')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date', '')
        target_audience = request.POST.get('target_audience', '')
        budget = request.POST.get('budget', '')
        success_metrics = request.POST.get('success_metrics', '')
        is_active = request.POST.get('is_active') == 'on'

        # Validate required fields
        if not all([name, description, start_date_str]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('library_admin:edit_library_plan', plan_id=plan.id)

        try:
            # Parse dates
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = None
            if end_date_str:
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Update the library plan
            plan.name = name
            plan.description = description
            plan.start_date = start_date
            plan.end_date = end_date
            plan.target_audience = target_audience
            plan.budget = float(budget) if budget else None
            plan.success_metrics = success_metrics
            plan.is_active = is_active
            plan.save()

            messages.success(request, f"Library plan '{plan.name}' has been updated successfully.")
            return redirect('library_admin:library_plans')

        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            messages.error(request, f"Error updating library plan: {str(e)}")

    context = {
        'library': library,
        'plan': plan,
        'page_title': 'Edit Library Plan',
        'today': timezone.now().date(),
        'pending_requests_count': MembershipRequest.objects.filter(library=library, status='PENDING').count(),
    }

    return render(request, 'library_admin/membership/edit_library_plan.html', context)


@login_required
@user_passes_test(is_library_admin)
def delete_library_plan(request, plan_id):
    """View function for deleting a library plan."""
    user = request.user
    libraries = Library.objects.filter(admin=user)

    if not libraries.exists():
        messages.warning(request, "You are not assigned to any library yet.")
        return redirect('core:home')

    library = libraries.first()

    try:
        plan = LibraryPlan.objects.get(id=plan_id, library=library)
        plan_name = plan.name
        plan.delete()

        messages.success(request, f"Library plan '{plan_name}' has been deleted successfully.")

    except LibraryPlan.DoesNotExist:
        messages.error(request, "Library plan not found.")

    return redirect('library_admin:library_plans')


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