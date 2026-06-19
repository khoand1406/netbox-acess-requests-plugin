"""
Models for access_request_management.

For more information on NetBox models, see:
https://docs.netbox.dev/en/stable/plugins/development/models/

For NetBox model features (tags, custom fields, change logging, etc.), see:
https://docs.netbox.dev/en/stable/development/models/#netbox-model-features
"""

from django.db import models
from django.urls import reverse
from dcim.models.sites import Region, Site
from dcim.models.sites import Location
from netbox import settings
from netbox.models import NetBoxModel
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from .choices import AccessRequestHistoryActionChoices, AccessRequestHistoryStatusChoices, AccessRequestPersonEntryStatusChoice, AccessRequestPersonStatusChoices, AccessRequestStatusChoices
from django.core.validators import RegexValidator
from upload_file_plugin.models import UploadedFile


class AccessRequest(NetBoxModel):
    name= models.CharField(
        max_length=100, 
        unique= True, 
        blank= False, 
        verbose_name=_("Name"),
        help_text=_('Unique name of the access request')
    )
    status = models.CharField(
        max_length=30,
        choices=AccessRequestStatusChoices,
        default=AccessRequestStatusChoices.STATUS_DRAFT,
        verbose_name=_('Status')
    )
    planned_date= models.DateField(
        verbose_name=_("Planned Date"),
        help_text=_("Expected Entry Date")   
    )
    reason= models.CharField(
        max_length=500,
        blank=False,
        null=False,
        help_text=_("Reason for requesting access")
    )
    region= models.ForeignKey(
        to=Region,
        on_delete=models.PROTECT,
        related_name="access_request",
        blank=True,
        null= True,
        verbose_name=_("Region"),
        help_text= _("Region where site is located")
        
    )
    site= models.ForeignKey(
        to= Site,
        on_delete= models.PROTECT,
        related_name="access_request",
        blank=True,
        null=True,
        verbose_name=_("Site"),
        help_text=_("Target site/ data center")
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_access_requests',
        verbose_name=_('Created by')
    )
    class Meta:
        ordering = ('-last_updated',)
        verbose_name = _('Access Request')
        verbose_name_plural = _('Access Requests')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'plugins:access_request_management:accessrequest',
            args=[self.pk]
        )
    def get_status_color(self):
        status_colors= {
            AccessRequestStatusChoices.STATUS_PENDING: 'secondary',
            AccessRequestStatusChoices.STATUS_APPROVED: 'success',
            AccessRequestStatusChoices.STATUS_REJECTED: 'danger',
            AccessRequestStatusChoices.STATUS_CONFIRMED: 'success',
            AccessRequestStatusChoices.STATUS_FINISHED: 'warning'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_status_display(self):
        return dict(
            (c[0], c[1]) for c in AccessRequestStatusChoices.CHOICES
        ).get(self.status, self.status)
    

    @property
    def is_editable(self):
        return self.status not in (
            AccessRequestStatusChoices.STATUS_APPROVED,
            AccessRequestStatusChoices.STATUS_FINISHED,
            AccessRequestStatusChoices.STATUS_PENDING,
            AccessRequestStatusChoices.STATUS_CONFIRMED
        )

    @property
    def is_deletable(self):
        return self.is_editable 
    
    @property
    def can_submit(self):
        return (
        self.status in (AccessRequestStatusChoices.STATUS_DRAFT, AccessRequestStatusChoices.STATUS_REJECTED)
        and self.persons.exists()
    )
    
    @property
    def is_pending(self):
        return (self.status == AccessRequestStatusChoices.STATUS_PENDING)
        
    @property
    def is_confirmed(self):
            return self.status == AccessRequestStatusChoices.STATUS_CONFIRMED
    @property
    def is_approved(self):
        return (
            self.status == AccessRequestStatusChoices.STATUS_APPROVED
        )
    @property
    def is_rejected(self):
        return (
            self.status== AccessRequestStatusChoices.STATUS_REJECTED
        )
    @property
    def is_finished(self):
        return (
            self.status== AccessRequestStatusChoices.STATUS_FINISHED
        )
    
class AccessRequestPerson(NetBoxModel):
    access_request= models.ForeignKey(
        AccessRequest,
        on_delete=models.CASCADE,
        related_name='persons',
        verbose_name=_('Access request')
    )
    identity_code = models.CharField(
        max_length=12,
        verbose_name=_('Identity code'),
        help_text=_('Unique 12-digit identifier within the request'),
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message=_('Identity code must contain exactly 12 digits.')
            )
        ]
    )

    full_name = models.CharField(
        max_length=50,
        verbose_name=_('Full name')
    )
    
    status= models.CharField(
        max_length=50,
        choices=AccessRequestPersonStatusChoices,
        default=AccessRequestPersonStatusChoices.STATUS_PENDING,   
        verbose_name=_("Status")
    )
    
    entry_status= models.CharField(
        max_length=20,
        choices= AccessRequestPersonEntryStatusChoice,
        default=AccessRequestPersonEntryStatusChoice.STATUS_PENDING,
        verbose_name=_('Entry Status')
    )

    organization = models.CharField(
        max_length=100,
        verbose_name=_('Organization')
    )

    job_title = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Job title')
    )

    phone_number = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('Phone number'),
        validators=[
            RegexValidator(
                regex=r'^0\d{9}$',
                message=_('Enter a valid Vietnamese phone number (10 digits, starting with 0).')
            )
        ]
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='access_request_members',
        blank=True,
        null=True,
        verbose_name=_('Location'),
        help_text=_('Location must belong to the selected site of the access request.')
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Description')
    )
    
    attachments = GenericRelation(
        UploadedFile,
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='member'
    )

    class Meta:
        ordering = ('last_updated',)
        verbose_name = _('Access Request Member')
        verbose_name_plural = _('Access Request Members')
        constraints = [
            models.UniqueConstraint(
                fields=['access_request', 'identity_code'],
                name='unique_access_request_identity_code'
            )
        ]

    def __str__(self):
        return f'{self.full_name} ({self.identity_code})'

    def get_absolute_url(self):
        return reverse(
            'plugins:access_request_management:accessrequestperson', args=[self.pk]
        )
    
    def get_status_color(self):
        status_colors= {
            AccessRequestPersonStatusChoices.STATUS_PENDING: 'secondary',
            AccessRequestPersonStatusChoices.STATUS_VERIFY: 'success',
            AccessRequestPersonStatusChoices.STATUS_UNVERIFY: 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_entry_status_color(self):
        entry_status_colors= {
            AccessRequestPersonEntryStatusChoice.STATUS_PENDING: 'secondary',
            AccessRequestPersonEntryStatusChoice.STATUS_IN: 'success',
            AccessRequestPersonEntryStatusChoice.STATUS_OUT: 'orange'
        }
        return entry_status_colors.get(self.entry_status, 'secondary')
    
    def get_status_display(self):
        return dict(
            (c[0], c[1]) for c in AccessRequestPersonStatusChoices.CHOICES
        ).get(self.status, self.status)
    
    
    @property
    def is_editable(self):
        return self.status != AccessRequestPersonStatusChoices.STATUS_VERIFY and self.access_request.is_editable
    
    @property
    def is_deletable(self):
        return self.status !=AccessRequestPersonStatusChoices.STATUS_VERIFY and self.access_request.is_deletable

    def clean(self):

        super().clean()

        if not self.access_request_id:
            return

        if not self.location_id:
            return

        access_request_site_id = self.access_request.site_id
        if (
        access_request_site_id
        and self.location.site_id != access_request_site_id
        ):
            from django.core.exceptions import ValidationError

            raise ValidationError({
            "location": _(
                "The selected location must belong to the site of the access request."
            )
        })
    
class AccessRequestHistory(models.Model):
    access_request = models.ForeignKey(
        to=AccessRequest,
        on_delete=models.CASCADE,
        related_name='histories',
        verbose_name=_('Access request')
    )
    perform_by= models.ForeignKey(
        to=settings.AUTH_USER_MODEL, 
        on_delete= models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_request_histories',
        verbose_name=_('Performed by')
    )
    action= models.CharField(
        max_length=50,
        choices= AccessRequestHistoryActionChoices,
        verbose_name=_('Action')
        
    )
    status= models.CharField(
        max_length= 50,
        choices= AccessRequestHistoryStatusChoices,
        default=AccessRequestHistoryStatusChoices.DEFAULT,
        verbose_name=_('Status')
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Description')
    )
    created_at= models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Access Request History')
        verbose_name_plural = _('Access Request Histories')

    def __str__(self):
        return f'{self.access_request} - {self.action}'
    
    def get_action_display(self):
        return dict(
            (c[0], c[1]) for c in AccessRequestHistoryActionChoices.CHOICES
        ).get(self.action, self.action)

    def get_action_color(self):
        return dict(
            (c[0], c[2]) for c in AccessRequestHistoryActionChoices.CHOICES
        ).get(self.action, 'secondary')

    def get_status_display(self):
        return dict(
            (c[0], c[1]) for c in AccessRequestHistoryStatusChoices.CHOICES
        ).get(self.status, self.status)

    def get_status_color(self):
        return dict(
            (c[0], c[2]) for c in AccessRequestHistoryStatusChoices.CHOICES
        ).get(self.status, 'secondary')