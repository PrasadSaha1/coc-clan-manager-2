from django.shortcuts import redirect
from functools import wraps

def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Redirect to home page if the user is already logged in
        return view_func(request, *args, **kwargs)
    return _wrapped_view