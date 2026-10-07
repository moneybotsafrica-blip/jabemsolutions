from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "core"

urlpatterns = [
    # TEMPORARY coming-soon landing page — to restore the real homepage, delete the
    # next line and uncomment the original home path below.
    path("", TemplateView.as_view(template_name="core/coming_soon.html"), name="coming_soon"),
    # path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("school-supplies/", views.supplies, {"kind": "school"}, name="school_supplies"),
    path("office-supplies/", views.supplies, {"kind": "office"}, name="office_supplies"),
    path("contact/", views.contact, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
