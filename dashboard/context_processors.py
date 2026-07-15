def role_flags(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    return {
        "is_customer_user": user.is_customer(),
        "is_mechanic_user": user.is_mechanic(),
        "is_admin_user": user.is_admin_role(),
    }
