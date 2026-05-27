"""
Test cases for access_request_management models.
"""

from django.core.exceptions import ValidationError

from ..models import Access_Request
from ..testing import PluginModelTestCase
from ..testing.utils import create_tags, get_random_string


class Access_RequestTestCase(PluginModelTestCase):
    """Test Access_Request model."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        # Create test instances
        Access_Request.objects.create(name='Test 1')
        Access_Request.objects.create(name='Test 2')
        Access_Request.objects.create(name='Test 3')

    def test_create_accessrequest(self):
        """Test creating a Access_Request instance."""
        name = f'Test {get_random_string(10)}'
        instance = Access_Request.objects.create(name=name)

        self.assertEqual(instance.name, name)
        self.assertIsNotNone(instance.pk)

    def test_accessrequest_str(self):
        """Test Access_Request string representation."""
        instance = Access_Request.objects.first()
        self.assertEqual(str(instance), instance.name)

    def test_accessrequest_absolute_url(self):
        """Test Access_Request get_absolute_url method."""
        instance = Access_Request.objects.first()
        url = instance.get_absolute_url()

        self.assertIsNotNone(url)
        self.assertIn(str(instance.pk), url)

    def test_accessrequest_unique_name(self):
        """Test that Access_Request names must be unique."""
        name = 'Duplicate Name'
        Access_Request.objects.create(name=name)

        with self.assertRaises(ValidationError):
            instance = Access_Request(name=name)
            instance.full_clean()

    def test_model_to_dict(self):
        """Test model_to_dict helper method."""
        instance = Access_Request.objects.first()
        data = self.model_to_dict(instance)

        self.assertIn('name', data)
        self.assertEqual(data['name'], instance.name)
        self.assertIn('id', data)

    def test_instance_equal(self):
        """Test assertInstanceEqual helper method."""
        instance = Access_Request.objects.first()

        # Should pass with matching data
        self.assertInstanceEqual(
            instance,
            {'name': instance.name, 'id': instance.pk}
        )

    def test_accessrequest_with_tags(self):
        """Test Access_Request with tags."""
        tags = create_tags(['important', 'test'])
        instance = Access_Request.objects.first()

        instance.tags.add(*tags)
        instance.save()

        self.assertEqual(instance.tags.count(), 2)
        self.assertIn(tags[0], instance.tags.all())

    def test_bulk_create(self):
        """Test bulk creation of Access_Request instances."""
        initial_count = Access_Request.objects.count()

        instances = [
            Access_Request(name=f'Bulk {i}')
            for i in range(5)
        ]
        Access_Request.objects.bulk_create(instances)

        self.assertEqual(
            Access_Request.objects.count(),
            initial_count + 5
        )

    def test_query_filter(self):
        """Test filtering Access_Request instances."""
        # Create a specific instance for filtering
        test_name = f'FilterTest {get_random_string(10)}'
        Access_Request.objects.create(name=test_name)

        # Test filter
        results = Access_Request.objects.filter(name=test_name)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, test_name)

    def test_ordering(self):
        """Test Access_Request default ordering."""
        instances = list(Access_Request.objects.all())

        # Check that instances are ordered by name
        names = [instance.name for instance in instances]
        self.assertEqual(names, sorted(names))


class Access_RequestValidationTestCase(PluginModelTestCase):
    """Test Access_Request validation."""

    def test_empty_name(self):
        """Test that empty name is not allowed."""
        with self.assertRaises(ValidationError):
            instance = Access_Request(name='')
            instance.full_clean()

    def test_name_max_length(self):
        """Test name field max length."""
        long_name = 'x' * 101  # Exceeds max_length of 100

        with self.assertRaises(ValidationError):
            instance = Access_Request(name=long_name)
            instance.full_clean()
