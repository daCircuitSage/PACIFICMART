from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from product.models import Product, ReviewRating
from category.models import Category
from orders.models import OrderProduct, Order

User = get_user_model()

class ReviewTestCase(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create category and product
        self.category = Category.objects.create(
            category_name='Test Category',
            slug='test-category'
        )
        
        self.product = Product.objects.create(
            product_name='Test Product',
            slug='test-product',
            product_description='Test Description',
            product_price=100.00,
            product_category=self.category,
            stock=10
        )
        
        # Create order and order product
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD001',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='1234567890',
            address_line_1='123 Test St',
            city='Test City',
            country='Test Country',
            order_total=100.00,
            tax=10.00,
            is_ordered=True
        )
        
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            user=self.user,
            product=self.product,
            quantity=1,
            product_price=100.00,
            ordered=True
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_review_submission(self):
        """Test that review submission works and displays immediately"""
        url = reverse('submit_review', args=[self.product.id])
        product_url = reverse('product_detail', args=[self.category.slug, self.product.slug])
        
        # Submit review
        response = self.client.post(url, {
            'subject': 'Great Product',
            'review': 'This is a great product!',
            'rating': 5
        })
        
        # Should redirect back to product page
        self.assertRedirects(response, product_url)
        
        # Check review was created
        review = ReviewRating.objects.get(user=self.user, product=self.product)
        self.assertEqual(review.subject, 'Great Product')
        self.assertEqual(review.rating, 5.0)
        
        # Check product detail page shows the review
        response = self.client.get(product_url)
        self.assertContains(response, 'Great Product')
        self.assertContains(response, 'This is a great product!')
        
        # Check success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('submitted successfully', str(messages[0]))
    
    def test_review_update(self):
        """Test that review update works and displays immediately"""
        # Create initial review
        review = ReviewRating.objects.create(
            user=self.user,
            product=self.product,
            subject='Original Review',
            review='Original content',
            rating=3.0
        )
        
        url = reverse('submit_review', args=[self.product.id])
        product_url = reverse('product_detail', args=[self.category.slug, self.product.slug])
        
        # Update review
        response = self.client.post(url, {
            'subject': 'Updated Review',
            'review': 'Updated content',
            'rating': 4.0
        })
        
        # Should redirect back to product page
        self.assertRedirects(response, product_url)
        
        # Refresh review from database
        review.refresh_from_db()
        self.assertEqual(review.subject, 'Updated Review')
        self.assertEqual(review.rating, 4.0)
        
        # Check product detail page shows updated review
        response = self.client.get(product_url)
        self.assertContains(response, 'Updated Review')
        self.assertContains(response, 'Updated content')
        
        # Check success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('updated', str(messages[0]))
    
    def test_no_review_without_purchase(self):
        """Test that users cannot review products they haven't purchased"""
        # Create another user who hasn't purchased the product
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.client.login(username='otheruser', password='otherpass123')
        
        product_url = reverse('product_detail', args=[self.category.slug, self.product.slug])
        response = self.client.get(product_url)
        
        # Should not show review form
        self.assertNotContains(response, 'Submit Review')
        self.assertContains(response, 'must purchase this product to post a review')
    
    def test_review_display_ordering(self):
        """Test that reviews display in correct order (newest first)"""
        # Create multiple reviews
        old_review = ReviewRating.objects.create(
            user=self.user,
            product=self.product,
            subject='Old Review',
            review='Old content',
            rating=3.0
        )
        
        new_review = ReviewRating.objects.create(
            user=User.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='pass123'
            ),
            product=self.product,
            subject='New Review',
            review='New content',
            rating=4.0
        )
        
        product_url = reverse('product_detail', args=[self.category.slug, self.product.slug])
        response = self.client.get(product_url)
        
        # New review should appear first
        self.assertRegex(response.content.decode(), r'New Review.*Old Review')
    
    def test_cache_clearing_on_review_submit(self):
        """Test that cache is cleared when review is submitted"""
        # First visit to populate cache
        product_url = reverse('product_detail', args=[self.category.slug, self.product.slug])
        self.client.get(product_url)
        
        # Submit review
        url = reverse('submit_review', args=[self.product.id])
        self.client.post(url, {
            'subject': 'Cache Test Review',
            'review': 'Testing cache clearing',
            'rating': 5.0
        })
        
        # Second visit should show new review
        response = self.client.get(product_url)
        self.assertContains(response, 'Cache Test Review')
