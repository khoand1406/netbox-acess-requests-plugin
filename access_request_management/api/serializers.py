"""
API serializers for access_request_management.

Serializers are required for NetBox event handling (webhooks, change logging).
They also power the REST API endpoints.

For more information on NetBox REST API serializers, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#serializers

For Django REST Framework serializers, see:
https://www.django-rest-framework.org/api-guide/serializers/
"""

from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from dcim.models.sites import Location

from ..models import AccessRequest, AccessRequestPerson
from dcim.api.serializers import RegionSerializer
from dcim.api.serializers import SiteSerializer

class AccessRequestSerializer(NetBoxModelSerializer):
    
    region = RegionSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    site = SiteSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    created_by = serializers.StringRelatedField()

    member_count = serializers.IntegerField(
        source="persons.count",
        read_only=True
    )

    class Meta:
        model = AccessRequest

        fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "planned_date",
            "reason",
            "region",
            "site",
            "created_by",
            "member_count",
            "created",
            "last_updated",
            "tags",
            "custom_fields",
        )

class AccessRequestPersonSerializer(NetBoxModelSerializer):

    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        allow_null=True,
        required=False
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    status_color = serializers.CharField(
        source='get_status_color',
        read_only=True
    )

    is_editable = serializers.BooleanField(read_only=True)
    is_deletable = serializers.BooleanField(read_only=True)

    class Meta:
        model = AccessRequestPerson
        fields = [
            'id',
            'url',
            'display',
            'access_request',
            'identity_code',
            'full_name',
            'status',
            'status_display',
            'status_color',
            'organization',
            'job_title',
            'phone_number',
            'location',
            'description',
            'is_editable',
            'is_deletable',
            'created',
            'last_updated',
        ]

    def validate(self, attrs):

        instance = AccessRequestPerson(
            **{
                **getattr(self.instance, '__dict__', {}),
                **attrs
            }
        )

        access_request = self.context.get('access_request')
        if access_request:
            instance.access_request = access_request

        instance.clean()

        return attrs

