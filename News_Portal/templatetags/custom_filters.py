import re
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

BAD_WORDS = ['редиска', 'какашка', 'плохой_человек']


@register.filter(name='censor')
@stringfilter
def censor(value):
    if not isinstance(value, str):
        raise ValueError(f"Фильтр 'censor' нельзя применять к объектам типа {type(value)}.")

    def replace_func(match):
        word = match.group(0)
        return word[0] + '*' * (len(word) - 1)

    for bad_word in BAD_WORDS:

        pattern = rf'\b[А-яЁё]{re.escape(bad_word[1:])}\b'

        value = re.sub(pattern, replace_func, value, flags=re.UNICODE)

    return value