from django import template
register = template.Library()

# wzięte z https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query
@register.simple_tag
def url_replace(request, field, value):
    d = request.GET.copy()
    d[field] = value
    return d.urlencode()

@register.simple_tag
def url_delete(request, field):
    d = request.GET.copy()
    del d[field]
    return d.urlencode()


# z zajęc
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()

