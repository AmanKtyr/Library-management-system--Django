from django import forms
from .models import Transaction, Membership, MembershipPlan
from apps.books.models import BookCopy
from apps.libraries.models import Library
from apps.accounts.models import User

class TransactionForm(forms.Form):
    """Form for creating transactions (borrow, return, reserve)."""
    book_copy = forms.ModelChoiceField(queryset=BookCopy.objects.none())
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    processed_by = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        transaction_type = kwargs.pop('transaction_type', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Get libraries where the user has an active membership
            user_libraries = Library.objects.filter(memberships__user=user, memberships__is_active=True)

            if transaction_type == 'BORROW' or transaction_type == 'RESERVE':
                # For borrowing or reserving, show available books
                if transaction_type == 'BORROW':
                    status_filter = 'AVAILABLE'
                else:  # RESERVE
                    status_filter = ['AVAILABLE', 'BORROWED']

                self.fields['book_copy'].queryset = BookCopy.objects.filter(
                    library__in=user_libraries,
                    status__in=status_filter if isinstance(status_filter, list) else [status_filter]
                )

            # For staff users, show the processed_by field
            if user.is_super_admin or user.is_library_admin or user.is_staff_member:
                self.fields['processed_by'].queryset = User.objects.filter(
                    user_type__in=['SUPER_ADMIN', 'LIBRARY_ADMIN', 'STAFF']
                )
                self.fields['processed_by'].initial = user
            else:
                self.fields.pop('processed_by')

class MembershipForm(forms.ModelForm):
    """Form for creating and updating memberships."""

    class Meta:
        model = Membership
        fields = ['user', 'library', 'plan']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If the form is being used by a regular member
        if user and user.is_library_member:
            self.fields['user'].initial = user
            self.fields['user'].widget = forms.HiddenInput()

            # Only show libraries where the user doesn't already have an active membership
            existing_memberships = Membership.objects.filter(user=user, is_active=True).values_list('library', flat=True)
            self.fields['library'].queryset = Library.objects.filter(is_active=True).exclude(id__in=existing_memberships)

        # If the form is being used by a library admin or staff
        elif user and (user.is_library_admin or user.is_staff_member):
            # Get the library associated with this admin/staff
            if user.is_library_admin:
                library = Library.objects.filter(admin=user).first()
            else:
                library = user.staffed_libraries.first()

            if library:
                self.fields['library'].initial = library
                self.fields['library'].widget = forms.HiddenInput()

                # Only show users who don't already have an active membership for this library
                existing_members = Membership.objects.filter(library=library, is_active=True).values_list('user', flat=True)
                self.fields['user'].queryset = User.objects.filter(user_type='MEMBER').exclude(id__in=existing_members)

        # Always show only active plans
        self.fields['plan'].queryset = MembershipPlan.objects.filter(is_active=True)
