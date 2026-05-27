"""
GraphQL schema for access_request_management.

For more information on NetBox GraphQL, see:
https://docs.netbox.dev/en/stable/plugins/development/graphql/

For Strawberry GraphQL documentation, see:
https://strawberry.rocks/
"""

from typing import List

import strawberry
import strawberry_django

from .models import AccessRequest


@strawberry_django.type(
    AccessRequest,
    fields='__all__',
)
class Access_RequestType:
    """GraphQL type for Access_Request model."""
    pass


@strawberry.type(name="Query")
class Access_RequestQuery:
    """GraphQL queries for access_request_management."""

    accessrequest: Access_RequestType = strawberry_django.field()
    accessrequest_list: List[Access_RequestType] = strawberry_django.field()


schema = [
    Access_RequestQuery,
]

