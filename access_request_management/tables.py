"""
Tables for access_request_management.

For more information on NetBox tables, see:
https://docs.netbox.dev/en/stable/plugins/development/tables/

For django-tables2 documentation, see:
https://django-tables2.readthedocs.io/
"""

import django_tables2 as tables
from django.utils.translation import gettext_lazy as _ 
from netbox.tables import NetBoxTable, columns

from .models import AccessRequest, AccessRequestPerson


class AccessRequestTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
        verbose_name=_("Name")
    )
    
    status= columns.ChoiceFieldColumn(
        verbose_name= _("Status")
    )
    region = tables.Column(
        linkify=True,
        verbose_name=_("Region")
    )

    site = tables.Column(
        linkify=True,
        verbose_name=_("Site")
    )
    created = columns.DateTimeColumn(
    verbose_name=_("Created"),
    )
    
    created_by = tables.Column(
        verbose_name=_('Created By')
    )

    last_updated = tables.DateTimeColumn(
    verbose_name=_("Last Updated"),
    format="Y-m-d H:i:s"
    )

    class Meta(NetBoxTable.Meta):
        model = AccessRequest
        fields = (
            'pk',
            'id',
            'name',
            'status',
            'reason',
            'planned_date',
            'region',
            'site',
            'created_by',
            'created',
            'last_updated',
            'actions',
        )

        default_columns = (
            'name',
            'status',
            'reason',
            'planned_date',
            'region',
            'site',
            'created_by',
            'created',
            'last_updated',
            'actions',
        )
        
class AccessRequestPersonTable(NetBoxTable):
    

    full_name = tables.Column(
        verbose_name=_("Full Name"),
        linkify=True
    )

    status= columns.ChoiceFieldColumn(
        verbose_name= _("Status")
    )

    location = tables.Column(
        verbose_name=_("Location"),
        linkify=True
    )

    class Meta(NetBoxTable.Meta):

        model = AccessRequestPerson
        
        

        fields = (
            "pk",
            "id",
            "identity_code",
            "full_name",
            "status",
            "organization",
            "job_title",
            "phone_number",
            "location",
            "description",
            "created",
            "last_updated",
            "actions",
        )

        default_columns = (
            "identity_code",
            "full_name",
            "status",
            "organization",
            "phone_number",
            "location",
            "last_updated",
            "actions",
        )
    
    