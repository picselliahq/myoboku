from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def debug_superuser_member_required(
    view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url="admin:login"
):
    """
    Decorator for views that checks that DEBUG is true, that the user is logged in and is a superuser,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: settings.DEBUG and u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
