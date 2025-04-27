from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User
from apps.libraries.models import Library


class SimpleSignupForm(forms.Form):
    """
    A completely custom signup form that doesn't rely on allauth.
    This form is designed to work with our custom User model that uses email instead of username.
    Includes library selection for membership request.
    """
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email address')
        })
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First name')
        })
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last name')
        })
    )
    phone_number = forms.CharField(
        label=_("Phone number"),
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Phone number')
        })
    )
    address = forms.CharField(
        label=_("Address"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Address'),
            'rows': 3
        })
    )
    library = forms.ModelChoiceField(
        label=_("Select Library"),
        queryset=Library.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text=_("Select the library you want to join. Your request will be reviewed by the library administrator.")
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password')
        })
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm Password')
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1)
        except ValidationError as error:
            self.add_error('password1', error)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        return password2

    def save(self):
        """
        Create a new user with the form data and create a membership request.
        The user will be set to pending approval status.
        """
        from apps.transactions.models import MembershipRequest

        # Create the user
        user = User(
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone_number=self.cleaned_data.get('phone_number', ''),
            address=self.cleaned_data.get('address', ''),
            user_type='MEMBER',  # Default to MEMBER for self-registration
            approval_status='PENDING'  # Set to pending approval
        )
        user.set_password(self.cleaned_data['password1'])
        user.save()

        # Create a membership request
        library = self.cleaned_data['library']
        membership_request = MembershipRequest(
            user=user,
            library=library,
            status='PENDING'
        )
        membership_request.save()

        return user


class CustomUserCreationForm(forms.ModelForm):
    """
    A form for creating new users with all required fields.
    Includes all required fields plus password confirmation.
    """
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password'),
            'autocomplete': 'new-password'
        }),
        help_text=_("Your password must be at least 8 characters long and contain letters and numbers."),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm Password'),
            'autocomplete': 'new-password'
        }),
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'user_type', 'phone_number',
                  'address', 'date_of_birth', 'profile_picture', 'is_active')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email address')
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last name')
            }),
            'user_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Phone number')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Address'),
                'rows': 3
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1, self.instance)
        except ValidationError as error:
            self.add_error('password1', error)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        # Set additional permissions based on user_type
        if self.cleaned_data.get('user_type') == 'SUPER_ADMIN':
            user.is_staff = True
            user.is_superuser = True
        elif self.cleaned_data.get('user_type') == 'LIBRARY_ADMIN':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user
