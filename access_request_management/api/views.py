"""
API viewsets for access_request_management.

For more information on NetBox REST API viewsets, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#viewsets

For Django REST Framework viewsets, see:
https://www.django-rest-framework.org/api-guide/viewsets/
"""

from rest_framework.response import Response
from rest_framework import status

from netbox.api.viewsets import NetBoxModelViewSet
from ..utils import create_access_request_history
from ..models import AccessRequest, AccessRequestPerson, AccessRequestStatusChoices, AccessRequestHistoryStatusChoices, AccessRequestHistoryActionChoices, AccessRequestPersonStatusChoices
from .serializers import AccessRequestPersonSerializer, AccessRequestSerializer
from rest_framework.decorators import action


class AccessRequestViewSet(NetBoxModelViewSet):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer

class AccessRequestsViewSet(NetBoxModelViewSet):
    queryset = AccessRequest.objects.all()
    serializer_class = AccessRequestSerializer

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        obj = self.get_object()

        if obj.status not in (AccessRequestStatusChoices.STATUS_DRAFT, AccessRequestStatusChoices.STATUS_REJECTED):
            
            return Response(
                {"detail": "Only draft/rejected requests can be submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

        if not obj.persons.exists():
            return Response(
                {"detail": "At least one member is required before submitting."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.status = AccessRequestStatusChoices.STATUS_PENDING
        obj.save()

        create_access_request_history(
            access_request=obj,
            performed_by=request.user,
            action=AccessRequestHistoryActionChoices.ACTION_SENT_REQUEST,
            status=AccessRequestHistoryStatusChoices.STATUS_SUCCESS,
            description=f"Request submitted by {request.user}",
        )

        serializer = self.get_serializer(obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk= None):
        obj= self.get_object()
        obj.status= AccessRequestStatusChoices.STATUS_CONFIRMED
        obj.save()
        create_access_request_history(
            access_request=obj,
            performed_by=request.user,
            action=AccessRequestHistoryActionChoices.ACTION_CONFIRM_REQUEST,
            status=AccessRequestHistoryStatusChoices.STATUS_SUCCESS,
            description=f"Request confirmed by {request.user}",
        )
        serializer= self.get_serializer(obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk= None):
        obj= self.get_object()
        if(obj.status != AccessRequestStatusChoices.STATUS_CONFIRMED):
            return Response({
                "success":False,
                "message":"Must confirm the request access first"
            },
            status= status.HTTP_400_BAD_REQUEST)
        members= obj.persons.all()
        invalid_members= members.filter(
        status__in=[
        AccessRequestPersonStatusChoices.STATUS_UNVERIFY,
        AccessRequestPersonStatusChoices.STATUS_PENDING,
    ]
)
        if invalid_members.exists():
            create_access_request_history(access_request=obj, 
                                        performed_by=request.user, 
                                        action=AccessRequestHistoryActionChoices.ACTION_APPROVE_REQUEST, 
                                        status=AccessRequestHistoryStatusChoices.STATUS_FAILED, 
                                        description="Members are invalid")
            return Response(
            {
                "success": False,
                "message": "Fail! There are invalid members",
                "invalid_members": [
                    {
                        "identity_code": m.identity_code,
                        "full_name": m.full_name,
                    }
                    for m in invalid_members
                ],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        check_only= request.data.get("check_only", False)
        if check_only:
            return Response({"success": True})
        obj.status = AccessRequestStatusChoices.STATUS_APPROVED
        reason= request.data.get("reason", "")
        
        obj.save()
        create_access_request_history(access_request=obj, 
                                    performed_by= request.user, 
                                    action=AccessRequestHistoryActionChoices.ACTION_APPROVE_REQUEST, 
                                    status=AccessRequestHistoryStatusChoices.STATUS_SUCCESS, 
                                    description=reason)
        return Response({"success": True})
    
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk= None):
        obj= self.get_object()
        members= obj.persons.all()
        invalid_members= members.filter(status= AccessRequestPersonStatusChoices.STATUS_PENDING)
        if invalid_members:
            create_access_request_history(
                access_request=obj, 
                performed_by= request.user, 
                action= AccessRequestHistoryActionChoices.ACTION_REJECT_REQUEST, 
                status=AccessRequestHistoryStatusChoices.STATUS_FAILED, 
                description="Invalid Members Status"
            )
            return Response({
                "success":False,
                "invalid_members":[
                    {
                        "identity_code": m.identity_code,
                        "full_name":m.full_name
                    }
                    for m in invalid_members
                ],
                "message":"Must verify or unverify member before processing"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        if(obj.status != AccessRequestStatusChoices.STATUS_CONFIRMED):
            return Response({
                "success":False,
                "message":"Must confirm the request access first"
            },
            status= status.HTTP_400_BAD_REQUEST)
        if obj.status == AccessRequestStatusChoices.STATUS_APPROVED:
            return Response({
                "success":False,
                "message":"Can't reject approved access requests",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        reason= request.data.get("reason", "")
        obj.status= AccessRequestStatusChoices.STATUS_REJECTED
        obj.save()
        create_access_request_history(
            access_request=obj, 
            performed_by= request.user, 
            action=AccessRequestHistoryActionChoices.ACTION_REJECT_REQUEST, 
            status=AccessRequestHistoryStatusChoices.STATUS_SUCCESS, 
            description=reason
            )
        return Response({
            "success": True
        })
        

class AccessRequestPersonViewSet(NetBoxModelViewSet):
    queryset= AccessRequestPerson.objects.all()
    serializer_class= AccessRequestPersonSerializer
    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk= None):
        obj= self.get_object()
        obj.status= AccessRequestPersonStatusChoices.STATUS_VERIFY
        obj.save()
        serializer= self.get_serializer(obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="unverified")
    def unverify(self, request, pk= None):
        obj= self.get_object()
        obj.status= AccessRequestPersonStatusChoices.STATUS_UNVERIFY
        obj.save()
        serializer= self.get_serializer(obj)
        return Response(serializer.data)
        
    
        
        
        