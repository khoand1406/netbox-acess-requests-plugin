"""
Filtersets for access_request_management.

For more information on NetBox filtersets, see:
https://docs.netbox.dev/en/stable/plugins/development/filtersets/

For django-filters documentation, see:
https://django-filter.readthedocs.io/
"""

import django_filters

from dcim.models.sites import Region, Site
from extras.filters import TagFilter
from dcim.models.sites import Location
from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q

from utilities.filtersets import register_filterset
from .models import AccessRequest, AccessRequestPerson, AccessRequestPersonStatusChoices, AccessRequestStatusChoices

@register_filterset
class AccessRequestFilterSet(NetBoxModelFilterSet):

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    ) 
    
    region = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region',
        label='Region'
    )

    site = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='site',
        label='Site'
    )

    status = django_filters.MultipleChoiceFilter(
        choices=AccessRequestStatusChoices,
        field_name='status'
    )

    planned_date = django_filters.DateFilter(
        field_name='planned_date'
    )
    tag= TagFilter()

    class Meta:
        model = AccessRequest
        fields = (
            'q',
            'id',
            'name',
            'status',
            'planned_date',
            'region',
            'site',
            'created_by',
            'tag'
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        return queryset.filter(
            Q(name__icontains=value) |
            Q(status__icontains=value) |
            Q(reason__icontains=value)
        )

class AccessRequestPersonFilterSet(NetBoxModelFilterSet):

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    access_request_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AccessRequest.objects.all(),
        label="Access Request",
    )

    location_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        label="Location",
    )

    status = django_filters.MultipleChoiceFilter(
        choices=AccessRequestPersonStatusChoices,
        label="Status",
    )

    class Meta:

        model = AccessRequestPerson

        fields = (
            "id",
            "identity_code",
            "full_name",
            "status",
            "organization",
            "job_title",
            "phone_number",
            "access_request_id",
            "location_id",
        )

    def search(self, queryset, name, value):

        if not value.strip():
            return queryset

        return queryset.filter(
                Q(identity_code__icontains=value)
            |   Q(full_name__icontains=value)
            |   Q(organization__icontains=value)
            |   Q(phone_number__icontains=value)
        )
