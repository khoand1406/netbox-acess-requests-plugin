"""
Test cases for access_request_management GraphQL API.
"""
from ..models import Access_Request
from ..testing import PluginGraphQLTestCase


class Access_RequestGraphQLTestCase(PluginGraphQLTestCase):
    """Test Access_Request GraphQL queries."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        Access_Request.objects.create(name='GraphQL Test 1')
        Access_Request.objects.create(name='GraphQL Test 2')
        Access_Request.objects.create(name='GraphQL Test 3')

    def test_query_accessrequest(self):
        """Test GraphQL query for a single Access_Request."""
        self.add_permissions('access_request_management.view_accessrequest')

        instance = Access_Request.objects.first()

        query = (
            "query { "
            "accessrequest(id: " + str(instance.pk) + ") { "
            "id name "
            "} "
            "}"
        )

        response = self.execute_query(query)
        self.assertIsNone(response.get('errors'))

        data = response['data']['accessrequest']
        self.assertEqual(data['id'], str(instance.pk))
        self.assertEqual(data['name'], instance.name)

    def test_query_accessrequest_list(self):
        """Test GraphQL query for list of Access_Requests."""
        self.add_permissions('access_request_management.view_accessrequest')

        query = """
        query {
            accessrequest_list {
                id
                name
            }
        }
        """

        response = self.execute_query(query)
        self.assertIsNone(response.get('errors'))

        data = response['data']['accessrequest_list']
        self.assertEqual(len(data), 3)
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])

    def test_query_accessrequest_with_all_fields(self):
        """Test GraphQL query with all available fields."""
        self.add_permissions('access_request_management.view_accessrequest')

        instance = Access_Request.objects.first()

        query = (
            "query { "
            "accessrequest(id: " + str(instance.pk) + ") { "
            "id name created last_updated "
            "} "
            "}"
        )

        response = self.execute_query(query)
        self.assertIsNone(response.get('errors'))

        data = response['data']['accessrequest']
        self.assertEqual(data['id'], str(instance.pk))
        self.assertEqual(data['name'], instance.name)
        self.assertIsNotNone(data['created'])
        self.assertIsNotNone(data['last_updated'])

