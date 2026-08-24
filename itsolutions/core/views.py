from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render

from catalog.models import Product
from .forms import ContactForm
from .models import ContactMessage


def home(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    # Get featured POS products specifically for the product grid
    featured_pos_products = Product.objects.filter(
        slug__in=[
            'cash-drawer-m4052',
            'pos-solutions-waiter-app',
            'cloud-based-pos-software',
            'pos-head-office-module',
            'pos-payment-integration'
        ]
    )
    return render(request, "core/home.html", {
        "featured_products": featured_products,
        "featured_pos_products": featured_pos_products
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
