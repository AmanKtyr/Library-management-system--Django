from django import template

register = template.Library()

@register.filter
def abs(value):
    """Returns the absolute value of a number."""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value
