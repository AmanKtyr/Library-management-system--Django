from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Library
from books.models import BookCopy
from transactions.models import Membership
from accounts.models import User
from .forms import LibraryForm, LibraryStaffForm  # We'll create these forms later

def library_list(request):
    """View function for listing all libraries."""
    libraries = Library.objects.filter(is_active=True)

    context = {
        'libraries': libraries,
    }

    return render(request, 'libraries/library_list.html', context)

def library_detail(request, slug):
    """View function for displaying details of a specific library."""
    library = get_object_or_404(Library, slug=slug, is_active=True)

    # Get book copies available in this library
    book_copies = BookCopy.objects.filter(library=library, status='AVAILABLE')

    # Get total number of books in this library
    total_books = BookCopy.objects.filter(library=library).count()

    # Get total number of members in this library
    total_members = Membership.objects.filter(library=library, is_active=True).count()

    context = {
        'library': library,
        'book_copies': book_copies,
        'total_books': total_books,
        'total_members': total_members,
    }

    return render(request, 'libraries/library_detail.html', context)

@login_required
def create_library(request):
    """View function for creating a new library (Super Admin only)."""
    # Redirect to the manage libraries page, which now includes the create form
    return redirect('libraries:manage_libraries')

@login_required
def manage_libraries(request):
    """View function for managing libraries (Super Admin only)."""
    user = request.user

    if not user.is_super_admin:
        return HttpResponseForbidden("You don't have permission to access this page.")

    libraries = Library.objects.all()

    # Create a new form instance for adding a library
    form = LibraryForm()

    if request.method == 'POST':
        form = LibraryForm(request.POST, request.FILES)
        if form.is_valid():
            library = form.save()
            messages.success(request, f"Library '{library.name}' created successfully.")
            return redirect('libraries:manage_libraries')

    context = {
        'libraries': libraries,
        'form': form,
    }

    return render(request, 'libraries/manage_libraries.html', context)

@login_required
def manage_library(request, slug):
    """View function for managing a specific library."""
    user = request.user
    library = get_object_or_404(Library, slug=slug)

    # Check if user has permission to manage this library
    if not (user.is_super_admin or (user.is_library_admin and library.admin == user)):
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        form = LibraryForm(request.POST, request.FILES, instance=library)
        if form.is_valid():
            form.save()
            messages.success(request, f"Library '{library.name}' updated successfully.")
            return redirect('libraries:manage_library', slug=library.slug)
    else:
        form = LibraryForm(instance=library)

    context = {
        'library': library,
        'form': form,
    }

    return render(request, 'libraries/manage_library.html', context)

@login_required
def manage_library_staff(request, slug):
    """View function for managing staff of a specific library."""
    user = request.user
    library = get_object_or_404(Library, slug=slug)

    # Check if user has permission to manage this library's staff
    if not (user.is_super_admin or (user.is_library_admin and library.admin == user)):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get all staff members of this library
    staff_members = library.staff.all()

    # Get all users with STAFF role who are not already staff of this library
    available_staff = User.objects.filter(user_type='STAFF').exclude(id__in=staff_members.values_list('id', flat=True))

    if request.method == 'POST':
        form = LibraryStaffForm(request.POST, library=library, available_staff=available_staff)
        if form.is_valid():
            selected_staff = form.cleaned_data['staff']
            library.staff.set(selected_staff)
            messages.success(request, f"Staff for '{library.name}' updated successfully.")
            return redirect('libraries:manage_library_staff', slug=library.slug)
    else:
        form = LibraryStaffForm(library=library, available_staff=available_staff, initial={'staff': staff_members})

    context = {
        'library': library,
        'staff_members': staff_members,
        'form': form,
    }

    return render(request, 'libraries/manage_library_staff.html', context)

@login_required
def manage_library_members(request, slug):
    """View function for managing members of a specific library."""
    user = request.user
    library = get_object_or_404(Library, slug=slug)

    # Check if user has permission to manage this library's members
    if not (user.is_super_admin or (user.is_library_admin and library.admin == user) or
            (user.is_staff_member and user in library.staff.all())):
        return HttpResponseForbidden("You don't have permission to access this page.")

    # Get all memberships for this library
    memberships = Membership.objects.filter(library=library)

    context = {
        'library': library,
        'memberships': memberships,
    }

    return render(request, 'libraries/manage_library_members.html', context)
