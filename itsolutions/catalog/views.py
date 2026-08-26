from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.db import transaction
from decimal import Decimal
from .models import Product, Category, Cart, CartItem, Order, OrderItem, POSCategory, POSProduct, Quote, QuoteSettings


@staff_member_required
def quote_print(request, quote_id):
    quote = get_object_or_404(Quote.objects.prefetch_related("items__product"), pk=quote_id)
    return render(request, "catalog/quote_print.html", {"quote": quote, "quote_settings": QuoteSettings.get_solo()})


@staff_member_required
def quote_pdf(request, quote_id):
    """Generate the formal sales-quotation PDF used by the preview."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    quote = get_object_or_404(Quote.objects.prefetch_related("items__product"), pk=quote_id)
    company = QuoteSettings.get_solo()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{quote.quote_number}.pdf"'
    document = SimpleDocTemplate(response, pagesize=A4, leftMargin=11 * mm, rightMargin=11 * mm, topMargin=10 * mm, bottomMargin=10 * mm)
    styles = getSampleStyleSheet()
    body = ParagraphStyle("FormalBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11)
    small = ParagraphStyle("FormalSmall", parent=body, fontSize=7.5, leading=9)
    title = ParagraphStyle("FormalTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=27, leading=29, textColor=colors.HexColor("#1762A3"), alignment=2)
    label = ParagraphStyle("FormalLabel", parent=body, fontName="Helvetica-Bold")
    blue = colors.HexColor("#1762A3")
    grey = colors.HexColor("#D4D4D4")
    width = 188 * mm
    def para(value, style=body):
        return Paragraph(str(value or "").replace("\n", "<br/>"), style)

    company_text = para(f"<font color='#1762A3' size='13'><b>JABEM SOLUTIONS LIMITED</b></font><br/><b>{company.company_name.upper()}</b><br/>{company.address}<br/><b>Ph:</b> {company.phone} &nbsp; <b>Email:</b> {company.email}<br/><b>Reg / VAT:</b> {company.business_number}")
    meta_text = para(f"<b>Number:</b>&nbsp;&nbsp; {quote.quote_number}<br/><b>Date:</b>&nbsp;&nbsp; {quote.issued_date:%d %b %Y}<br/><b>Page:</b>&nbsp;&nbsp; 1<br/><b>Reference:</b>&nbsp;&nbsp; {(quote.notes or 'Quotation')[:70]}<br/><b>Valid until:</b>&nbsp;&nbsp; {quote.valid_until:%d %b %Y}")
    header = Table([[company_text, [Paragraph("QUOTATION", title), meta_text]]], colWidths=[119 * mm, 69 * mm])
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 10, colors.HexColor("#5C9ED0")), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    client_text = f"<b>{quote.client_name}</b><br/>{quote.client_company}<br/>{quote.client_phone}<br/>{quote.client_email}<br/>{quote.client_address}"
    parties = Table([[para("<b>Sold To:</b><br/>" + client_text), para("<b>Ship To:</b><br/>" + client_text), para("<b>Sales person:</b> Jabem Solutions<br/><b>Contact:</b> +254736 794 594<br/><b>Currency:</b> KES")]], colWidths=[72 * mm, 72 * mm, 44 * mm])
    parties.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOX", (0, 0), (1, 0), 1, colors.black), ("INNERGRID", (0, 0), (1, 0), 0.4, colors.black), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    rows = [["Line", "Item", "Item Description", "Quantity", "Unit", "Unit Price", "Total"], ["PRODUCTS / SERVICES", "", "", "", "", "", ""]]
    for index, item in enumerate(quote.items.all(), 1):
        rows.append([str(index), item.product.sku if item.product else "", para(item.description or item.item_name or (item.product.name if item.product else ""), small), str(item.quantity), "EA", f"{item.unit_price:,.2f}", f"{item.line_total:,.2f}"])
    if len(rows) == 2:
        rows.append(["", "", "No items have been added yet.", "", "", "", ""])
    item_table = Table(rows, colWidths=[10 * mm, 20 * mm, 65 * mm, 18 * mm, 17 * mm, 29 * mm, 29 * mm], repeatRows=1)
    item_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("BACKGROUND", (0, 0), (-1, 0), grey), ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F4F4F4")), ("SPAN", (0, 1), (-1, 1)), ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"), ("ALIGN", (0, 0), (-1, 1), "CENTER"), ("ALIGN", (0, 2), (1, -1), "CENTER"), ("ALIGN", (3, 2), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    totals = Table([["Subtotal:", f"KES {quote.subtotal:,.2f}"], ["Discount:", "KES 0.00"], ["Delivery:", "KES 0.00"], ["VAT:", f"KES {quote.tax_amount:,.2f}"], ["Total:", f"KES {quote.total:,.2f}"]], colWidths=[35 * mm, 41 * mm])
    totals.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("BACKGROUND", (0, 0), (0, -1), grey), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("ALIGN", (1, 0), (1, -1), "RIGHT"), ("PADDING", (0, 0), (-1, -1), 6)]))
    bottom = Table([[para((quote.notes or f"{quote.quote_number} - quotation prepared for {quote.client_name}"), body), totals]], colWidths=[112 * mm, 76 * mm])
    bottom.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    bank = para(f"<b>BANK DETAILS:</b><br/><b>Account Name:</b> {company.company_name}&nbsp;&nbsp;&nbsp;&nbsp; <b>Bank details:</b> {company.bank_details or 'Available on request.'}<br/><b>Payment details:</b> {company.payment_details}<br/><br/><b>Lipa Na M-Pesa:</b> Paybill No. 247247, Account Number: 309061<br/>or Paybill No. 516600, Account Number: 309061.", small)
    terms = para(f"<b>TERMS AND CONDITIONS:</b><br/>{company.terms}<br/><br/><font color='#4B5563'>Quotation created by Jabem Solutions Limited - +254736 794 594 - info@jabemsolutions.co.ke</font>", small)
    story = [header, Spacer(1, 7 * mm), parties, Spacer(1, 6 * mm), item_table, Spacer(1, 0), bottom, Spacer(1, 6 * mm), bank, Spacer(1, 5 * mm), terms]
    document.build(story)
    return response


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
        item_title = item.description or item.item_name or (item.product.name if item.product else "Manual item")
        message += f"{index}. {item_title}\n"
        if item.product:
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
