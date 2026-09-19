from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render
from django.http import HttpResponse

from .forms import ContactForm
from .models import ContactMessage
from catalog.models import Category, Product


def home(request):
    base = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
    )
    products = list(base[:8])
    latest_products = base.exclude(pk__in=[p.pk for p in products])[:8]
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


SUPPLIES_PAGES = {
    "school": {
        "title": "School Supplies",
        "kicker": "For Schools, Colleges & Universities",
        "lead": "Everything your students and staff need — from backpacks and exercise books to art, craft and classroom equipment. Bulk orders welcome with dedicated school pricing and delivery straight to your campus.",
        "hero_items": ["School Bags", "Exercise Books", "Art & Craft", "Classroom Gear"],
        "tiles": [
            {"name": "School Bags & Backpacks", "icon": "bi-backpack", "terms": "backpack bag", "desc": "Durable bags for every level, from primary to campus."},
            {"name": "Exercise Books & Notebooks", "icon": "bi-journal-text", "terms": "notebook exercise book", "desc": "Quarters, foolscaps, hardcover and spiral notebooks."},
            {"name": "Stationery Sets", "icon": "bi-pencil", "terms": "stationery pencil pen ruler", "desc": "Pens, pencils, erasers, sharpeners and complete sets."},
            {"name": "Art & Craft Supplies", "icon": "bi-palette", "terms": "paint crayon craft clay", "desc": "Paints, brushes, crayons, modelling clay and boards."},
            {"name": "Maths & Geometry Sets", "icon": "bi-rulers", "terms": "geometry compass calculator", "desc": "Compasses, protractors, set squares and calculators."},
            {"name": "Whiteboards & Classroom Gear", "icon": "bi-easel", "terms": "whiteboard marker display", "desc": "Boards, markers, displays and teaching accessories."},
        ],
        "cta_title": "Equipping a whole school?",
        "cta_text": "Send us your supply list and we'll quote bundle pricing with free Nairobi delivery on bulk orders.",
        "search_terms": ["school", "backpack", "stationery", "pencil", "notebook", "exercise book", "geometry", "crayon", "paint", "whiteboard", "calculator", "marker"],
    },
    "office": {
        "title": "Office Supplies",
        "kicker": "For Offices, Institutions & Home Desks",
        "lead": "Keep your workplace stocked — filing, paper and toner, desk accessories and the practical equipment that keeps offices running. Set up a standing order or request an institutional quote.",
        "hero_items": ["Paper & Toner", "Filing", "Desk Accessories", "Equipment"],
        "tiles": [
            {"name": "Paper & Toner", "icon": "bi-printer", "terms": "paper toner cartridge", "desc": "Bond paper, cartridges and ribbons for every printer."},
            {"name": "Filing & Organizers", "icon": "bi-folder2-open", "terms": "folder file binder archive", "desc": "Box files, lever arch files, folders and archive boxes."},
            {"name": "Desk Accessories", "icon": "bi-cup-straw", "terms": "desk stapler organiser punch", "desc": "Staplers, punches, trays, pen holders and desk pads."},
            {"name": "Binding & Laminating", "icon": "bi-scissors", "terms": "binding laminator comb", "desc": "Binding machines, combs, covers and laminator pouches."},
            {"name": "Power & Extensions", "icon": "bi-plug", "terms": "extension socket adapter", "desc": "Extensions, surge protection and cable management."},
            {"name": "Office Equipment", "icon": "bi-buildings", "terms": "office shredder projector", "desc": "Shredders, projectors and everyday office hardware."},
        ],
        "cta_title": "Stocking a whole office?",
        "cta_text": "Share your requisition list for institutional pricing, monthly standing orders and count-down delivery.",
        "search_terms": ["office", "paper", "toner", "cartridge", "folder", "binder", "stapler", "shredder", "binding", "laminat", "extension", "desk"],
    },
}


def supplies(request, kind):
    cfg = SUPPLIES_PAGES[kind]
    clauses = Q()
    for term in cfg["search_terms"]:
        clauses |= Q(name__icontains=term)
    products = (
        Product.objects.filter(clauses, is_active=True)
        .select_related("category", "brand")
        .order_by("name")[:12]
    )
    return render(request, "core/supplies.html", {
        "page": cfg,
        "products": products,
        "wa_link": "https://wa.me/254736794594",
    })


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    return HttpResponse(
        f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /accounts/\nDisallow: /cart/\nSitemap: {sitemap_url}\n",
        content_type="text/plain",
    )


def sitemap_xml(request):
    urls = ["/", "/about/", "/services/", "/school-supplies/", "/office-supplies/", "/contact/", "/products/"]
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
