"""
Test cases for access_request_management views.
"""

from django.urls import reverse

from ..models import Access_Request
from ..testing import PluginViewTestCase
from ..testing.utils import disable_warnings, get_random_string


class Access_RequestViewTestCase(PluginViewTestCase):
    """Test Access_Request views."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        Access_Request.objects.create(name='View Test 1')
        Access_Request.objects.create(name='View Test 2')
        Access_Request.objects.create(name='View Test 3')

    def setUp(self):
        """Set up each test."""
        super().setUp()
        self.base_url = 'plugins:access_request_management:accessrequest'

    def test_list_accessrequests(self):
        """Test Access_Request list view."""
        self.add_permissions('access_request_management.view_accessrequest')

        url = reverse('plugins:access_request_management:accessrequest_list')
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)

    def test_list_accessrequests_without_permission(self):
        """Test Access_Request list view without permission."""
        url = reverse('plugins:access_request_management:accessrequest_list')

        with disable_warnings('django.request'):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_view_accessrequest(self):
        """Test Access_Request detail view."""
        self.add_permissions('access_request_management.view_accessrequest')

        instance = Access_Request.objects.first()
        url = reverse('plugins:access_request_management:accessrequest', kwargs={'pk': instance.pk})
        response = self.client.get(url)

        self.assertHttpStatus(response, 200)
        self.assertEqual(response.context['object'], instance)

    def test_create_accessrequest(self):
        """Test creating a Access_Request via form."""
        self.add_permissions(
            'access_request_management.add_accessrequest',
            'access_request_management.view_accessrequest'
        )

        url = reverse('plugins:access_request_management:accessrequest_add')
        name = f'Created {get_random_string(10)}'

        form_data = self.post_data({
            'name': name,
        })

        response = self.client.post(url, form_data, follow=True)
        self.assertHttpStatus(response, 200)

        # Verify object was created
        instance = Access_Request.objects.get(name=name)
        self.assertEqual(instance.name, name)

    def test_create_accessrequest_without_permission(self):
        """Test creating a Access_Request without permission."""
        url = reverse('plugins:access_request_management:accessrequest_add')

        with disable_warnings('django.request'):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)

    def test_edit_accessrequest(self):
        """Test editing a Access_Request via form."""
        self.add_permissions(
            'access_request_management.change_accessrequest',
            'access_request_management.view_accessrequest'
        )

        instance = Access_Request.objects.first()
        url = reverse('plugins:access_request_management:accessrequest_edit', kwargs={'pk': instance.pk})

        new_name = f'Edited {get_random_string(10)}'
        form_data = self.post_data({
            'name': new_name,
        })

        response = self.client.post(url, form_data, follow=True)
        self.assertHttpStatus(response, 200)

        # Verify object was updated
        instance.refresh_from_db()
        self.assertEqual(instance.name, new_name)

    def test_delete_accessrequest(self):
        """Test deleting a Access_Request."""
        self.add_permissions(
            'access_request_management.delete_accessrequest',
            'access_request_management.view_accessrequest'
        )

        instance = Access_Request.objects.first()
        url = reverse('plugins:access_request_management:accessrequest_delete', kwargs={'pk': instance.pk})

        # Confirm deletion
        response = self.client.post(url, {'confirm': True}, follow=True)
        self.assertHttpStatus(response, 200)

        # Verify object was deleted
        self.assertFalse(
            Access_Request.objects.filter(pk=instance.pk).exists()
        )

    def test_delete_accessrequest_without_permission(self):
        """Test deleting a Access_Request without permission."""
        instance = Access_Request.objects.first()
        url = reverse('plugins:access_request_management:accessrequest_delete', kwargs={'pk': instance.pk})

        with disable_warnings('django.request'):
            response = self.client.get(url)
            self.assertHttpStatus(response, 403)


class Access_RequestFormTestCase(PluginViewTestCase):
    """Test Access_Request form validation."""

    def setUp(self):
        """Set up each test."""
        super().setUp()
        self.add_permissions(
            'access_request_management.add_accessrequest',
            'access_request_management.view_accessrequest'
        )

    def test_form_validation_empty_name(self):
        """Test form validation with empty name."""
        url = reverse('plugins:access_request_management:accessrequest_add')
        form_data = self.post_data({'name': ''})

        response = self.client.post(url, form_data)
        self.assertHttpStatus(response, 200)  # Form redisplay

        # Should not create object
        self.assertEqual(Access_Request.objects.filter(name='').count(), 0)

    def test_form_validation_duplicate_name(self):
        """Test form validation with duplicate name."""
        Access_Request.objects.create(name='Duplicate')

        url = reverse('plugins:access_request_management:accessrequest_add')
        form_data = self.post_data({'name': 'Duplicate'})

        response = self.client.post(url, form_data)
        self.assertHttpStatus(response, 200)  # Form redisplay

        # Should only have one instance with this name
        self.assertEqual(Access_Request.objects.filter(name='Duplicate').count(), 1)
