from django.conf import settings

from portal.forms import SearchForm
from portal.models import Article


def portal_defaults(request):
    language = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)[:2]
    popular_articles = (
        Article.objects.published()
        .select_related("category", "brand")
        .localized(language)
        .order_by("-views", "-created_at")[:5]
    )
    return {
        "global_popular_articles": popular_articles,
        "search_form": SearchForm(request.GET or None),
        "site_name": settings.SITE_NAME,
        "adsense_client": settings.GOOGLE_ADSENSE_CLIENT,
    }
