from django import template

register = template.Library()


@register.filter(name='range')
def range_filter(start, end):
    return range(start, end + 1)


@register.filter
def split(value, arg):
    return value.split(arg)


@register.filter
def stars_count(rating):
    return range(int(rating))
