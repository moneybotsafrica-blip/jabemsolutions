from django.db import models


class SiteStats(models.Model):
    """Model to store site-wide statistics for admin dashboard"""
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Site Statistics"
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class SiteContent(models.Model):
    """Model for managing site content like hero text, banners, etc."""
    CONTENT_TYPE_CHOICES = [
        ('hero_text', 'Hero Text'),
        ('banner', 'Banner'),
        ('announcement', 'Announcement'),
        ('testimonial', 'Testimonial'),
        ('feature', 'Feature'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='content/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Site Content"
    
    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title or 'No title'}"


class ContactMessage(models.Model):
    """Model for storing contact form submissions"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
