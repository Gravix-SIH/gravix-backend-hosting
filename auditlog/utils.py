def log_admin_action(request, action, target_type, target_id=None, details=None):
    """
    Creates an AuditLog entry for an admin action.

    Call this in every admin view after a successful write operation.
    """
    from .models import AuditLog

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

    AuditLog.objects.create(
        actor=request.user,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {},
        ip_address=ip,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )
