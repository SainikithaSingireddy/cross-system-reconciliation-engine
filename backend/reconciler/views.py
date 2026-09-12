from decimal import Decimal, InvalidOperation

from rest_framework.response import Response
from rest_framework.views import APIView

from .services.comparator import find_discrepancies


def numeric_sort_key(value):
    """
    Convert a discrepancy value into a numeric value for sorting.

    None values are kept separate so they can remain at the end
    for both ascending and descending sorting.
    """
    if value is None:
        return None

    try:
        first_value = str(value).split(",")[0].strip()
        return Decimal(first_value)
    except (InvalidOperation, ValueError):
        return None


def sort_results(results, field, descending=False):
    """
    Sort numeric values while keeping missing values at the end.
    """
    values = [item for item in results if numeric_sort_key(item[field]) is not None]
    missing = [item for item in results if numeric_sort_key(item[field]) is None]

    values.sort(
        key=lambda item: numeric_sort_key(item[field]),
        reverse=descending,
    )

    return values + missing


class DiscrepancyListView(APIView):
    def get(self, request):
        org_id = request.query_params.get("org_id")

        if not org_id:
            return Response(
                {"error": "org_id is required"},
                status=400,
            )

        reason = request.query_params.get("reason")
        ordering = request.query_params.get("ordering")

        results = find_discrepancies(org_id=org_id)

        if reason:
            results = [
                item
                for item in results
                if item["reason"] == reason
            ]

        if ordering == "system_a":
            results = sort_results(results, "system_a")

        elif ordering == "-system_a":
            results = sort_results(
                results,
                "system_a",
                descending=True,
            )

        elif ordering == "system_b":
            results = sort_results(results, "system_b")

        elif ordering == "-system_b":
            results = sort_results(
                results,
                "system_b",
                descending=True,
            )

        return Response(
            {
                "org_id": org_id,
                "count": len(results),
                "results": results,
            }
        )