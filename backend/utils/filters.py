from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter

from apps.events.models import Events


class EventFilter(FilterSet):
    """Filter for Event queryset"""

    dtstart = DateFilter(field_name="dtstart", lookup_expr="gte")
    dtend = DateFilter(field_name="dtstart", lookup_expr="lte")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    club_type = CharFilter(field_name="club_type")
    school = CharFilter(field_name="school", lookup_expr="icontains")

    class Meta:
        model = Events
        fields = [
            "dtstart",
            "dtend",
            "min_price",
            "max_price",
            "club_type",
            "school",
        ]
