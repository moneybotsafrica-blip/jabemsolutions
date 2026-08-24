from django.conf import settings


def site_settings(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "COMPANY_PHONE": settings.COMPANY_PHONE,
        "COMPANY_EMAIL": settings.COMPANY_EMAIL,
        "COMPANY_ADDRESS": settings.COMPANY_ADDRESS,
    }
