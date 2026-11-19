import json

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils.html import escape
from django.utils.safestring import mark_safe

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


NEWSLETTER_SUBJECT = "Newsletter subscription"


@require_POST
def newsletter_signup(request):
    """Footer newsletter form; signups land in admin under Contact messages."""
    email = request.POST.get("email", "").strip()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"message": "Please enter a valid email address."}, status=400)
    already = ContactMessage.objects.filter(subject=NEWSLETTER_SUBJECT, email__iexact=email).exists()
    if not already:
        ContactMessage.objects.create(
            name=email.split("@")[0][:200],
            email=email,
            subject=NEWSLETTER_SUBJECT,
            message="Subscribed from the website footer.",
        )
    return JsonResponse({"message": "Thanks! You're on the list for offers and new stock."})


def syrve(request):
    """Syrve restaurant POS landing page with "request a call" forms."""
    from . import syrve_content

    error, error_source, phone_value = "", "", ""
    if request.method == "POST":
        phone_value = request.POST.get("phone", "").strip()[:30]
        error_source = request.POST.get("source")
        if error_source not in ("hero", "top", "bottom"):
            error_source = "bottom"
        digits = "".join(ch for ch in phone_value if ch.isdigit())
        if len(digits) < 7:
            error = "Please enter a valid phone number."
        else:
            phone = "+254 " + phone_value.lstrip("0")
            msg = ContactMessage.objects.create(
                name="Syrve call request",
                email="",
                phone=phone[:20],
                subject="Syrve demo request",
                message=f"Call-back request from the Syrve page ({error_source} form).",
            )
            send_mail(
                subject=f"[Syrve demo] Call back {phone}",
                message=f"Please call {phone} about a Syrve demo (Syrve page, {error_source} form).",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.COMPANY_EMAIL],
                fail_silently=True,
            )
            return redirect(f"{request.path}?ref=SYR-{msg.pk:05d}#contacts")

    page_url = f"{settings.SITE_URL}/syrve/"
    east_africa = ["Kenya", "Uganda", "Tanzania", "Rwanda", "Burundi", "South Sudan"]
    structured = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "@id": f"{page_url}#service",
                "name": "Syrve restaurant POS - Official Syrve Distributor in East Africa",
                "alternateName": ["Syrve Kenya", "Syrve Africa", "Syrve East Africa"],
                "serviceType": "Restaurant POS software supply, installation and support",
                "description": (
                    "Jabem Solutions is the official Syrve distributor in East Africa, supplying, "
                    "installing and supporting Syrve restaurant POS and management software."
                ),
                "url": page_url,
                "brand": {"@type": "Brand", "name": "Syrve"},
                "provider": {"@id": f"{settings.SITE_URL}/#organization"},
                "areaServed": [{"@type": "Country", "name": c} for c in east_africa],
            },
            {
                "@type": "FAQPage",
                "@id": f"{page_url}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                    }
                    for item in syrve_content.FAQ
                ],
            },
        ],
    }

    return render(request, "core/syrve.html", {
        # "</" is escaped so FAQ text can never close the <script> tag early.
        "structured_data": mark_safe(json.dumps(structured, ensure_ascii=False).replace("</", "<\\/")),
        "why": syrve_content.WHY,
        "fits": syrve_content.FITS,
        "function_tabs": syrve_content.FUNCTION_TABS,
        "assistants": syrve_content.ASSISTANTS,
        "loyalty": syrve_content.LOYALTY,
        "back_office": syrve_content.BACK_OFFICE,
        "packages": syrve_content.PACKAGES,
        "services": syrve_content.SERVICES,
        "steps": syrve_content.STEPS,
        "faq": syrve_content.FAQ,
        "error": error,
        "error_source": error_source,
        "phone_value": phone_value,
        "reference": request.GET.get("ref", "")[:20],
    })


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


# Let Vercel's edge cache crawler files so Googlebot never waits on a cold
# serverless start; stale copies are served while a fresh one is rebuilt.
CRAWLER_CACHE_CONTROL = "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /products/cart/",
        "Disallow: /products/checkout/",
        "Disallow: /products/order/",
        "Disallow: /products/pos/",
        "Disallow: /products/quotes/",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    response = HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
    response["Cache-Control"] = CRAWLER_CACHE_CONTROL
    return response


FAVICON_PATH = settings.BASE_DIR / "static" / "images" / "favicon.ico"


def favicon_ico(request):
    # Google and browsers request /favicon.ico at the site root.
    response = HttpResponse(FAVICON_PATH.read_bytes(), content_type="image/x-icon")
    response["Cache-Control"] = "public, max-age=604800, s-maxage=604800"
    return response


SITEMAP_PAGES = [
    ("/", "daily", "1.0"),
    ("/products/", "daily", "0.9"),
    ("/services/", "weekly", "0.9"),
    ("/about/", "monthly", "0.7"),
    ("/contact/", "monthly", "0.8"),
    ("/syrve/", "weekly", "0.9"),
    ("/school-supplies/", "weekly", "0.7"),
    ("/office-supplies/", "weekly", "0.7"),
]


def sitemap_xml(request):
    entries = [
        f"<url><loc>{settings.SITE_URL}{path}</loc><changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
        for path, freq, prio in SITEMAP_PAGES
    ]
    products = Product.objects.filter(is_active=True).only("slug", "updated_at").order_by("-updated_at")
    for product in products:
        if not product.slug:
            continue
        entries.append(
            f"<url><loc>{escape(settings.SITE_URL + product.get_absolute_url())}</loc>"
            f"<lastmod>{product.updated_at.date().isoformat()}</lastmod>"
            "<changefreq>weekly</changefreq><priority>0.6</priority></url>"
        )
    response = HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(entries) + "</urlset>",
        content_type="application/xml",
    )
    response["Cache-Control"] = CRAWLER_CACHE_CONTROL
    return response


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
