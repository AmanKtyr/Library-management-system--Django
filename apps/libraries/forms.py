from django import forms
from .models import Library
from apps.accounts.models import User

class LibraryForm(forms.ModelForm):
    """Form for creating and updating libraries."""

    class Meta:
        model = Library
        fields = [
            'name', 'address', 'city', 'state', 'postal_code', 'country',
            'phone', 'email', 'website', 'description', 'opening_hours',
            'established_date', 'image', 'admin', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'opening_hours': forms.Textarea(attrs={'rows': 4}),
            'established_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit admin choices to users with LIBRARY_ADMIN role
        self.fields['admin'].queryset = User.objects.filter(user_type='LIBRARY_ADMIN')
        self.fields['admin'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})"

class LibraryStaffForm(forms.Form):
    """Form for managing library staff."""
    staff = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library', None)
        available_staff = kwargs.pop('available_staff', None)
        super().__init__(*args, **kwargs)

        if available_staff is not None:
            # Include current staff and available staff
            current_staff = library.staff.all() if library else User.objects.none()
            self.fields['staff'].queryset = (current_staff | available_staff).distinct()
            self.fields['staff'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.email})"
