from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse

from .forms import ContactForm
from .models import ContactMessage
from catalog.models import Category, Product


def home(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")[:8]
    )
    latest_products = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .order_by("-created_at")[:8]
    )
    return render(
        request,
        "core/home.html",
        {
            "featured_products": products,
            "latest_products": latest_products,
        },
    )


def about(request):
    return render(request, "core/about.html")


def services(request):
    return render(request, "core/services.html")


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /accounts/\nDisallow: /cart/\nSitemap: {sitemap_url}\n",
        content_type="text/plain",
    )


def sitemap_xml(request):
    urls = ["/", "/about/", "/services/", "/contact/", "/products/"]
    body = "".join(f"<url><loc>{request.build_absolute_uri(path)}</loc><changefreq>weekly</changefreq></url>" for path in urls)
    return HttpResponse(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>',
        content_type="application/xml",
    )


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
