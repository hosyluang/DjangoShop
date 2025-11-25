from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required


def non_superuser_required(view_func):
    # chi cho phep user ko phai superuser
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and not u.is_superuser, login_url="/no-access/"
    )
    return login_required(actual_decorator(view_func))
