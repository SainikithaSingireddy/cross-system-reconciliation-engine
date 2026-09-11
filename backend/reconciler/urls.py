from django.urls import path

from .views import DiscrepancyListView


urlpatterns = [
    path(
        "discrepancies/",
        DiscrepancyListView.as_view(),
        name="discrepancies",
    ),
]