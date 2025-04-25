from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.db.models import Q

from .forms import CustomUserCreationForm
from .models import User

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
    template_name = 'accounts/user_add.html'
    success_url = reverse_lazy('core:admin_users')
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
    template_name = 'accounts/user_list.html'
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
