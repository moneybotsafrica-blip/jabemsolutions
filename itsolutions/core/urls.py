from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "core"

urlpatterns = [
    # TEMPORARY greeting page at the site root — to restore the homepage, delete
    # the next line and change the "home/" path back to "".
    path("", TemplateView.as_view(template_name="core/greeting.html"), name="greeting"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("school-supplies/", views.supplies, {"kind": "school"}, name="school_supplies"),
    path("office-supplies/", views.supplies, {"kind": "office"}, name="office_supplies"),
    path("contact/", views.contact, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
