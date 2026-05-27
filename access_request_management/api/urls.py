"""
API URL patterns for access_request_management.

For more information on NetBox REST API routing, see:
https://docs.netbox.dev/en/stable/plugins/development/rest-api/#routers

For Django REST Framework routers, see:
https://www.django-rest-framework.org/api-guide/routers/
"""

from netbox.api.routers import NetBoxRouter

from .views import AccessRequestPersonViewSet, AccessRequestViewSet, AccessRequestsViewSet

app_name = "access_request_management"

router = NetBoxRouter()
router.register("access-requests", AccessRequestsViewSet)
router.register("access-requests-person", AccessRequestPersonViewSet)

urlpatterns = router.urls

