from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.contrib.auth import authenticate, login

from .forms import CustomUserCreationForm, SimpleSignupForm
from .models import User

class SimpleSignupView(FormView):
    """
    A completely custom signup view that doesn't rely on allauth.
    This view uses our custom SimpleSignupForm to create new users and membership requests.
    """
    form_class = SimpleSignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('account_login')

    def form_valid(self, form):
        # Create the user and membership request
        form.save()

        # Get the library name for the success message
        library_name = form.cleaned_data['library'].name

        # Add a success message
        messages.success(
            self.request,
            f"Your account has been created and your membership request for {library_name} has been submitted. "
            f"IMPORTANT: You will not be able to login until your request is approved by the library administrator. "
            f"You will receive an email when your request is approved."
        )

        # Redirect to login page
        return super().form_valid(form)

def is_admin(user):
    """Check if user is a super admin or library admin."""
    return user.is_super_admin or user.is_library_admin

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class UserCreateView(SuccessMessageMixin, CreateView):
    """
    Custom view for creating users, replacing the Django admin user creation page.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'superadmin/users/user_add.html'
    success_url = reverse_lazy('superadmin:users')
    success_message = "User %(email)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add User'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Restrict user type options based on current user's permissions
        if not self.request.user.is_super_admin:
            # Library admins can only create staff and member users
            user_type_field = form.fields['user_type']
            user_type_field.choices = [
                choice for choice in user_type_field.choices
                if choice[0] in ['STAFF', 'MEMBER']
            ]
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User {form.instance.email} has been created successfully.")
        return response

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class UserListView(ListView):
    """
    Custom view for listing users, replacing the Django admin user list page.
    """
    model = User
    template_name = 'superadmin/users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter based on user permissions
        if not self.request.user.is_super_admin:
            # Library admins can only see staff and member users
            queryset = queryset.filter(
                Q(user_type='STAFF') | Q(user_type='MEMBER')
            )

        # Search functionality
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )

        # Filter by user type
        user_type = self.request.GET.get('user_type', '')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'User Management'
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_user_type'] = self.request.GET.get('user_type', '')
        context['selected_status'] = self.request.GET.get('status', '')

        # Get user type counts
        context['user_types'] = [
            {
                'name': 'Super Admin',
                'code': 'SUPER_ADMIN',
                'count': User.objects.filter(user_type='SUPER_ADMIN').count() if self.request.user.is_super_admin else 0,
                'visible': self.request.user.is_super_admin
            },
            {
                'name': 'Library Admin',
                'code': 'LIBRARY_ADMIN',
                'count': User.objects.filter(user_type='LIBRARY_ADMIN').count() if self.request.user.is_super_admin else 0,
                'visible': self.request.user.is_super_admin
            },
            {
                'name': 'Staff',
                'code': 'STAFF',
                'count': User.objects.filter(user_type='STAFF').count(),
                'visible': True
            },
            {
                'name': 'Member',
                'code': 'MEMBER',
                'count': User.objects.filter(user_type='MEMBER').count(),
                'visible': True
            }
        ]

        # Get status counts
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['inactive_users'] = User.objects.filter(is_active=False).count()

        return context

def login_view(request):
    """
    View function for the custom login page.
    Handles both GET and POST requests.
    """
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user role
        if request.user.is_super_admin:
            return redirect('superadmin:dashboard')
        elif request.user.is_library_admin:
            return redirect('library_admin:dashboard')
        elif request.user.is_staff_member:
            return redirect('staff:dashboard')
        else:  # Regular member
            return redirect('member:dashboard')

    if request.method == 'POST':
        email = request.POST.get('login')
        password = request.POST.get('password')

        # Get the user role from the form
        # First try to get it from the hidden input field
        user_role = request.POST.get('user_role', 'member')

        # If that's not set, try to get it from the radio buttons
        if not user_role or user_role == '':
            login_role = request.POST.get('login-role')
            if login_role:
                user_role = login_role

        print(f"Form data: {request.POST}")
        print(f"Selected user_role: {user_role}")

        # Validate input
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, 'accounts/login.html', {'email_error': True})

        if not password:
            messages.error(request, "Please enter your password.")
            return render(request, 'accounts/login.html', {'password_error': True, 'email': email})

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Please contact the administrator.")
                return render(request, 'accounts/login.html', {'email': email})

            # Check if the user's account has been approved (except for admins and staff)
            if user.user_type == 'MEMBER' and user.approval_status != 'APPROVED':
                if user.approval_status == 'PENDING':
                    messages.warning(request,
                        "Your membership request is pending approval by the library administrator. "
                        "You will receive an email when your request is approved. "
                        "Please check back later or contact the library for more information."
                    )
                elif user.approval_status == 'REJECTED':
                    messages.error(request,
                        "Your membership request has been rejected. "
                        "Please contact the library administrator for more information."
                    )
                return render(request, 'accounts/login.html', {'email': email})

            # Print debug information
            print(f"User role from form: {user_role}")
            print(f"User is_super_admin: {user.is_super_admin}")
            print(f"User is_library_admin: {user.is_library_admin}")
            print(f"User is_staff_member: {user.is_staff_member}")

            # Check if the selected role matches the user's actual role
            role_mismatch = False

            # Only check role match if the user explicitly selected a role other than their highest role
            if user.is_super_admin:
                # Super admin can log in as any role
                role_mismatch = False
            elif user.is_library_admin:
                # Library admin can't log in as super admin
                if user_role == 'super_admin':
                    role_mismatch = True
            elif user.is_staff_member:
                # Staff can't log in as super admin or library admin
                if user_role in ['super_admin', 'library_admin']:
                    role_mismatch = True
            else:  # Regular member
                # Member can only log in as member
                if user_role in ['super_admin', 'library_admin', 'staff']:
                    role_mismatch = True

            if role_mismatch:
                messages.error(request,
                    "The selected role does not match your account type. "
                    "Please select the correct role and try again."
                )
                return render(request, 'accounts/login.html', {'email': email, 'role_error': True})

            # Log the user in
            login(request, user)

            # Redirect based on user role
            if user_role == 'super_admin' and user.is_super_admin:
                return redirect('superadmin:dashboard')
            elif user_role == 'library_admin' and user.is_library_admin:
                return redirect('library_admin:dashboard')
            elif user_role == 'staff' and user.is_staff_member:
                return redirect('staff:dashboard')
            else:  # Regular member or fallback
                return redirect('member:dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, 'accounts/login.html', {'email': email, 'auth_error': True})

    # GET request
    return render(request, 'accounts/login.html')

