from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query_params = context['request'].GET.copy()

    for key, value in kwargs.items():
        query_params[key] = value

    return query_params.urlencode()