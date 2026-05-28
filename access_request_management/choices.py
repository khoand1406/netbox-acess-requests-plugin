from utilities.choices import ChoiceSet
from django.utils.translation import gettext_lazy as _

class AccessRequestStatusChoices(ChoiceSet):
    """
    Trạng thái của phiếu yêu cầu ra vào.
    """
    key = 'AccessRequest.status'

    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED= 'confirmed'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FINISHED= 'closed'

    CHOICES = [
        (STATUS_DRAFT, _('Draft'), 'gray'),
        (STATUS_PENDING, _('Pending Approval'), 'blue'),
        (STATUS_CONFIRMED, _('CONFIRMED'), 'blue'),
        (STATUS_APPROVED, _('Approved'), 'green'),
        (STATUS_REJECTED, _('Rejected'), 'red'),
        (STATUS_CANCELLED, _('Cancelled'), 'orange'),
        (STATUS_FINISHED, _('Close'), 'blue')
    ]
    
class AccessRequestHistoryActionChoices(ChoiceSet):
    key= 'AccessRequestHistory.action'
    
    ACTION_ADD_MEM= 'add_member'
    ACTION_UPDATE_MEM= 'update_member'
    ACTION_REMOVE_MEM= 'remove_member'
    
    ACTION_SENT_REQUEST= 'send_request'
    ACTION_UPDATE_REQUEST= 'update_request'
    
    ACTION_CONFIRM_REQUEST= 'confirmed'
    ACTION_APPROVE_REQUEST= 'approved'
    ACTION_REJECT_REQUEST= 'rejected'
    ACTION_FINISH_REQUEST='finished'
    
    ACTION_MEMBER_CHECK_IN= 'checkin'
    ACTION_MEMBER_CHECK_OUT= 'checkout'
    
    
    CHOICES = [
        (ACTION_ADD_MEM, _("Add Member"), 'blue'),
        (ACTION_UPDATE_MEM, _("Update Member"), 'orange'),
        (ACTION_REMOVE_MEM, _("Delete Member"), 'red'),
        (ACTION_SENT_REQUEST, _("Send Request"), 'green'),
        (ACTION_UPDATE_REQUEST, _("Update Request"), 'orange'),
        (ACTION_CONFIRM_REQUEST, _("Confirmed Request"), 'blue'),
        (ACTION_APPROVE_REQUEST, _("Approve Request"), 'green'),
        (ACTION_REJECT_REQUEST, _("Reject Request"), 'red'),
        (ACTION_MEMBER_CHECK_IN, _("Check In"), 'green'),
        (ACTION_MEMBER_CHECK_OUT, _("Check Out"), 'orange'),
        (ACTION_FINISH_REQUEST, _("Finish Request"), 'blue')
    ]
    
class AccessRequestHistoryStatusChoices(ChoiceSet):
    key= 'AccessRequestHistory.status'
    
    STATUS_SUCCESS= 'success'
    STATUS_FAILED= 'failed'
    
    CHOICES= [
        (STATUS_SUCCESS, _('Success'), 'green'),
        (STATUS_FAILED, _('Failed'), 'red')    
    ]
    DEFAULT= STATUS_SUCCESS
    
class AccessRequestPersonStatusChoices(ChoiceSet):
    key= 'AccessRequestPerson.status'
    
    STATUS_PENDING= 'pending'
    STATUS_VERIFY= 'verified'
    STATUS_UNVERIFY= 'unverified'
    
    CHOICES= [
        (STATUS_PENDING, _('PENDING'), 'orange'),
        (STATUS_VERIFY, _('VERIFIED'), 'green'),
        (STATUS_UNVERIFY, _('UNVERIFIED'), 'red')
    ]
    
    DEFAULT= STATUS_PENDING
    
class AccessRequestPersonEntryStatusChoice(ChoiceSet):
    key= 'AccessRequestPerson.entry_status'
    STATUS_PENDING= 'pending'
    STATUS_IN= 'in'
    STATUS_OUT= 'out'
    
    CHOICES= [
        (STATUS_PENDING, _('PENDING'), 'grey'),
        (STATUS_IN, _('IN'), 'green'),
        (STATUS_OUT, _('OUT'), 'orange')
    ]
    
    DEFAULT= STATUS_PENDING
    
    