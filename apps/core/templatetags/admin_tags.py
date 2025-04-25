from django import template
from django import get_version
import sys

register = template.Library()

@register.simple_tag
def get_django_version():
    """Return the Django version."""
    return get_version()

@register.simple_tag
def get_python_version():
    """Return the Python version."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
