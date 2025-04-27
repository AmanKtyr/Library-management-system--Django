from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for allauth that works with our custom User model.
    This adapter doesn't use the username field since our User model doesn't have one.
    """
    
    def populate_username(self, request, user):
        """
        Override the populate_username method to not set a username.
        Our User model doesn't have a username field.
        """
        # Don't set username as our model doesn't have this field
        pass
    
    def save_user(self, request, user, form, commit=True):
        """
        Override the save_user method to properly save our custom User model.
        """
        # Get data from the form
        data = form.cleaned_data
        
        # Set email
        user.email = data.get('email')
        
        # Set user_type to MEMBER for self-registration
        user.user_type = 'MEMBER'
        
        # Set first_name and last_name if provided
        if 'first_name' in data:
            user.first_name = data.get('first_name')
        if 'last_name' in data:
            user.last_name = data.get('last_name')
        
        # Set password
        if 'password1' in data:
            user.set_password(data.get('password1'))
        else:
            user.set_unusable_password()
        
        # Save the user
        if commit:
            user.save()
        
        return user
