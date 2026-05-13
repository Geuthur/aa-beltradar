# Django
from django.template.defaulttags import register

# AA Example
from example import __title__, __version__


@register.simple_tag
def example_templatetag() -> str | None:
    """Example template tag."""
    return "Hello, World!"
