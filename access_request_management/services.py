from .models import AccessRequestHistoryStatusChoices, AccessRequestHistoryActionChoices
from .utils import create_access_request_history
class AccessRequestHistoryService:
    
    @staticmethod
    def log(access_request, performed_by, action, description="", status=None):
        return create_access_request_history(
            access_request=access_request,
            performed_by=performed_by,
            action=action,
            status=status or AccessRequestHistoryStatusChoices.STATUS_SUCCESS,
            description=description,
        )

    @staticmethod
    def log_member_add(obj, user):
        return AccessRequestHistoryService.log(
            access_request=obj.access_request,
            performed_by=user,
            action=AccessRequestHistoryActionChoices.ACTION_ADD_MEM,
            description=f"Added member: {obj.full_name}",
        )

    @staticmethod
    def log_member_update(obj, user):
        return AccessRequestHistoryService.log(
            access_request=obj.access_request,
            performed_by=user,
            action=AccessRequestHistoryActionChoices.ACTION_UPDATE_MEM,
            description=f"Updated member: {obj.full_name}",
        )

    @staticmethod
    def log_failed(access_request, user, action, error):
        return AccessRequestHistoryService.log(
            access_request=access_request,
            performed_by=user,
            action=action,
            status=AccessRequestHistoryStatusChoices.STATUS_FAILED,
            description=str(error),
        )