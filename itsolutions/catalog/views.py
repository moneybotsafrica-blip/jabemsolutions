from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from decimal import Decimal
from .models import Product, Category, Cart, CartItem, Order, OrderItem, POSCategory, POSProduct


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category", "brand", "stock")
        kind = self.request.GET.get("type")
        category_slug = self.request.GET.get("category")
        q = self.request.GET.get("q")
        if kind in {"hardware", "software"}:
            qs = qs.filter(product_type=kind)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["selected_type"] = self.request.GET.get("type", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category", "brand", "stock")


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to cart")
    return redirect('catalog:product_detail', slug=product.slug)


@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'catalog/cart.html', {'cart': cart})


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    messages.success(request, "Cart updated")
    return redirect('catalog:cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('catalog:cart')


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty")
        return redirect('catalog:product_list')
    
    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                payment_method=request.POST.get('payment_method', 'whatsapp'),
                notes=request.POST.get('notes', ''),
                subtotal=cart.total_price,
                shipping_cost=Decimal('500.00'),
                total=cart.total_price + Decimal('500.00')
            )
            
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            cart.items.all().delete()
        
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('catalog:order_success', order_id=order.id)
    
    return render(request, 'catalog/checkout.html', {'cart': cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'catalog/order_success.html', {'order': order})


@login_required
def whatsapp_checkout(request):
    cart = get_or_create_cart(request.user)
    
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty")
        return redirect('catalog:product_list')
    
    # Build WhatsApp message with cart items and better formatting
    message = "🛒 *NEW ORDER*\n\n"
    message += f"👤 Customer: {request.user.username}\n"
    message += f"📧 Email: {request.user.email}\n\n"
    
    message += "*ORDER ITEMS:*\n"
    for index, item in enumerate(cart.items.all(), 1):
        message += f"{index}. {item.product.name}\n"
        message += f"   SKU: {item.product.sku}\n"
        message += f"   Qty: {item.quantity} × KES {item.product.price:.0f}\n"
        message += f"   Subtotal: KES {item.total_price:.0f}\n\n"
    
    total_with_shipping = cart.total_price + 500
    message += "*ORDER SUMMARY:*\n"
    message += f"📦 Subtotal: KES {cart.total_price:.0f}\n"
    message += f"🚚 Shipping: KES 500\n"
    message += f"💰 *TOTAL: KES {total_with_shipping:.0f}*\n\n"
    message += "Please provide your shipping details (name, phone, address, city) to complete the order."
    
    # URL encode the message
    from urllib.parse import quote
    encoded_message = quote(message)
    
    # WhatsApp number (replace with your business number)
    whatsapp_number = "254736794594"
    
    # Redirect to WhatsApp
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    return redirect(whatsapp_url)


class POSView(TemplateView):
    template_name = "catalog/pos.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mode = self.request.GET.get('mode', 'restaurant')
        
        modes = [
            {'key': 'restaurant', 'name': 'Restaurant', 'icon': 'bi-utensils'},
            {'key': 'club', 'name': 'Club', 'icon': 'bi-music-note'},
            {'key': 'supermarket', 'name': 'Supermarket', 'icon': 'bi-cart'},
            {'key': 'coffeeshop', 'name': 'Coffee Shop', 'icon': 'bi-cup-hot'},
            {'key': 'cafe', 'name': 'Cafe', 'icon': 'bi-cup-straw'},
        ]
        
        current_mode_data = next((m for m in modes if m['key'] == mode), modes[0])
        
        ctx['current_mode'] = mode
        ctx['current_mode_name'] = current_mode_data['name']
        ctx['current_mode_icon'] = current_mode_data['icon']
        ctx['modes'] = modes
        ctx['categories'] = POSCategory.objects.filter(mode=mode, is_active=True).order_by('order')
        ctx['products'] = POSProduct.objects.filter(category__mode=mode, is_active=True).select_related('category').order_by('order')
        return ctx
