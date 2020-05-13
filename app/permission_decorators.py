from functools import wraps
from flask import abort, redirect, url_for, request
from flask_login import current_user
from app.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                next = url_for(request.endpoint, **request.view_args)
                return redirect(url_for("auth.login", next=next))
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
