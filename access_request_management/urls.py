"""
URL patterns for access_request_management.

For more information on URL routing, see:
https://docs.netbox.dev/en/stable/plugins/development/views/#url-registration

For Django URL patterns, see:
https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (
    path("access-requests/", views.AccessRequestListView.as_view(), name="accessrequest_list"),
    path("access-requests/add/", views.AccessRequestEditView.as_view(), name="accessrequest_add"),
    path("access-requests/<int:pk>/", views.AccessRequestView.as_view(), name="accessrequest"),
    path("access-requests/<int:pk>/edit/", views.AccessRequestEditView.as_view(), name="accessrequest_edit"),
    path("access-requests/<int:pk>/delete/", views.AccessRequestDeleteView.as_view(), name="accessrequest_delete"),
    path(
        "access-requests/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="accessrequest_changelog",
        kwargs={"model": models.AccessRequest},
    ),
    path("access-requests/<int:pk>/access-members/", views.AccessRequestPersonListView.as_view(), name="accessrequest_access-members"),
    path("access-requests/<int:pk>/request-history/", views.AccessRequestHistoryListView.as_view(), name="accessrequest_request-history"),
    path("access-request-persons/", views.AccessRequestPersionListView.as_view(), name="accessrequestperson_list"),
    path("access-request-persons/add/", views.AccessRequestPersonEditView.as_view(), name="accessrequestperson_add"),
    path("access-request-persons/<int:pk>/", views.AccessRequestPersonView.as_view(), name="accessrequestperson"),
    path("access-request-persons/<int:pk>/edit/", views.AccessRequestPersonEditView.as_view(), name="accessrequestperson_edit"),
    path("access-request-person/<int:pk>/delete/", views.AccessRequestPersonDeleteView.as_view(), name="accessrequestperson_delete"),
    path("access-request-person/import/", views.AccessRequestPersionImportView.as_view(), name="accessrequestperson_import"),
    path(
        "access-requests-person/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="accessrequestperson_changelog",
        kwargs={"model": models.AccessRequestPerson},
    ),
    
)
