from django_filters import CharFilter, DateTimeFilter, FilterSet, NumberFilter

from apps.events.models import Events


class EventFilter(FilterSet):
    """Filter for Event queryset"""

    dtstart_utc = DateTimeFilter(field_name="dtstart_utc", lookup_expr="gte")
    dtend_utc = DateTimeFilter(field_name="dtstart_utc", lookup_expr="lte")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    club_type = CharFilter(field_name="club_type")
    school = CharFilter(field_name="school", lookup_expr="icontains")
    added_at = DateTimeFilter(field_name="added_at", lookup_expr="gte")

    class Meta:
        model = Events
        fields = [
            "dtstart_utc",
            "dtend_utc",
            "min_price",
            "max_price",
            "club_type",
            "school",
            "added_at",
        ]
