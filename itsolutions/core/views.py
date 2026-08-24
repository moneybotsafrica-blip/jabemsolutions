from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render

from catalog.models import Product
from .forms import ContactForm
from .models import ContactMessage


def home(request):
    # Get specific featured products for the homepage
    featured_products = Product.objects.filter(
        slug__in=[
            'pos-software-premium',
            'thermal-receipt-printer',
            'pos-terminal-pro',
            'iphone-17-pro-256gb',
            'ipad-pro-13-m4-8gb-512gb-ipados-18-13',
            'cisco-catalyst-ws-c3750-48ps-s-48-port-poe-managed-switch',
            'mustek-cash-drawer-m4052',
            'epos-cash-drawer',
            'posiflex-cr-4000-cash-drawer',
            'posiflex-cr-3100-cash-drawer',
            'barcode-scanner-2d',
            'customer-display-pole',
            'pos-keyboard-programmable',
            'pos-stand-touchscreen'
        ],
        is_active=True
    )
    
    # Get additional POS products for the product grid
    featured_pos_products = Product.objects.filter(
        slug__in=[
            'mustek-cash-drawer-m4052',
            'posiflex-cr-4000-cash-drawer',
            'epos-cash-drawer',
            'posiflex-cr-3100-cash-drawer',
            'barcode-scanner-2d',
            'customer-display-pole',
            'pos-keyboard-programmable',
            'pos-stand-touchscreen'
        ],
        is_active=True
    )
    
    # Get more products for extended listing
    latest_products = Product.objects.filter(is_active=True).exclude(
        slug__in=[
            'pos-software-premium',
            'thermal-receipt-printer',
            'pos-terminal-pro',
            'iphone-17-pro-256gb',
            'ipad-pro-13-m4-8gb-512gb-ipados-18-13',
            'cisco-catalyst-ws-c3750-48ps-s-48-port-poe-managed-switch',
            'mustek-cash-drawer-m4052',
            'epos-cash-drawer',
            'posiflex-cr-4000-cash-drawer',
            'posiflex-cr-3100-cash-drawer',
            'barcode-scanner-2d',
            'customer-display-pole',
            'pos-keyboard-programmable',
            'pos-stand-touchscreen'
        ]
    )[:20]
    
    return render(request, "core/home.html", {
        "featured_products": featured_products,
        "featured_pos_products": featured_pos_products,
        "latest_products": latest_products
    })


def about(request):
    return render(request, "core/about.html")


def services(request):
    return render(request, "core/services.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Save message to database
            ContactMessage.objects.create(
                name=data['name'],
                email=data['email'],
                phone=data.get('phone', ''),
                subject=data['subject'],
                message=data['message']
            )
            
            # Also send email notification
            send_mail(
                subject=f"[Website Contact] {data['subject']}",
                message=(
                    f"From: {data['name']} <{data['email']}>\n"
                    f"Phone: {data.get('phone', '-')}\n\n"
                    f"{data['message']}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.COMPANY_EMAIL],
                fail_silently=True,
            )
            messages.success(request, "Thanks for reaching out — we'll get back to you shortly.")
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})
