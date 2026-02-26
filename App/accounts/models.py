from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from cloudinary.models import CloudinaryField
from django.urls import reverse


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an valid Eamil!')
        if not username:
            raise ValueError('This is not a valid username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            is_email_verified = False  # Explicitly set default
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    



class Account(AbstractUser):
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=155, unique=True)
    phone_number = models.CharField(max_length=25)


    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Require email verification
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)  # Email verification status


    objects = MyAccountManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True



class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    profile_picture = CloudinaryField('profile_picture', blank=True, null=True)
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return self.user.first_name
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"
    
    def get_profile_picture_url(self):
        """Returns profile picture URL or default image"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/media/default/images.png'
    


class Vendor(models.Model):
    """Vendor model for managing business sellers"""
    
    VENDOR_STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    BUSINESS_CATEGORY_CHOICES = (
        ('ELECTRONICS', 'Electronics'),
        ('CLOTHING', 'Clothing & Fashion'),
        ('FOOD', 'Food & Beverages'),
        ('HOME', 'Home & Garden'),
        ('SPORTS', 'Sports & Outdoors'),
        ('BOOKS', 'Books & Media'),
        ('TOYS', 'Toys & Games'),
        ('HEALTH', 'Health & Beauty'),
        ('AUTOMOTIVE', 'Automotive'),
        ('OTHER', 'Other'),
    )
    
    # Link to user account
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='vendor')
    
    # Business Information
    business_name = models.CharField(max_length=200, help_text="Business/Store name")
    business_category = models.CharField(max_length=20, choices=BUSINESS_CATEGORY_CHOICES)
    business_description = models.TextField(blank=True, help_text="Describe your business")
    
    # Contact Information
    business_phone = models.CharField(max_length=25, help_text="Business contact number")
    business_email = models.EmailField(max_length=155, help_text="Business email address")
    
    # Location Information
    store_location = models.CharField(max_length=500, blank=True, help_text="Physical store location (optional)")
    store_city = models.CharField(max_length=50, blank=True)
    store_state = models.CharField(max_length=50, blank=True)
    
    # NID Card Verification
    nid_card_front = CloudinaryField('nid_card_front', help_text="Front side of NID card")
    nid_card_back = CloudinaryField('nid_card_back', help_text="Back side of NID card")
    
    # Status and Timestamps
    status = models.CharField(max_length=10, choices=VENDOR_STATUS_CHOICES, default='PENDING')
    is_active = models.BooleanField(default=False)  # Only active vendors can post products
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, help_text="Admin notes about approval/rejection")
    
    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"
    
    def get_full_name(self):
        """Get vendor full name from user account"""
        return self.user.full_name()
    
    def get_email(self):
        """Get vendor email from user account"""
        return self.user.email
    
    def approve(self, admin_notes=""):
        """Approve vendor account"""
        from django.utils import timezone
        self.status = 'APPROVED'
        self.is_active = True
        self.approved_at = timezone.now()
        self.admin_notes = admin_notes
        self.save()
    
    def reject(self, admin_notes=""):
        """Reject vendor account"""
        from django.utils import timezone
        self.status = 'REJECTED'
        self.is_active = False
        self.rejected_at = timezone.now()
        self.admin_notes = admin_notes
        self.save()
    
    def can_post_products(self):
        """Check if vendor can post products"""
        return self.is_active and self.status == 'APPROVED'
    
    def get_absolute_url(self):
        """Get vendor detail URL"""
        return reverse('vendor_detail', args=[self.id])
    


