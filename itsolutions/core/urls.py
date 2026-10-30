from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("school-supplies/", views.supplies, {"kind": "school"}, name="school_supplies"),
    path("office-supplies/", views.supplies, {"kind": "office"}, name="office_supplies"),
    path("contact/", views.contact, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
]
