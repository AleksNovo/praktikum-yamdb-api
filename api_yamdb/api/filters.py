from django_filters import FilterSet, CharFilter, NumberFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтр произведений."""

    category = CharFilter(field_name='category__slug')
    year = NumberFilter(field_name='year')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year',)
