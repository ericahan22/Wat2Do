from django_filters import CharFilter, DateTimeFilter, FilterSet, NumberFilter
from django.db.models import Q

from apps.events.models import Events


class EventFilter(FilterSet):
    """Filter for Event queryset"""

    dtstart_utc = DateTimeFilter(field_name="dtstart_utc", lookup_expr="gte")
    dtend_utc = DateTimeFilter(field_name="dtstart_utc", lookup_expr="lte")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    club_type = CharFilter(field_name="club_type")
    school = CharFilter(field_name="school", lookup_expr="exact")
    added_at = DateTimeFilter(field_name="added_at", lookup_expr="gte")
    categories = CharFilter(method="filter_categories")

    def filter_categories(self, queryset, name, value):
        """
        Filter events by categories. Supports semicolon-separated values for OR query.
        Checks if any of the requested categories exist in the event's categories JSONField.
        """
        if not value:
            return queryset
        
        # Parse semicolon-separated categories
        categories = [cat.strip() for cat in value.split(";") if cat.strip()]
        
        if not categories:
            return queryset
        
        # Build OR query: match any of the categories
        or_queries = Q()
        for category in categories:
            or_queries |= Q(categories__icontains=category)
        
        return queryset.filter(or_queries)

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
            "categories",
        ]
