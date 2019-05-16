from functools import wraps
from typing import Callable
from typing import Optional
from typing import Tuple

from django.contrib.auth.views import redirect_to_login
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import reverse

from users.models import CustomUser


def check_permissions(allowed_user_types: Tuple[str], redirect_path: Optional[str] = None) -> Callable:
    """
    Decorator that will validate if user have correct user type to get to resources.

    `allowed_user_types` argument is a tuple of UserTypes from CustomUser model.
    Types of users which are located in this tuples are allowed to get to view which is decorated by this decorator
    """
    for user_type in allowed_user_types:
        assert user_type in CustomUser.UserType._member_names_

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request: WSGIRequest, *args: dict, **kwargs: dict) -> Callable:
            if request.user.user_type not in allowed_user_types:
                return redirect_to_login(
                    request.get_full_path(), redirect_path if redirect_path is not None else reverse("login"), "next"
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
