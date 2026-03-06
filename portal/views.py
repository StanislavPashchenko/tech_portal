import json

from django.conf import settings
from django.db.models import Count, F
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone, translation
from django.views.generic import DetailView, ListView, TemplateView

from portal.models import Article, Brand, Category, ErrorCode
from portal.translations import get_text


def split_content_blocks(text):
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return blocks or [text]


def get_language_code():
    return (translation.get_language() or settings.LANGUAGE_CODE)[:2]


def build_breadcrumbs(crumbs):
    breadcrumbs = [
        {"label": get_text("home", get_language_code()), "url": reverse("portal:home")}
    ]
    breadcrumbs.extend(crumbs)
    return breadcrumbs


class SeoContextMixin:
    def seo_context(self, **kwargs):
        return {
            "page_title": kwargs.get("page_title", settings.SITE_NAME),
            "meta_description": kwargs.get(
                "meta_description", settings.DEFAULT_META_DESCRIPTION
            ),
            "canonical_url": kwargs.get(
                "canonical_url", self.request.build_absolute_uri(self.request.path)
            ),
            "og_type": kwargs.get("og_type", "website"),
            "og_image": kwargs.get("og_image"),
            "meta_robots": kwargs.get("meta_robots", "index,follow"),
            "breadcrumbs": kwargs.get("breadcrumbs", []),
        }

    def breadcrumb_schema(self, breadcrumbs):
        item_list = []
        for index, crumb in enumerate(breadcrumbs, start=1):
            item_list.append(
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": crumb["label"],
                    "item": self.request.build_absolute_uri(crumb["url"]),
                }
            )
        return json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": item_list,
            },
            ensure_ascii=False,
        )


class LocalizedTemplateMixin:
    def get_template_names(self):
        template_names = super().get_template_names()
        language = get_language_code()
        localized_templates = []
        for template_name in template_names:
            if template_name.startswith("portal/"):
                localized_templates.append(
                    f"portal/{language}/{template_name.removeprefix('portal/')}"
                )
        return localized_templates + template_names


class HomeView(LocalizedTemplateMixin, SeoContextMixin, TemplateView):
    template_name = "portal/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        article_queryset = (
            Article.objects.published()
            .select_related("category", "brand")
            .localized(language)
        )
        latest_errors = (
            ErrorCode.objects.select_related("brand", "device").localized(language)[:6]
        )
        category_sections = []
        for category in Category.objects.order_by("position", "name"):
            if category.slug == "errors":
                continue
            category_sections.append(
                {
                    "category": category,
                    "articles": article_queryset.filter(category=category)[:4],
                }
            )
        breadcrumbs = [{"label": get_text("home", language), "url": reverse("portal:home")}]
        context.update(
            {
                "hero_articles": article_queryset[:3],
                "latest_articles": article_queryset[:8],
                "category_sections": category_sections,
                "latest_errors": latest_errors,
                "top_brands": Brand.objects.annotate(article_total=Count("articles")).order_by(
                    "-article_total", "name"
                )[:8],
                "page_heading": get_text("site_name", language),
                "intro_text": get_text("home_intro", language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{settings.SITE_NAME} | {get_text('site_tagline', language)}",
                meta_description=settings.DEFAULT_META_DESCRIPTION,
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class CategoryIndexView(LocalizedTemplateMixin, SeoContextMixin, TemplateView):
    template_name = "portal/category_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("categories", language), "url": reverse("portal:category_index")}]
        )
        context.update(
            {
                "categories": Category.objects.order_by("position", "name"),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('categories', language)} | {settings.SITE_NAME}",
                meta_description=get_text("categories_description", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class CategoryArticleListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/category_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs["category_slug"])

    def get_queryset(self):
        language = get_language_code()
        return (
            Article.objects.published()
            .select_related("category", "brand")
            .filter(category=self.get_category())
            .localized(language)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        language = get_language_code()
        breadcrumbs = build_breadcrumbs(
            [{"label": category.get_label(language), "url": category.get_absolute_url()}]
        )
        context.update(
            {
                "category": category,
                "page_heading": category.get_label(language),
                "page_intro": category.get_description(language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{category.get_label(language)} | {settings.SITE_NAME}",
                meta_description=category.get_meta_description(language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorCodeListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/error_list.html"
    context_object_name = "error_codes"
    paginate_by = 12

    def get_queryset(self):
        language = get_language_code()
        return ErrorCode.objects.select_related("brand", "device").localized(language)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        category = get_object_or_404(Category, slug="errors")
        breadcrumbs = build_breadcrumbs(
            [{"label": category.get_label(language), "url": category.get_absolute_url()}]
        )
        context.update(
            {
                "category": category,
                "page_heading": category.get_label(language),
                "page_intro": category.get_description(language),
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{category.get_label(language)} | {settings.SITE_NAME}",
                meta_description=category.get_meta_description(language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ArticleDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        language = get_language_code()
        return (
            Article.objects.published()
            .select_related("category", "brand", "device")
            .filter(category__slug=self.kwargs["category_slug"])
            .localized(language)
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        article = get_object_or_404(queryset, slug=self.kwargs["slug"])
        Article.objects.filter(pk=article.pk).update(views=F("views") + 1)
        article.refresh_from_db()
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = context["article"]
        language = get_language_code()
        related_articles = (
            Article.objects.published()
            .select_related("category", "brand")
            .filter(category=article.category)
            .exclude(pk=article.pk)
            .localized(language)[:4]
        )
        breadcrumbs = build_breadcrumbs(
            [
                {
                    "label": article.category.get_label(language),
                    "url": article.category.get_absolute_url(),
                },
                {"label": article.display_title, "url": article.get_absolute_url()},
            ]
        )
        content_blocks = split_content_blocks(article.display_content)
        article_schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": article.display_title,
                "description": article.get_meta_description(language),
                "datePublished": article.created_at.isoformat(),
                "dateModified": article.updated_at.isoformat(),
                "author": {"@type": "Organization", "name": settings.SITE_NAME},
                "publisher": {"@type": "Organization", "name": settings.SITE_NAME},
                "mainEntityOfPage": self.request.build_absolute_uri(article.get_absolute_url()),
                "image": [article.image] if article.image else [],
                "articleSection": article.category.get_label(language),
            },
            ensure_ascii=False,
        )
        context.update(
            {
                "content_blocks": content_blocks,
                "midpoint_index": max(1, len(content_blocks) // 2),
                "related_articles": related_articles,
                "article_schema": article_schema,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{article.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=article.get_meta_description(language),
                og_type="article",
                og_image=article.image,
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class ErrorCodeDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/error_detail.html"
    context_object_name = "error_code"

    def get_queryset(self):
        language = get_language_code()
        return ErrorCode.objects.select_related("brand", "device").localized(language)

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        error_code = get_object_or_404(queryset, slug=self.kwargs["slug"])
        ErrorCode.objects.filter(pk=error_code.pk).update(views=F("views") + 1)
        error_code.refresh_from_db()
        return error_code

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_code = context["error_code"]
        language = get_language_code()
        error_category = get_object_or_404(Category, slug="errors")
        related_error_codes = (
            ErrorCode.objects.select_related("brand", "device")
            .filter(brand=error_code.brand)
            .exclude(pk=error_code.pk)
            .localized(language)[:6]
        )
        breadcrumbs = build_breadcrumbs(
            [
                {
                    "label": error_category.get_label(language),
                    "url": error_category.get_absolute_url(),
                },
                {
                    "label": f"{error_code.brand.display_name} {error_code.code}",
                    "url": error_code.get_absolute_url(),
                },
            ]
        )
        error_schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": error_code.display_title,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": error_code.display_solutions,
                        },
                    }
                ],
            },
            ensure_ascii=False,
        )
        context.update(
            {
                "related_error_codes": related_error_codes,
                "error_schema": error_schema,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{error_code.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=error_code.get_meta_description(language),
                og_type="article",
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class BrandListView(LocalizedTemplateMixin, SeoContextMixin, ListView):
    template_name = "portal/brand_list.html"
    context_object_name = "brands"
    queryset = Brand.objects.annotate(
        article_total=Count("articles", distinct=True),
        error_total=Count("error_codes", distinct=True),
    ).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("brands", language), "url": reverse("portal:brand_list")}]
        )
        context["breadcrumb_schema"] = self.breadcrumb_schema(breadcrumbs)
        context.update(
            self.seo_context(
                page_title=f"{get_text('brands', language)} | {settings.SITE_NAME}",
                meta_description=get_text("brands_description", language),
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class BrandDetailView(LocalizedTemplateMixin, SeoContextMixin, DetailView):
    template_name = "portal/brand_detail.html"
    context_object_name = "brand"
    queryset = Brand.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = context["brand"]
        language = get_language_code()
        brand_devices = brand.devices.all()
        breadcrumbs = build_breadcrumbs(
            [
                {"label": get_text("brands", language), "url": reverse("portal:brand_list")},
                {"label": brand.display_name, "url": brand.get_absolute_url()},
            ]
        )
        context.update(
            {
                "brand_articles": (
                    Article.objects.published()
                    .select_related("category", "brand")
                    .filter(brand=brand)
                    .localized(language)[:8]
                ),
                "brand_error_codes": (
                    ErrorCode.objects.select_related("brand", "device")
                    .filter(brand=brand)
                    .localized(language)[:8]
                ),
                "brand_devices": brand_devices[:8],
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{brand.get_seo_title(language)} | {settings.SITE_NAME}",
                meta_description=brand.get_meta_description(language) or brand.display_description[:255],
                breadcrumbs=breadcrumbs,
            )
        )
        return context


class SearchView(LocalizedTemplateMixin, SeoContextMixin, TemplateView):
    template_name = "portal/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = get_language_code()
        query = self.request.GET.get("q", "").strip()
        article_results = Article.objects.none()
        error_results = ErrorCode.objects.none()
        if query:
            article_results = (
                Article.objects.published()
                .select_related("category", "brand")
                .localized(language)
                .search(query)
            )
            error_results = (
                ErrorCode.objects.select_related("brand", "device")
                .localized(language)
                .search(query)
            )
        breadcrumbs = build_breadcrumbs(
            [{"label": get_text("search", language), "url": reverse("portal:search")}]
        )
        context.update(
            {
                "query": query,
                "article_results": article_results[:12],
                "error_results": error_results[:12],
                "results_total": article_results.count() + error_results.count() if query else 0,
                "breadcrumb_schema": self.breadcrumb_schema(breadcrumbs),
            }
        )
        context.update(
            self.seo_context(
                page_title=f"{get_text('search', language)} | {settings.SITE_NAME}",
                meta_description=get_text("search_description", language),
                meta_robots="noindex,follow",
                breadcrumbs=breadcrumbs,
            )
        )
        return context


def robots_txt(request):
    return render(
        request,
        "robots.txt",
        {
            "sitemap_url": request.build_absolute_uri(reverse("sitemap")),
            "generated_at": timezone.now(),
        },
        content_type="text/plain",
    )
