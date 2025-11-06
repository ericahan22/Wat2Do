"""
Security tests for event submission endpoints.
Tests various attack vectors that were previously vulnerable.
"""
import pytest
from django.test import TestCase
from utils.validation import (
    validate_and_sanitize_event_data,
    validate_required_fields,
    sanitize_text,
    sanitize_social_handle,
    USER_EDITABLE_FIELDS,
    ADMIN_EDITABLE_FIELDS,
    PROTECTED_FIELDS,
)


class TestInputSanitization(TestCase):
    """Test input sanitization functions"""
    
    def test_sanitize_text_removes_html(self):
        """Test that HTML tags are stripped from text"""
        malicious_input = '<script>alert("XSS")</script>Hello'
        result = sanitize_text(malicious_input)
        self.assertEqual(result, 'alert("XSS")Hello')
        self.assertNotIn('<script>', result)
    
    def test_sanitize_text_removes_img_tags(self):
        """Test that img tags with onerror are removed"""
        malicious_input = '<img src=x onerror=alert(1)>Test'
        result = sanitize_text(malicious_input)
        self.assertNotIn('<img', result)
        self.assertNotIn('onerror', result)
    
    def test_sanitize_text_enforces_max_length(self):
        """Test that text is truncated to max length"""
        long_text = "A" * 1000
        result = sanitize_text(long_text, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_sanitize_social_handle_removes_at_symbol(self):
        """Test that @ symbol is removed from handles"""
        result = sanitize_social_handle("@username")
        self.assertEqual(result, "username")
    
    def test_sanitize_social_handle_removes_html(self):
        """Test that HTML is stripped from handles"""
        malicious_input = '<script>alert(1)</script>username'
        result = sanitize_social_handle(malicious_input)
        self.assertNotIn('<script>', result)
        self.assertIn('username', result)


class TestFieldWhitelisting(TestCase):
    """Test field whitelisting in validation"""
    
    def test_protected_fields_are_filtered(self):
        """Test that protected fields are filtered out"""
        malicious_data = {
            'title': 'Test Event',
            'dtstart': '2024-01-01',
            'id': 99999,  # Protected field
            'added_at': '2020-01-01',  # Protected field
            'dtstamp': '2020-01-01',  # Protected field
        }
        
        result = validate_and_sanitize_event_data(malicious_data, is_admin=False)
        
        # Should include safe fields
        self.assertIn('title', result)
        self.assertIn('dtstart', result)
        
        # Should NOT include protected fields
        self.assertNotIn('id', result)
        self.assertNotIn('added_at', result)
        self.assertNotIn('dtstamp', result)
    
    def test_user_cannot_set_status(self):
        """Test that regular users cannot set status field"""
        malicious_data = {
            'title': 'Test Event',
            'dtstart': '2024-01-01',
            'status': 'CONFIRMED',  # Should be filtered for non-admins
        }
        
        result = validate_and_sanitize_event_data(malicious_data, is_admin=False)
        
        # Status should NOT be in result for non-admin
        self.assertNotIn('status', result)
    
    def test_admin_can_set_status(self):
        """Test that admins can set status field"""
        admin_data = {
            'title': 'Test Event',
            'dtstart': '2024-01-01',
            'status': 'CONFIRMED',
        }
        
        result = validate_and_sanitize_event_data(admin_data, is_admin=True)
        
        # Status SHOULD be in result for admin
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'CONFIRMED')
    
    def test_only_user_editable_fields_allowed(self):
        """Test that only whitelisted fields are allowed"""
        data_with_random_fields = {
            'title': 'Test Event',
            'dtstart': '2024-01-01',
            'malicious_field': 'malicious_value',
            'another_bad_field': 'bad_value',
        }
        
        result = validate_and_sanitize_event_data(data_with_random_fields, is_admin=False)
        
        # Only valid fields should be present
        self.assertIn('title', result)
        self.assertIn('dtstart', result)
        self.assertNotIn('malicious_field', result)
        self.assertNotIn('another_bad_field', result)


class TestRequiredFieldValidation(TestCase):
    """Test required field validation"""
    
    def test_missing_title_raises_error(self):
        """Test that missing title raises ValueError"""
        invalid_data = {
            'dtstart': '2024-01-01',
            # Missing title
        }
        
        with self.assertRaises(ValueError) as context:
            validate_required_fields(invalid_data)
        
        self.assertIn('Title is required', str(context.exception))
    
    def test_missing_dtstart_raises_error(self):
        """Test that missing dtstart raises ValueError"""
        invalid_data = {
            'title': 'Test Event',
            # Missing dtstart
        }
        
        with self.assertRaises(ValueError) as context:
            validate_required_fields(invalid_data)
        
        self.assertIn('Start date/time is required', str(context.exception))
    
    def test_short_title_raises_error(self):
        """Test that title must be at least 3 characters"""
        invalid_data = {
            'title': 'AB',  # Too short
            'dtstart': '2024-01-01',
        }
        
        with self.assertRaises(ValueError) as context:
            validate_required_fields(invalid_data)
        
        self.assertIn('at least 3 characters', str(context.exception))
    
    def test_valid_data_passes(self):
        """Test that valid data passes validation"""
        valid_data = {
            'title': 'Valid Event Title',
            'dtstart': '2024-01-01',
        }
        
        # Should not raise any exception
        validate_required_fields(valid_data)


class TestLengthValidation(TestCase):
    """Test length validation for fields"""
    
    def test_title_max_length(self):
        """Test that title is truncated to max length"""
        long_title = "A" * 1000
        data = {
            'title': long_title,
            'dtstart': '2024-01-01',
        }
        
        result = validate_and_sanitize_event_data(data)
        
        # Title should be truncated to 500 chars
        self.assertLessEqual(len(result['title']), 500)
    
    def test_description_max_length(self):
        """Test that description is truncated to max length"""
        long_description = "A" * 10000
        data = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'description': long_description,
        }
        
        result = validate_and_sanitize_event_data(data)
        
        # Description should be truncated to 5000 chars
        self.assertLessEqual(len(result['description']), 5000)
    
    def test_social_handle_max_length(self):
        """Test that social handles are truncated"""
        long_handle = "a" * 200
        data = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'ig_handle': long_handle,
        }
        
        result = validate_and_sanitize_event_data(data)
        
        # Handle should be truncated to 100 chars
        self.assertLessEqual(len(result['ig_handle']), 100)


class TestDataTypeValidation(TestCase):
    """Test data type validation"""
    
    def test_boolean_field_validation(self):
        """Test that boolean fields are properly validated"""
        # Test with boolean
        data1 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'registration': True,
        }
        result1 = validate_and_sanitize_event_data(data1)
        self.assertTrue(result1['registration'])
        
        # Test with string "true"
        data2 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'registration': 'true',
        }
        result2 = validate_and_sanitize_event_data(data2)
        self.assertTrue(result2['registration'])
        
        # Test with string "false"
        data3 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'registration': 'false',
        }
        result3 = validate_and_sanitize_event_data(data3)
        self.assertFalse(result3['registration'])
    
    def test_price_validation(self):
        """Test that price is validated as number"""
        # Valid price
        data1 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'price': 15.99,
        }
        result1 = validate_and_sanitize_event_data(data1)
        self.assertEqual(result1['price'], 15.99)
        
        # Negative price should be rejected
        data2 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'price': -10,
        }
        result2 = validate_and_sanitize_event_data(data2)
        self.assertNotIn('price', result2)
        
        # Price too high should be rejected
        data3 = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'price': 99999,
        }
        result3 = validate_and_sanitize_event_data(data3)
        self.assertNotIn('price', result3)


class TestCategoriesValidation(TestCase):
    """Test categories field validation"""
    
    def test_categories_sanitized(self):
        """Test that categories are sanitized"""
        data = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'categories': [
                '<script>alert(1)</script>',
                'Valid Category',
                '<img src=x>',
            ]
        }
        
        result = validate_and_sanitize_event_data(data)
        
        # Categories should be present and sanitized
        self.assertIn('categories', result)
        
        # Should not contain HTML tags
        for cat in result['categories']:
            self.assertNotIn('<script>', cat)
            self.assertNotIn('<img', cat)
    
    def test_non_list_categories_ignored(self):
        """Test that non-list categories are ignored"""
        data = {
            'title': 'Test',
            'dtstart': '2024-01-01',
            'categories': 'not a list',
        }
        
        result = validate_and_sanitize_event_data(data)
        
        # Categories should not be in result if not a list
        self.assertNotIn('categories', result)


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])

