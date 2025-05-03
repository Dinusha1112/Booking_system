from django import template

register = template.Library()

@register.filter
def contains(value, arg):
    return arg in value.split(',') if value else False

@register.filter
def add_genre(current, new_genre):
    if not current:
        return new_genre
    genres = current.split(',')
    if new_genre not in genres:
        genres.append(new_genre)
    return ','.join(genres)

@register.filter
def remove_genre(current, genre_to_remove):
    if not current:
        return ''
    genres = current.split(',')
    genres = [g for g in genres if g != genre_to_remove]
    return ','.join(genres)

@register.filter
def format_genres(value):
    return value.replace(',', ', ') if value else ''