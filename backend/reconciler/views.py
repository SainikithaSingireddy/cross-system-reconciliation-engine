from rest_framework.response import Response
from rest_framework.views import APIView

from .services.comparator import find_discrepancies


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
                item for item in results
                if item["reason"] == reason
            ]

        if ordering == "system_a":
            results.sort(
                key=lambda item: (
                    item["system_a"] is None,
                    item["system_a"] or "",
                )
            )

        elif ordering == "system_b":
            results.sort(
                key=lambda item: (
                    item["system_b"] is None,
                    item["system_b"] or "",
                )
            )

        return Response({
            "org_id": org_id,
            "count": len(results),
            "results": results,
        })