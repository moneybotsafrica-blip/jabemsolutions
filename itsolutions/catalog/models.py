from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
import os


class Category(models.Model):
    KIND_CHOICES = [
        ("hardware", "Hardware"),
        ("software", "Software"),
        ("service", "Service"),
    ]
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default="hardware")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["kind", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_logo_url(self):
        """Return the best available logo URL for this brand."""
        if self.logo:
            # On Vercel, media files are copied to static/media/ during build
            if os.environ.get("VERCEL"):
                return f"/static/media/{self.logo.name}"
            return self.logo.url
        return None


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ("hardware", "Hardware"),
        ("software", "Software License"),
        ("bundle", "POS Bundle"),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField("SKU", max_length=60, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default="hardware")
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    external_image_url = models.URLField(max_length=500, blank=True, help_text="External image URL for products")
    is_active = models.BooleanField(default=True)
    track_inventory = models.BooleanField(
        default=True, help_text="Software licenses may not need stock tracking."
    )
    reorder_level = models.PositiveIntegerField(
        default=5, help_text="Trigger a low-stock flag at/below this quantity."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = base
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def quantity_on_hand(self):
        stock = getattr(self, "stock", None)
        return stock.quantity_on_hand if stock else 0

    @property
    def is_low_stock(self):
        return self.track_inventory and self.quantity_on_hand <= self.reorder_level

    @property
    def in_stock(self):
        return (not self.track_inventory) or self.quantity_on_hand > 0

    def get_image_url(self):
        """Return the best available image URL for this product."""
        if self.external_image_url:
            return self.external_image_url
        if self.image:
            # On Vercel, media files are copied to static/media/ during build
            if os.environ.get("VERCEL"):
                return f"/static/media/{self.image.name}"
            return self.image.url
        return None


class Stock(models.Model):
    """Current on-hand quantity per product. Kept separate from Product so
    stock changes don't churn the product's updated_at / history."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock")
    quantity_on_hand = models.IntegerField(default=0)
    warehouse_location = models.CharField(max_length=120, blank=True, default="Main Store")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stock"

    def __str__(self):
        return f"{self.product.name}: {self.quantity_on_hand} on hand"

    @transaction.atomic
    def adjust(self, delta, movement_type, reference="", created_by=None):
        """Atomically adjust stock and record the movement. delta may be
        negative (stock out) or positive (stock in / return / adjustment up)."""
        locked = Stock.objects.select_for_update().get(pk=self.pk)
        new_qty = locked.quantity_on_hand + delta
        if new_qty < 0:
            raise ValueError(
                f"Insufficient stock for {locked.product}: "
                f"{locked.quantity_on_hand} on hand, requested change {delta}"
            )
        locked.quantity_on_hand = new_qty
        locked.save(update_fields=["quantity_on_hand", "updated_at"])
        StockMovement.objects.create(
            product=locked.product,
            movement_type=movement_type,
            quantity=delta,
            resulting_quantity=new_qty,
            reference=reference,
            created_by=created_by,
        )
        self.quantity_on_hand = new_qty
        return locked


class StockMovement(models.Model):
    MOVEMENT_CHOICES = [
        ("in", "Stock In (Purchase/Restock)"),
        ("out", "Stock Out (Sale/Install)"),
        ("adjustment", "Manual Adjustment"),
        ("return", "Customer Return"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=12, choices=MOVEMENT_CHOICES)
    quantity = models.IntegerField(help_text="Signed change applied (negative for stock out).")
    resulting_quantity = models.IntegerField()
    reference = models.CharField(max_length=200, blank=True, help_text="PO number, ticket, invoice, etc.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.sku}: {self.quantity:+d} ({self.movement_type})"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('whatsapp', 'WhatsApp Order'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='whatsapp')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Shipping information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Order Items"
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def total_price(self):
        return self.price * self.quantity


# POS Demo Models
class POSCategory(models.Model):
    MODE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('club', 'Club'),
        ('supermarket', 'Supermarket'),
        ('coffeeshop', 'Coffee Shop'),
        ('cafe', 'Cafe'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., bi-box-seam)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='restaurant')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "POS Category"
        verbose_name_plural = "POS Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class POSProduct(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60, unique=True)
    category = models.ForeignKey(POSCategory, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., bi-pc-display)")
    image = models.URLField(max_length=500, blank=True, help_text="URL to product image")
    description = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "POS Product"
        verbose_name_plural = "POS Products"

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_display_image(self):
        """Return the best available image URL for POS product display."""
        if self.image:
            return self.image
        return None


class POSCustomer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "POS Customer"
        verbose_name_plural = "POS Customers"

    def __str__(self):
        return self.name


class POSSale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(POSCustomer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "POS Sale"
        verbose_name_plural = "POS Sales"

    def __str__(self):
        return f"Order #{self.order_id}"


class POSSaleItem(models.Model):
    sale = models.ForeignKey(POSSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(POSProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "POS Sale Item"
        verbose_name_plural = "POS Sale Items"

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
