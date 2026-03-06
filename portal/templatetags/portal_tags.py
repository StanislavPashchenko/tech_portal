from django import template

from portal.translations import get_text, localized_path

register = template.Library()


@register.simple_tag(takes_context=True)
def ui(context, key):
    request = context.get("request")
    language = getattr(request, "LANGUAGE_CODE", "uk")
    return get_text(key, language)


@register.simple_tag(takes_context=True)
def category_label(context, category):
    request = context.get("request")
    language = getattr(request, "LANGUAGE_CODE", "uk")
    return category.get_label(language)


@register.simple_tag(takes_context=True)
def category_description(context, category):
    request = context.get("request")
    language = getattr(request, "LANGUAGE_CODE", "uk")
    return category.get_description(language)


@register.simple_tag(takes_context=True)
def switch_lang_path(context, lang_code):
    request = context.get("request")
    if not request:
        return "/"
    return localized_path(request.get_full_path(), lang_code)
