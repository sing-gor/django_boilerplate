from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@wongyusing.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """docstring for ModelTests."""

    def test_create_user_with_email_successful(self):
        """test creating a new user with an email if successful """
        email = 'test@wongyusing.com'
        password = 'wongyusing'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_email_normailzed(self):
        """Test the email for a new is normailzed"""

        email = 'test@WONGYUSING.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='wongyusing'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_mail(self):
        """Test creating user with no email rails error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                password='wongyusing'
            )

    def test_create_super_user(self):
        """Test creating an super user"""
        user = get_user_model().objects.create_superuser(
            email="admin@wongyusing.com",
            password='wongyusing'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Sing"
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string respresentation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='YuSing'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_to_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='test title',
            time_minutes=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self,mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'myimage.jpg')
        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path,exp_path)
