from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter

from .models import Events


class EventFilter(FilterSet):
    """Filter for Events queryset"""

    start_date = DateFilter(field_name="date", lookup_expr="gte")
    end_date = DateFilter(field_name="date", lookup_expr="lte")
    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    club_type = CharFilter(field_name="club_type")
    club_handle = CharFilter(field_name="club_handle", lookup_expr="icontains")

    class Meta:
        model = Events
        fields = [
            "start_date",
            "end_date",
            "min_price",
            "max_price",
            "club_type",
            "club_handle",
        ]
