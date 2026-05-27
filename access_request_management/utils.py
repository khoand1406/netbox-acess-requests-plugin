from .models import AccessRequestHistory
def create_access_request_history(
    *,
    access_request,
    performed_by,
    action,
    status="",
    description="",
):

    return AccessRequestHistory.objects.create(
        access_request=access_request,
        perform_by=performed_by,
        action=action,
        status=status,
        description=description,
    )